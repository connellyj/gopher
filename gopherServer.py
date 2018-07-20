"""
A Gopher Server written in Python

author:  Julia Connelly, Adante Ratzlaff, Jack Wines
CS 331, Spring 2018
date:  12 April 2018
"""
import sys
import socket
import os


class GopherServer:
    def __init__(self, port=50000):
        self.port = port
        self.host = ""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.links = GopherServer.readLinks("root/")

    @staticmethod
    def cleanLinksFile(s):
        cleanLinks = ""
        splitLines = s.split("\n")
        splitLines.sort()
        for line in splitLines:
            splitLine = line.split("\t")
            properLengths = [70 - 1, 225 - 1]
            for name, length, i in zip(splitLine[:2], properLengths, range(2)):
                splitLine[i] = name[:length]
            cleanLinks += "\t".join(splitLine) + "\r\n"
        return cleanLinks

    @staticmethod
    def readLinks(linksPath):
        try:
            with open(linksPath + ".links", "r") as linksFile:
                return GopherServer.cleanLinksFile(linksFile.read())
        except OSError:
            return None

    @staticmethod
    def readFile(filePath):
        try:
            with open(filePath, "r", encoding = "ascii", errors = "ignore") as file:
                return file.read()
        except OSError:
            return None

    @staticmethod
    def getResponse(filePath):
        filePath = "root/" + filePath.replace("\r", "").replace("\n", "")
        if os.path.isdir(filePath):
            return GopherServer.readLinks(filePath)
        else:
            return GopherServer.readFile(filePath)

    @staticmethod
    def addPeriodOnNewLine(resp):
        return resp + "\r\n."

    # returns False and prints if fails
    @staticmethod
    def safeDecode(data, clientSock):
        try:
            return data.decode(encoding = "ascii", errors = "ignore")
        except UnicodeDecodeError:
            errStr = "Error decoding from utf-8\r\n"
            print(errStr, file=sys.stderr)
            clientSock.sendall(errStr.encode('ascii'))
            return None

    # returns an error string and prints if fails
    @staticmethod
    def safeEncode(s):
        try:
            return s.encode('ascii', errors = "ignore")
        except UnicodeEncodeError:
            errStr = "Error encoding to utf-8. str: "
            print(errStr, s, "\r\n", file=sys.stderr)
            return errStr.encode('ascii', errors = "ignore")

    def listen(self):
        self.sock.listen(5)

        while True:
            clientSock, clientAddr = self.sock.accept()
            print("Connection received from ", clientSock.getpeername())

            data = clientSock.recv(1024)

            # try to decode data. utf-8 is the default
            decodedData = GopherServer.safeDecode(data, clientSock)
            if not decodedData:
                continue
            # an empty string means we should send the .links file.
            if decodedData.strip() == "":
                toSend = GopherServer.safeEncode(GopherServer.addPeriodOnNewLine(self.links))
                clientSock.sendall(toSend)
            else:
                info = GopherServer.getResponse(decodedData)
                if info:
                    clientSock.sendall(GopherServer.safeEncode(GopherServer.addPeriodOnNewLine(info)))
                else:
                    clientSock.sendall(
                        GopherServer.addPeriodOnNewLine("Received file path does not exist.\r\n").encode('ascii'))
            clientSock.close()


def main():
    # Create a server
    if len(sys.argv) > 1:
        try:
            server = GopherServer(int(sys.argv[1]))
        except ValueError:
            print("Error in specifying port. Creating server on default port.")
            server = GopherServer()
    else:
        server = GopherServer()

    # Listen forever
    print("Listening on port " + str(server.port))
    server.listen()


main()
