"""
A gopher client with a command-line interface written in Python
Modified from TCP client code written by Amy Csizmar Dalal

author: Jack Wines, Julia Connelly, and Adante Ratzlaff
CS 331, Spring 2018
date:  12 April 2018
"""

import sys
import socket
import re
import os

output_filename = "server_output.txt"
quit_commands = {"q", "Q", "quit", "Quit", "QUIT"}


def usage():
	print("Usage:  python3 gopherClient.py <server> <port number>")


# Checks if connection closes with some variant of newline + .
def closeConnectionProperly(path):
	with open(path, "r+", errors = "ignore") as f:
		s = f.read().rstrip()
		if not (len(s) > 1 and (s[-1] == "." and s[-2] in "\r\n")):
			print("Connection not closed properly", file=sys.stderr)


def parseServerOutput(output):
	"""
	Takes in a string, splits on CR/LFs, then splits on tabs to parse Gopher
	server output in a useful way for the client.
	:param output:  String, ideally Gopher server output
	:return: list of dictionaries, each dictionary representing the contents of
	a line.
	"""

	linebreak = re.compile("\r?\n\r?")
	lines = linebreak.split(output)
	data = []
	for line in lines:
		if len(line) > 0:
			line_data = {}
			file_char = line[0]
			if file_char == "0":
				line_data["type"] = "document"
			elif file_char == "1":
				line_data["type"] = "directory"
			else:
				line_data["type"] = "unknown type"
			line = line[1:]
			line_split = line.split("\t")

			# If the line is missing the minimum required information, ignore it and
			# move on.
			if len(line_split) >= 4:
				try:
					line_data["port"] = int(line_split[3])
				except ValueError:
					continue
				line_data["user display"] = line_split[0]
				line_data["selector"] = line_split[1]
				line_data["domain"] = line_split[2]
				data.append(line_data)
	return data


def displayOptions(lines):
	print("Enter the number of an option below or \"q\" to quit")
	option_number = 1
	for line in lines:
		display = str(option_number) + " " + line["user display"] \
				  + " (" + line["type"] + ")"
		print(display)
		option_number += 1


def displayFile():
	document = open(output_filename, errors="ignore")
	for line in document:
		print(line)


def sendRequest(server, port, sel=""):
	output_file = open(output_filename, "w+", errors="ignore")
	server_output = 1
	try:
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_sock.connect((server, port))
		server_sock.send((sel + "\r\n").encode('ascii', errors = "ignore"))
		while server_output:
			server_output = server_sock.recv(4096)
			output_file.write(server_output.decode(errors="ignore"))
		output_file.close()
	except OSError:
		print("Socket error - could not retrieve data from server")
		return False
	output_file.close()
	closeConnectionProperly(output_filename)
	return True


def cmdLineArgs():
	if len(sys.argv) >= 3:
		try:
			return sys.argv[1], int(sys.argv[2])
		except ValueError:
			print("The port number must be an integer.", file=sys.stderr)
		return False


def getUserInput():
	user_action = input()
	print()

	# Check if the input is the valid int
	try:
		return user_action, int(user_action) - 1
	except ValueError:
		return user_action, -1


def main():
	# Process command line args (server, port, message)
	args = cmdLineArgs()
	if not args:
		usage()
		return
	server, port = args

	# Establish an initial connection with the server
	links_file = ""
	if sendRequest(server, port):
		with open(output_filename, "r", errors = "ignore") as server_output:
			links_file = server_output.read()

	# Handle failed request
	if not links_file:
		print("Failed to connect to the server.", file=sys.stderr)
		return

	# Repeat a loop of requesting user input and attempting to make requests
	# until the user decides to quit.
	while True:
		lines = parseServerOutput(links_file)
		displayOptions(lines)
		if not lines:
			print("(No options to display)")

		user_action, index = getUserInput()
		# Input is an int and the index for a line previously displayed
		if 0 <= index <= len(lines) - 1:
			line = lines[index]

			if sendRequest(line["domain"], line["port"], line["selector"]):
				# If we asked for a directory, update the links file.
				if line["type"] == "directory":
					with open(output_filename, errors = "ignore") as server_output:
						links_file = server_output.read()
				# Otherwise, treat the type as a document and try to save a copy of it.  At least this way the user
				# has some binary to look at if they really want it.  Or we've downloaded a virus.
				elif line["type"] == "document":
					displayFile()
				else:
					print("Client will not attempt to handle an option of unknown type")

			# Server communication failed
			else:
				print("Sorry, the requested document or directory could not be retrieved at this time.")
				break

		# User input a recognized "quit" command
		elif user_action in quit_commands:
			# End the program
			break
		# We don't know what the user was trying to do
		else:
			print('Sorry, your input was not recognized. Please try again.')

		# Clear the output file at the end of each loop
		try:
			os.remove(output_filename)
		except OSError:
			pass
	# Try to remove the output file at the end of the program, too, just to be safe
	try:
		os.remove(output_filename)
	except OSError:
		pass


main()
