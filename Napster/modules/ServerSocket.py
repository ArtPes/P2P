import socket, errno
import os
import sys
from thread import *
from multiprocessing import Process
from thread import *
import hashlib
import base64

def convert_to_string(no, numBytes):
    result = str(no)
    num = len(result)
    while num < numBytes:
        result = '0' + result
        num += 1
    return result

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()


def clientthread(conn):
        try:
            cmd = conn.recv(4)
            if cmd == 'RETR':
                fileRemoteMd5 = conn.recv(16)


            for root, dirs, files in os.walk("shareable"):
                for file in files:
                    fileMd5 = hashfile(open("shareable/" + file, 'rb'), hashlib.md5())
                    if fileRemoteMd5 == fileMd5:
                        length = os.stat("shareable/" + file).st_size
                        numChunks = length / 1024 + 1

                        strChunks = convert_to_string(numChunks, 6)
                        conn.send('ARET')
                        conn.send(strChunks)
                        with open("shareable/" + file, 'rb') as f:
                            l = f.read(1024)
                            while (l):
                                lenChunk = len(str(l))
                                strLenChunk = convert_to_string(lenChunk, 5)
                                conn.send(strLenChunk)
                                conn.send(l)
                                l = f.read(1024)
        except socket.error, e:
            if isinstance(e.args, tuple):
                print "errno is %d" % e[0]
                if e[0] == errno.EPIPE:
                   # remote peer disconnected
                   print "Detected remote disconnect"
                else:
                   # determine and handle different error
                   pass
            else:
                print "socket error ", e
            conn.close()



def start_server():
    #creo un nuvo processo in ascolto delle richieste dei peer
    newpid = os.fork()
    if newpid == 0:              #sono nel processo figlio
        HOST = None               # Symbolic name meaning all available interfaces
        PORT = 3000              # Arbitrary non-privileged port
        s = None
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_INET6,
                                      socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                s = None
                continue
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(sa)
                s.listen(5)
            except socket.error as msg:
                s.close()
                s = None
                continue
            break
        if s is None:
            print 'could not open socket'
            sys.exit(1)

        while True:
            #wait to accept a connection - blocking call
            conn, addr = s.accept()
            print 'Connected by', addr

            #start new thread takes 1st argument as a function name to be run
            start_new_thread(clientthread ,(conn,))
        s.close()
    else:
        return newpid #per chiudere il processo del server al logout