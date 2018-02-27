# coding=utf-8
import threading
import socket
import helpers


class PeerHandler(threading.Thread):
    """
    gestore dei peer che si connettono per scaricare un file
    :param conn: connessione al peer che vuole effettuare il download
    :type conn: object
    :param addr: indirizzi del peer che vuole effettuare il download
    :type addr: object
    :param file_list: lista dei file disponibili per l'upload
    :type file_list: list
    """
    conn = None
    addr = None
    file_list = None
    md5 = None

    def __init__(self, conn, addr, file_list):
        """
        Costruttore della classe PeerHandler

        :param conn: connessione al peer che vuole effettuare il download
        :type conn: object
        :param addr: indirizzi del peer che vuole effettuare il download
        :type addr: object
        :param file_list: lista dei file disponibili per l'upload
        :type file_list: list
        """
        threading.Thread.__init__(self)

        self.conn = conn
        self.addr = addr
        self.file_list = file_list

    def filesize(self, n):
        """
        Calcola la dimensione del file

        :param n: nome del file
        :type n: str
        :return: dimensione del file
        :rtype: int
        """

        f = open(n, 'r')
        f.seek(0, 2)
        sz = f.tell()
        f.seek(0, 0)
        f.close()
        return sz

    def run(self):
        """
        Codice eseguito nel thread.
        Riceve dal peer l'md5 del file che desidera scaricare e lo invia diviso in parti
        """

        try:
            cmd = self.conn.recv(4)                                                 # Ricezione del comando di download dal peer, deve contenere RETR
        except socket.error as e:
            print 'Socket Error: ' + e.message
        except Exception as e:
            print 'Error: ' + e.message
        else:
            if cmd == "RETR":
                try:
                    self.md5 = self.conn.recv(32)                                   # Ricezione dell'md5 del file da inviare
                    print 'Received md5: ' + self.md5
                except socket.error as e:
                    print 'Socket Error: ' + e.message
                except Exception as e:
                    print 'Error: ' + e.message
                else:
                    found_name = None

                    for idx, file in enumerate(self.file_list):                     # Ricerca del file da inviare tra quelli disponibili
                        if file.md5 == self.md5:
                            found_name = file.name

                    if found_name is None:
                        print 'Found no file with md5: ' + self.md5
                    else:

                        chunk_size = 1024                                           # Dimensione di una parte di file

                        try:
                            file = open("shareable/" + found_name, "rb")
                        except Exception as e:
                            print 'Error: ' + e.message + "\n"
                        else:
                            tot_dim = self.filesize("shareable/" + found_name)      # Calcolo delle dimesioni del file
                            n_chunks = int(tot_dim // chunk_size)              # Calcolo del numero di parti
                            resto = tot_dim % chunk_size                            # Eventuale resto
                            if resto != 0.0:
                                n_chunks += 1

                            file.seek(0, 0)                                         # Spostamento all'inizio del file

                            try:
                                buff = file.read(chunk_size)                        # Lettura del primo chunk
                                chunks_sent = 0

                                msg = 'ARET' + str(n_chunks).zfill(6)               # Risposta alla richiesta di download, deve contenere ARET ed il numero di chunks che saranno inviati
                                print 'Upload Message: ' + msg
                                self.conn.sendall(msg)
                                print 'Sending chunks...'

                                while len(buff) == chunk_size:                      # Invio dei chunks
                                    try:
                                        msg = str(len(buff)).zfill(5) + buff
                                        self.conn.sendall(msg)                      # Invio di
                                        chunks_sent += 1

                                        helpers.update_progress(chunks_sent, n_chunks, 'Uploading ' + file.name)      # Stampa a video del progresso dell'upload

                                        buff = file.read(chunk_size)                # Lettura chunk successivo
                                    except IOError:
                                        print "Connection error due to the death of the peer!!!\n"
                                if len(buff) != 0:                                  # Invio dell'eventuale resto, se più piccolo di chunk_size
                                    msg = str(len(buff)).zfill(5) + buff
                                    self.conn.sendall(msg)
                                print "\nUpload Completed"
                                file.close()                                        # Chiusura del file
                            except EOFError:
                                print "You have read a EOF char"
            else:
                print "Error: unknown directory response.\n"

        self.conn.shutdown(1)                                                       # Segnalazione di fine comunicazione
        self.conn.close()                                                           # Chiusura comunicazione
