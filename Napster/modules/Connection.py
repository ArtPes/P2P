# coding=utf-8
# socket.inet_aton('172.0.0.1') mi trasforma una stringa ipv4 in un ipv4 per il sistema
# socket.inet_pton(socket.AF_INET6, some_string)
import socket
import random

class Connection:
    """
    Crea le connessioni a directory e peers

    Attributes:
        socket: socket per le comunicazioni
        ipv4: indirizzo ipv4
        ipv6: indirizzo ipv6
        port: porta
    """
    socket = None
    ipv4 = None
    port = None
    ipv6 = None

    def __init__(self, ipv4, ipv6, port):
        """
        Costruttore della classe Connection

        :param ipv4: indirizzo ipv4
        :type ipv4: str
        :param ipv6: indirizzo ipv6
        :type ipv6: str
        :param port: porta
        :type port: str
        """
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = int(port)
        #self.ipv4 = '127.0.0.1'
        #self.ipv6 = '::1'
        #print (self.dir_ipv4)
        #print (self.dir_ipv6)

    def connect(self):
        """
        Crea una socket TCP selezionando un indirizzo a caso (con probabilità 50/50) tra ipv4 e ipv6
        Da utilizzare per le richieste alle directory
        """
        if random.choice((True, False)):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.connect((self.ipv4, self.port))                                 # inizializzazione della connessione
                print ("Succesfully connected to: " + self.ipv4 + " " + str(self.port))
            except socket.error, msg:
                print ("Connection error ipv4!\nTerminated.\nSocket.error : %s" % msg)
                print self.ipv4 + str(self.port)

        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.connect((self.ipv6, self.port))                                 # inizializzazione della connessione
                print ("Succesfully connected to: " + self.ipv6 + " " + str(self.port))
            except socket.error, msg:
                print ("Connection error ipv6!\nTerminated.\nSocket.error : %s" % msg)
                print self.ipv4 + str(self.port)

    '''
    def listen(self):
        """
        Crea una socket TCP selezionando un indirizzo a caso (con probabilità 50/50) tra ipv4 e ipv6
        Da utilizzare per le richieste degli altri peer
        """
        if random.choice((True, False)):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.bind((self.ipv4, self.port))                                    # inizializzazione della connessione
                self.socket.listen(5)
                print ("Listening on :" + self.ipv4 + str(self.port))
            except socket.error, msg:
                print ("Connection error ipv4!\nTerminated.\nSocket.error : %s" % msg)
                print self.ipv4 + " " + str(self.port)

        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.bind((self.ipv6, self.port))                                    # inizializzazione della connessione
                self.socket.listen(5)
                print ("Succesfully connected to :" + self.ipv6 + str(self.port))
            except socket.error, msg:
                print ("Connection error ipv6!\nTerminated.\nSocket.error : %s" % msg)
                print self.ipv6 + " " + str(self.port)
    '''

    def listen_v4(self):
        """
        Crea una socket TCP ipv4 in ascolto sull'indirizzo e porta specificati
        Da utilizzare per le richieste degli altri peer
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.ipv4, self.port))                                    # inizializzazione della connessione
            self.socket.listen(5)
            print "Listening on :" + self.ipv4 + str(self.port)
        except socket.error, msg:
            print "Connection error ipv4!\nTerminated.\nSocket.error : %s" % str(msg)
            print self.ipv4 + " " + str(self.port)

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
            print "Listening on :" + self.ipv6 + str(self.port)
        except socket.error, msg:
            print "Connection error ipv6!\nTerminated.\nSocket.error : %s" % str(msg)
            print self.ipv6 + " " + str(self.port)
