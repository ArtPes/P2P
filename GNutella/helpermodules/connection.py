# coding=utf-8
# socket.inet_aton('172.0.0.1') mi trasforma una stringa ipv4 in un ipv4 per il sistema
# socket.inet_pton(socket.AF_INET6, some_string)
import socket
import random
from helpermodules.output_monitor import output


class Connection:
    socket = None
    ipv4 = None
    port = None
    ipv6 = None

    def __init__(self, output_lock, ipv4, ipv6, port):
        self.output_lock = output_lock
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = int(port)

    def connect(self):
        """
        Crea una socket TCP selezionando un indirizzo a caso (con probabilità 50/50) tra ipv4 e ipv6
        Da utilizzare per le richieste alle directory
        """
        if random.choice((True, False)):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
            #self.socket.settimeout(5)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self.socket.settimeout(1)
            try:
                self.socket.connect((self.ipv4, self.port))                                 # inizializzazione della connessione
                output(self.output_lock, "Succesfully connected to: " + self.ipv4 + " " + str(self.port))
            except socket.error as msg:
                output(self.output_lock, "Connection error ipv4!\nTerminated.\nSocket.error : %s" % msg)
                output(self.output_lock, self.ipv4 + str(self.port))

        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
            #self.socket.settimeout(5)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self.socket.settimeout(1)
            try:
                self.socket.connect((self.ipv6, self.port))                                 # inizializzazione della connessione
                output(self.output_lock, "Succesfully connected to: " + self.ipv6 + " " + str(self.port))
            except socket.error as msg:
                output(self.output_lock, "Connection error ipv6!\nTerminated.\nSocket.error : %s" % msg)
                output(self.output_lock, self.ipv6 + str(self.port))

    def listen_v4(self):
        """
        Crea una socket TCP ipv4 in ascolto sull'indirizzo e porta specificati
        Da utilizzare per le richieste degli altri peer
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv6
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.ipv4, self.port))                                    # inizializzazione della connessione
            self.socket.listen(5)
            output(self.output_lock, "Listening on :" + self.ipv4 + str(self.port))
        except socket.error as msg:
            output(self.output_lock, "Connection error ipv4!\nTerminated.\nSocket.error : %s" % str(msg))
            output(self.output_lock, self.ipv4 + " " + str(self.port))

    def listen_v6(self):
        """
        Crea una socket TCP ipv6 in ascolto sull'indirizzo e porta specificati
        Da utilizzare per le richieste degli altri peer
        """
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.ipv6, self.port))                                    # inizializzazione della connessione
            self.socket.listen(5)
            output(self.output_lock, "Listening on :" + self.ipv6 + str(self.port))
        except socket.error as msg:
            output(self.output_lock, "Connection error ipv6!\nTerminated.\nSocket.error : %s" % str(msg))
            output(self.output_lock, self.ipv6 + " " + str(self.port))