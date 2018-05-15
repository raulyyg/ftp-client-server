#!/usr/bin/python

import socket, sys, os

# USAGE : client.py {host} {port} {protocol [GET, PUT, DEL]} {filename}
host = sys.argv[1]
port = int(sys.argv[2])

protocol = sys.argv[3]
protocol = protocol.upper()
file = sys.argv[4]

SIZE_SIZE = 11
PromptString = "FTP> ";

def getFileSizeMsg(size):

	# Convert the size into string
	strSize = str(size)

	# add 0's to the front of the strSize
	while len(strSize) < SIZE_SIZE:
		strSize = "0" + strSize;

	print("size: ", strSize);

	return bytes(strSize, "utf-8");



########




#####################################################
# Sends the specified amount of data using
# the specified socket
# @param sendSock - the socket to use for sending
# @param sendBuff - the buffer to send
#####################################################
def sendAll(sendSock, sendBuff):

	# The number of bytes successfully sent
	numSent = 0

	# Keep sending until all is sent
	while len(sendBuff) > numSent:

		# Send as much as you can
		sendCount = sendSock.send(sendBuff[numSent:])

		# Break the loop on error
		if not sendCount:
			break

		# Count the bytes you sent
		numSent += sendCount

def sendDataString(cliSock, data):
	# Put the file size into the message
	fileSizeMsg = getFileSizeMsg(len(data));

	# Send the message!
	sendAll(cliSock, fileSizeMsg);

	sendAll(cliSock, bytes(data, "utf-8"));

def sendDataFile(cliSock, fileName):
	# Get the file size
	fileSize = os.path.getsize(fileName);

	# Put the file size into the message
	fileSizeMsg = getFileSizeMsg(fileSize);

	# Send the message!
	sendAll(cliSock, fileSizeMsg);

	# How many file bytes have been sent
	numSent = 0;

	# Open the file for reading
	fileObj = open(fileName, "rb");

	# Keep sending the file in small chunks until all is sent
	while numSent < fileSize:

		# Read the bytes
		fileData = fileObj.read(4096);

		# The file data
		if not fileData:
			break;

		# Send all the bytes
		sendAll(cliSock, fileData);

		# Count the bytes
		numSent += len(fileData);
	#while numSent < fileSize

	fileObj.close();


#########


#########

#########################################
# Receives the number of bytes specified
# @param recvSock - the socket from which
# to receive
# @param recvSize - how much to receive
# @return - the data received
########################################
def recvAll(recvSock, recvSize):

	# The buffer to store the received contents
	recvBuff = bytearray();
	joinList = bytearray();

	# Keep receiving until all is received
	while not len(recvBuff) == recvSize:

		# The receiver buffer
		buff = recvSock.recv(recvSize - len(recvBuff))

		# Connection issues or we are done
		if not buff:
			break

		# Save the received content
		recvBuff = joinList.join([recvBuff, buff]);

	return recvBuff;

def receiveDataString(cliSock):
	# Get the file size message
	fileSizeMsg = recvAll(cliSock, SIZE_SIZE);

	# Get the file size from the message
	fileSize = int(fileSizeMsg.decode("utf-8"));

	buffer = bytearray();
	joinList = bytearray();

	# How many bytes are there left to receive
	numBytesLeft = fileSize;

	# Keep receiving and saving until all is saved
	while numBytesLeft > 0:

		# How many bytes to receive
		numToRecv = 4096;

		# If we have less than 4096 bytes
		if numBytesLeft < 4096:
			numToRecv = numBytesLeft;

		# Get the data
		fileData = recvAll(cliSock, numToRecv);

		buffer = joinList.join([buffer, fileData]);

		# Count the bytes
		numBytesLeft -= len(fileData);

	return buffer.decode("utf-8");

def receiveDataFile(dataSock, fileName):
	# Get the file size message
	fileSizeMsg = recvAll(dataSock, SIZE_SIZE);

	# Get the file size from the message
	fileSize = int(fileSizeMsg.decode("utf-8"));
	print("filesize: ", fileSize);

	# How many bytes are there left to receive
	numBytesLeft = fileSize;

	# Open the file
	fileObj = open(fileName, "wb");

	# Keep receiving and saving until all is saved
	while numBytesLeft > 0:

		# How many bytes to receive
		numToRecv = 4096;

		# If we have less than 4096 bytes
		if numBytesLeft < 4096:
			numToRecv = numBytesLeft;

		# Get the data
		fileData = recvAll(dataSock, numToRecv);

		# Save the data
		fileObj.write(fileData);

		# Count the bytes
		numBytesLeft -= len(fileData);

	# Close the file and the socket
	fileObj.close();

########



sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect((host,port))

status = sock.recv(5)
if status == "READY":
	if protocol == "GET":
		
		sock.send("GET")
		# send file name, receive number of bytes 
		sock.send(file)
		size = sock.recv(1024)
		status = "OK"
		sock.send(status)
			
		f = open(file,'wb')
		print "client receiving file " + file + " " + str(size) + " bytes"
		bytesReceived = 0
		while bytesReceived < int(size):
			data = sock.recv(int(size) % 1024)
			f.write(data)
			bytesReceived+=len(data)
		status = sock.recv(4)
		
		if status == "DONE":
			print "Complete"
			 
			
		
	elif protocol == "PUT":
		if os.access(file, os.R_OK):
			size = os.path.getsize(file)
			f = open(file,'rb')
			sock.send("PUT")
			sock.send(file)
			# wait for ok from server, send file
			status = sock.recv(2) 
			if status == "OK":
				print "client sending file " + file + " " + str(size) + " bytes"
				sock.send(str(size))
				bytesSent = 0
				while bytesSent < size:
					data = f.read(1024)
					sock.send(data)
					bytesSent+=len(data)
				
				status = sock.recv(4)
				if status == "DONE":
					print "Complete"
		elif os.access(file, os.F_OK):
			print "Cannot access file " + file + " or it does not exist" 
	elif protocol == "DEL":
		sock.send("DEL")
		sock.send(file)
		print "deleting file " + file 
		
		status = sock.recv(1024)
		if status == "DONE":
			print "Complete"
		else:
			print "Server cannot access " + file
	else:
		print "Please enter a valid protocol"
