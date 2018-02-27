# coding=utf-8
import threading
import PeerHandler
import Connection
import select


class PeerServer(threading.Thread):
    """
    Server multithread che gestisce le connessionni in entrata e l'upload dei file agli altri peer

    :param ps_socket_v4: socket ipv4 su cui fare da server per gli altri peer
    :type ps_socket_v4: object
    :param ps_socket_v6: socket ipv4 su cui fare da server per gli altri peer
    :type ps_socket_v6: object
    :param ps_ipv4: indirizzo ipv4 su cui fare da server per gli altri peer
    :type ps_ipv4: str
    :param ps_ipv6: indirizzo ipv6 su cui fare da server per gli altri peer
    :type ps_ipv6: str
    :param ps_port: porta su cui fare da server per gli altri peer
    :type ps_port: str
    :param file_list: lista dei file disponibili per l'upload
    :type file_list: list
    :param allow_run: flag di esecuzione del server
    :type allow_run: bool
    :param threads: lista dei thread attivi
    :type threads: list
    """
    ps_socket_v4 = None
    ps_socket_v6 = None
    ps_ipv4 = None
    ps_ipv6 = None
    ps_port = None
    file_list = None
    allow_run = True
    threads = []

    def __init__(self, ipv4, ipv6, port, file_list):
        """
        Costruttore della classe PeerServer

        :param ipv4: indirizzo ipv4 su cui fare da server per gli altri peer
        :type ipv4: str
        :param ipv6: indirizzo ipv6 su cui fare da server per gli altri peer
        :type ipv6: str
        :param port: porta su cui fare da server per gli altri peer
        :type port: str
        :param file_list: lista dei file disponibili per l'upload
        :type file_list: list
        """
        threading.Thread.__init__(self)

        self.ps_ipv4 = ipv4
        self.ps_ipv6 = ipv6
        self.ps_port = port
        self.file_list = file_list

    '''
    def run(self):
        """
        Gestisce le connessioni in entrata creando per ognuna un nuovo thread che effettua l'upload del file richiesto
        """
        c = Connection.Connection(self.ps_ipv4, self.ps_ipv6, self.ps_port)         # Inizializzazione della socket in ascolto per le richieste degli altri peer
        c.listen()
        #self.ps_socket_v4 = c.socket

        try:
            while self.allow_run:
                try:
                    conn, addr = c.socket.accept()
                    #conn, addr = self.ps_socket_v4.accept()                    # Attesa della connessione di un peer
                    print 'Peer connected on: ', addr

                    peer = PeerHandler.PeerHandler(conn, addr, self.file_list)      # Creazione di un thread che si occupa dell'upload del file
                    peer.start()
                    self.threads.append(peer)                                       # Inserimento del thread nella lista dei thread attivi

                except Exception as e:
                    print "Error: "+Exception+" / " + e.message
        except Exception as e:
            print 'Error: ' + e.message
    '''

    def run(self):
        """
        Gestisce le connessioni in entrata creando per ognuna un nuovo thread che effettua l'upload del file richiesto
        """

        c = Connection.Connection(self.ps_ipv4, self.ps_ipv6, self.ps_port) # Inizializzazione della socket in ascolto per le richieste degli altri peer
        c.listen_v4()
        self.ps_socket_v4 = c.socket
        c.listen_v6()
        self.ps_socket_v6 = c.socket

        try:
            while self.allow_run:
                input_ready, read_ready, error_ready = select.select([self.ps_socket_v4, self.ps_socket_v6], [], []) # Ricezione di un input dalle due socket

                for s in input_ready:
                    if s == self.ps_socket_v4:                                              # Controllo della provenienza della richiesta
                        try:
                            conn, addr = self.ps_socket_v4.accept()                         # Attesa della connessione di un peer sulla socket ipv4
                            print 'Peer connected on: ', addr

                            peer = PeerHandler.PeerHandler(conn, addr, self.file_list)      # Creazione di un thread che si occupa dell'upload del file
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

    def stop(self):
        """
        Ferma l'esecuzione del server che risponde alle richieste dei peer
        Da utilizzare al momento del logout
        """

        self.allow_run = False

        for p in self.threads:                                                 # Al logout si aspetta la terminazione dei thread in esecuzione
            p.join()

        self.ps_socket_v4.close()                                              # Chiusura delle socket in ascolto
        self.ps_socket_v6.close()                                              # Chiusura delle socket in ascolto
