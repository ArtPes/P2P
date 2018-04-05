# coding=utf-8
# socket.inet_aton('172.0.0.1') mi trasforma una stringa ipv4 in un ipv4 per il sistema
# socket.inet_pton(socket.AF_INET6, some_string)
import socket
import random
import sys
sys.path.append('/home/art/PycharmProjects/P2P/GNutella/helpermodules')
from output_monitor import output


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
        self.ipv4 = remove_zero(self.ipv4)
        #if True:
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


def add_zero(ip):                                  # aggiunge 0 davanti
    list = ip.split(".")

    a = list[0].zfill(3)
    b = list[1].zfill(3)
    c = list[2].zfill(3)
    d = list[3].zfill(3)

    new_ip = a + "." + b + "." + c + "." + d

    return new_ip


def remove_zero(ip):                               # rimuove 0 davanti
    list = ip.split(".")

    a = int(list[0])
    b = int(list[1])
    c = int(list[2])
    d = int(list[3])

    new_ip = str(a) + "." + str(b) + "." + str(c) + "." + str(d)

    return new_ip