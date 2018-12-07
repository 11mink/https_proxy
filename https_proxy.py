import os
import sys
from socket import *
from threading import Thread

size = 8096

def usage():
	print("usage : python https_proxy.py <port>")

def quit(s):
	print("Press ENTER to quit")
	if sys.stdin.readline():
		s.close()
		os._exit(0)

def relayPacket(src, dst):
	while True:
		try: 
			data = src.recv(size)
			if not data:
				src.close()
				dst.close()
				return
			dst.send(data)
		except:
			src.close()
			dst.close()
			return

def proxyFunc(client):
	data = client.recv(size)
	if not data:
		return

	#Get Server Address
	lines = data.split("\r\n")
	for line in lines:
		if line.startswith("CONNECT"):
			host = line[line.index(" ")+1:line.index(":")]
			port = line[line.index(":")+1:line.index(" HTTP/1.1")]
			break
	addr = (host, port)	

	#Connect to Server
	try:
		server = create_connection(addr)
	except:
		return

	#Reply with 200 response
	client.send("HTTP/1.1 200 Connection Established\r\n\r\n")

	#Client --> Server
	Thread(target = relayPacket, args = (client,server, )).start()
	#Client <-- Server
	Thread(target = relayPacket, args = (server,client, )).start()

def main():
	if len(sys.argv) != 2:
		usage()
		sys.exit()

	addr = ("127.0.0.1", int(sys.argv[1]))

	proxy = socket(AF_INET, SOCK_STREAM)
	proxy.bind(addr)
	proxy.listen(5)
	Thread(target = quit, args = (proxy,)).start()

	while True:
		client, addr = proxy.accept()
		Thread(target = proxyFunc, args = (client,)).start()

if __name__ == "__main__":
	main()
