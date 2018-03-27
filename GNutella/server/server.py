# coding=utf-8
import socket, json, os, hashlib, select, sys
from random import randint
import threading
from dbmodules.dbconnection import *
from helper import *
from dbmodules.dbconnection import MongoConnection
from helpermodules.commandFile import *
from helpermodules.output_monitor import *
from helper import controlMandator

my_ipv4 = "172.016.004.001"
my_ipv6 = "fc00:0000:0000:0000:0000:0000:0004:0001"
my_port = "06000"
partialIpv4 = "172.016."
partialIpv6 = "fc00:0000:0000:0000:0000:0000:"


class Client(threading.Thread):
    def __init__(self, client, address, dbConnect, output_lock):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.dbConnect = dbConnect
        self.output_lock = output_lock

    def run(self):
        conn = self.client[0]
        cmd = conn.recv(self.size).decode('ascii')

        if cmd[:4] == "QUER":
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:35] + "\t" + cmd[36:75] + "\t" + cmd[76:80] + "\t" + cmd[80:82] + "\t" + cmd[82:102])

            ttl = int(cmd[80:82])
            notVisited = self.dbConnect.checkPktId(cmd[4:20])
            if ttl > 1 and notVisited:  # se ttl > 1 e il pktId non è gia passato di qua, ritrasmetto la query
                neighbors = self.dbConnect.getNeighbors(cmd[20:35], cmd[36:75])
                cmd = cmd[:80] + str(ttl - 1).zfill(2) + cmd[82:]  # abbasso di 1 il time to live se lo ritrasmetto
                send_near(self.output_lock, neighbors, cmd)

            if notVisited:  # se non  è passato di qua cerco nei miei file e contatto il proprietario della query
                queryStr = cmd[82:102]
                matchedList = self.dbConnect.getMatchedFiles(queryStr)
                for file in matchedList:
                    msg = "AQUE" + cmd[4:20] + my_ipv4 + "|" + my_ipv6 + my_port + file["md5"] + file["name"]
                    send_aque(self.output_lock, cmd[20:35], cmd[36:75], cmd[75:80], msg)

        elif cmd[:4] == "AQUE":
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock,
                   cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:35] + "\t" + cmd[36:75] + "\t" + cmd[76:80] + "\t" +
                   cmd[80:82] + "\t" + cmd[82:102])

            self.dbConnect.handleQueryAck(cmd[4:])

        elif cmd[:4] == "NEAR":
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + cmd[20:35] + "\t" + cmd[36:75] + "\t" +
                   cmd[76:80] + "\t" + cmd[80:82])

            ttl = int(cmd[80:82])
            notVisited = self.dbConnect.checkPktId(cmd[4:20])
            if ttl > 1 and notVisited:  # se ttl > 1 e il pktId non è gia passato di qua, ritrasmetto la query
                neighbors = self.dbConnect.getNeighbors(cmd[20:35], cmd[36:75])
                cmd = cmd[:80] + str(ttl - 1).zfill(2)  # abbasso di 1 il time to live se lo ritrasmetto
                send_near(self.output_lock, neighbors, cmd)
            if notVisited:
                if not controlMandator(self.address[0], cmd[20:35], cmd[36:75]):  # controllo se il pachetto è del mandante
                    # TODO: devo mandare anche i miei vicini o ci pensano loro?
                    # TODO: devo inserirlo tra i meiei vicini o no?
                    msg = "ANEA" + cmd[4:20] + my_ipv4 + "|" + my_ipv6 + my_port
                    send_aque(self.output_lock, cmd[20:35], cmd[36:75], cmd[75:80], msg)

        elif cmd[:4] == "ANEA":
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + cmd[20:35] + "\t" + cmd[36:75] + "\t" +
                   cmd[76:80] + "\t" + cmd[80:82])

            self.dbConnect.handleNearAck(cmd[4:])

        elif cmd[:4] == "RETR":
            output(self.output_lock, "\nMessagge received: " + cmd)
            md5Remoto = cmd[4:36]
            file = self.dbConnect.getFile(md5Remoto)
            fileFd = None
            try:
                fileFd = open("fileCondivisi/" + file['name'], "rb")
            except Exception as e:
                output(self.output_lock, 'Error: ' + str(e) + "\n")
            else:
                tot_dim = os.stat("fileCondivisi/" + file['name']).st_size  # Calcolo delle dimesioni del file
                n_chunks = int(tot_dim // 1024)  # Calcolo del numero di parti
                resto = tot_dim % 1024  # Eventuale resto
                if resto != 0.0:
                    n_chunks += 1

                fileFd.seek(0, 0)  # Spostamento all'inizio del file


                try:

                    chunks_sent = 0
                    chunk_size = 1024

                    buff = fileFd.read(chunk_size)  # Lettura del primo chunk

                    msg = 'ARET' + str(n_chunks).zfill(6)  # Risposta alla richiesta di download, deve contenere ARET ed il numero di chunks che saranno inviati

                    conn.sendall(msg)

                    output(self.output_lock, '\nUpload Message: ' + msg[0:4] + "\t" + msg[4:10])

                    while len(buff) == chunk_size:  # Invio dei chunks
                        try:
                            msg = str(len(buff)).zfill(5).encode('utf-8') + buff
                            conn.sendall(msg)  # Invio di
                            chunks_sent += 1

                            # dlg.Update(chunks_sent)
                            #update_progress(self.output_lock, chunks_sent, n_chunks,
                            #                'Uploading ' + fileFd.name)  # Stampa a video del progresso dell'upload

                            buff = fileFd.read(chunk_size)  # Lettura chunk successivo
                        except IOError:
                            output(self.output_lock,
                                   "Client_run-Error: Connection error due to the death of the peer!!!\n")
                    if len(buff) != 0:  # Invio dell'eventuale resto, se più piccolo di chunk_size

                        msg = str(len(buff)).zfill(5).encode('utf-8') + buff
                        conn.sendall(msg)

                    output(self.output_lock, "\r\nUpload Completed")

                    fileFd.close()  # Chiusura del file
                except EOFError:
                    output(self.output_lock, "Client_run-Error: You have read a EOF char")

                    # dlg.Destroy()


class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        self.host = ''
        self.port = 6000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.running = None
        self.output_lock = threading.Lock()
        self.dbConnect = MongoConnection()

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            output(self.output_lock, 'Listening on ' + str(self.port))
        except socket.error as message:
            if self.server:
                self.server.close()
            output(self.output_lock, "Server_open_socket: Could not open socket: " + str(message))
            sys.exit(1)
        except socket.error as message:
            if self.server:
                self.server.close()
                output(self.output_lock, "Server_open_socket-Error: Could not open socket: " + str(message))
            sys.exit(1)

    def run(self):
        self.open_socket()
        input = [self.server]
        self.running = 1
        try:
            while self.running:
                inputready, outputready, exceptready = select.select(input, [], [])

                for s in inputready:
                    if s == self.server:
                        try:
                            # handle the server socket
                            c = Client(self.server.accept(), "172.016.004.002", self.dbConnect, self.output_lock)
                            c.start()
                            self.threads.append(c)
                        except Exception as e:
                            output(self.output_lock, "Server_run_socket: " + str(e) + " / " + str(e))
        except Exception as e:
            output(self.output_lock, 'Server_run_socket: ' + str(e))

        """
        try:
            while self.allow_run:
                input_ready, read_ready, error_ready = select.select([self.ps_socket_v4, self.ps_socket_v6], [], []) # Ricezione di un input dalle due socket

                for s in input_ready:
                    if s == self.ps_socket_v4:                                              # Controllo della provenienza della richiesta
                        try:
                            conn, addr = self.ps_socket_v4.accept()                         # Attesa della connessione di un peer sulla socket ipv4
                            print 'Peer connected on: ', addr

                            peer = Client(conn, addr, self.file_list)      # Creazione di un thread che si occupa dell'upload del file
                            peer.start()
                            self.threads.append(peer)                                       # Inserimento del thread nella lista dei thread attivi
                        except Exception as e:
                            print "Error: "+Exception+" / " + e.message

                    elif s == self.ps_socket_v6:                                            # Controllo della provenienza della richiesta
                        try:
                            conn, addr = self.ps_socket_v6.accept()                         # Attesa della connessione di un peer sulla socket ipv4
                            print 'Peer connected on: ', addr

                            peer = PeerHandler.PeerHandler(conn, addr, self.file_list)      # Creazione di un thread che si occupa dell'upload del file
                            peer.start()
                            self.threads.append(peer)                                       # Inserimento del thread nella lista dei thread attivi
                        except Exception as e:
                            print "Error: "+Exception+" / " + e.message
        except Exception as e:
            print 'Error: ' + e.message
            """

    def stop(self):
        # close all threads

        self.running = 0

        for c in self.threads:
            c.join()

        self.server.close()


s = Server()
s.start()
