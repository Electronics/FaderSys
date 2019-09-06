from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
import asyncio
import math

ip = "0.0.0.0"
port_rx = 9000
port_tx = 8000

execPage = 2
numFaders = 8
numLayers = 3

currentLayer = 0

faders = [[0.0 for x in range(numFaders)] for y in range(numLayers)] # array to store the`0-1.0 value of where the faders need to be / are

client = SimpleUDPClient(ip, port_tx)

def exec_handler(address, *args):
	#print(f"{address}: {args}")
	if not len(args) == 1:
		print("Unexpected number of arguments, got "+str(len(args))+" expected 1")
		return

	splitAddress = address.split('/')
	page = int(splitAddress[2])
	execNum = int(splitAddress[3])
	value = float(args[0])

	#try:
	if not page == 2:
		#print("Not the exec page we wanted")
		return

	x = execNum % numFaders
	y = math.floor(execNum / numFaders)

	print("Received x: "+str(x)+" y:"+str(y)+" value: "+str(value))

	if y >= numLayers:
		print("Fader is greater than the max number of layers configured")
		return

	faders[y][x] = value

	#except:
	#	print("Failed to decode OSC 'exec' packet")
	#	return


def default_handler(address, *args):
	print(f"DEFAULT {address}: {args}")


dispatcher = Dispatcher()
dispatcher.map("/exec/*", exec_handler)
dispatcher.set_default_handler(default_handler)

async def loop():
	"""Example main loop that only runs for 10 iterations before finishing"""

	# Initiate stuff after the OSC server is running
	print("Asking magicQ for exec feedback...")
	client.send_message("/feedback/exec", "") # ask for packets from magicQ about the exec page

	while True:
		#print(f"Loop {i}")
		await asyncio.sleep(1)


async def init_main():
	server = AsyncIOOSCUDPServer((ip, port_rx), dispatcher, asyncio.get_event_loop())
	transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

	await loop()  # Enter main loop of program

	transport.close()  # Clean up serve endpoint


asyncio.run(init_main())
