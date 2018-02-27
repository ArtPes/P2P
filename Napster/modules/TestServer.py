import socket
import json
import SharedFile
import os
import hashlib
from random import randint
import helpers

import threading


#TCP_IP = '172.30.8.1'#'127.0.0.1'
#TCP_IP = 'fc00::8:1'
#TCP_IP = "127.0.0.1"
#TCP_IP = '::1'
import select
import sys
class Client(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024

    def run(self):
        running = 1
        while running:
            conn = self.client
            cmd = conn.recv(4)

            if cmd == "FIND":
                print "received command: " + str(cmd)
                sessionId = conn.recv(16)
                print "received sessionID: " + str(sessionId)
                term = conn.recv(20)
                print "received search term: " + str(term)


                #  Finta risposta dalla directory
                #  Number of different md5
                idmd5 = None

                response = 'AFIN' + str(2).zfill(3)

                for root, dirs, files in os.walk("./share"):
                    for file in files:
                        filemd5 = helpers.hashfile(open("./share/" + file, 'rb'), hashlib.md5())
                        filename = file.ljust(100)
                        copies = str(2).zfill(3)
                        response += filemd5
                        response += filename
                        response += copies  # 2 copie
                        response += '127.000.000.001|0000:0000:0000:0000:0000:0000:0000:0001'
                        response += '03000'
                        response += '172.030.008.003|fc00:0000:0000:0000:0000:0000:0008:0003'
                        response += '03000'

                conn.send(response)

            elif cmd == "LOGI":
                msg = conn.recv(55)
                print "received command: " + str(cmd)
                print "received ipv4: " + msg[:4]
                print "received ipv6: " + msg[4:]
                print "received porta: "

                response = 'ALGI' + '1234567891234567'
                print response
                conn.sendall(response)

            elif cmd == "GREG":
                response = 'ADRE' + '002'
                print response
                conn.send(response)

            elif cmd == 'LOGO':
                print "received command: " + str(cmd)
                sessionid = conn.recv(16)
                print "peer: " + sessionid
                response = 'ALGO' + '003'
                print response
                conn.send(response)

            elif cmd == 'ADDF':
                response = 'RADD' + '003'
                print response
                conn.send(response)

            elif cmd == 'DELF':
                response = 'RDEL' + '003'
                print response
                conn.send(response)

            elif cmd == 'RETR':
                fileRemoteMd5 = conn.recv(32)

                for root, dirs, files in os.walk("share"):
                    for file in files:
                        fileMd5 = helpers.hashfile(open("share/" + file, 'rb'), hashlib.md5())
                        if fileRemoteMd5 == fileMd5:
                            print "Nome file dal client: ", file
                            length = os.stat("share/" + file).st_size
                            print "Lunghezza file", length
                            numChunks = length / 1024 + 1

                            strChunks = str(numChunks).zfill(6)
                            conn.send('ARET'+strChunks)

                            msg = ''
                            with open("share/" + file, 'rb') as f:
                                l = f.read(1024)
                                while (l):
                                    lenChunk = len(str(l))
                                    strLenChunk = str(lenChunk).zfill(5)
                                    msg += strLenChunk
                                    msg += l
                                    l = f.read(1024)
                            f.close()
                            conn.send(msg)
            elif cmd == 'DREG':
                conn.recv(48)
                print response
                conn.send('ADRE' + str(5).zfill(5))
class Server:
    def __init__(self):
        self.host = ''
        self.port = 3000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)
            print 'Ascolto peer sulla porta', self.port
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        input = [self.server,sys.stdin]
        running = 1
        while running:
            inputready,outputready,exceptready = select.select(input,[],[])

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    c = Client(self.server.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0

        # close all threads

        self.server.close()
        for c in self.threads:
            c.join()

s = Server()
s.run()
