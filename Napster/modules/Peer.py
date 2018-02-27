# coding=utf-8
import os
from SharedFile import SharedFile
from Owner import Owner
import Download
import hashlib
import socket
import Connection
import helpers


class Peer(object):
    """
    Rappresenta il peer corrente

    Attributes:
        session_id: identificativo della sessione corrente fornito dalla directory
        my_ipv4: indirizzo ipv4 del peer corrente
        my_ipv6: indirizzo ipv6 del peer corrente
        my_port: porta del peer corrente
        dir_ipv4: indirizzo ipv4 della directory
        dir_ipv6: indirizzo ipv6 della directory
        dir_port: porta della directory
        files_list:
        directory: connessione alla directory
    """
    session_id = None
    my_ipv4 = "172.030.008.002"
    my_ipv6 = "fc00:0000:0000:0000:0000:0000:0008:0002"
    my_port = "06000"
    dir_ipv4 = "172.030.001.001"
    dir_ipv6 = "fc00:0000:0000:0000:0000:0000:0001:0001"
    dir_port = "03000"
    files_list = []
    directory = None

    def __init__(self):
        """
        Costruttore della classe Peer
        """
        # Searching for shareable files
        for root, dirs, files in os.walk("shareable"):
            for file in files:
                file_md5 = helpers.hashfile(open("shareable/" + file, 'rb'), hashlib.md5())
                new_file = SharedFile(file, file_md5)
                self.files_list.append(new_file)

    def login(self):
        """
        Esegue il login alla directory specificata
        """

        print 'Logging in...'
        msg = 'LOGI' + self.my_ipv4 + '|' + self.my_ipv6 + self.my_port
        print 'Login message: ' + msg

        response_message = None
        try:
            self.directory = None
            c = Connection.Connection(self.dir_ipv4, self.dir_ipv6, self.dir_port)      # Creazione connessione con la directory
            c.connect()
            self.directory = c.socket

            self.directory.send(msg)                                                    # Richiesta di login
            print 'Message sent, waiting for response...'
            response_message = self.directory.recv(20)                                  # Risposta della directory, deve contenere ALGI e il session id
            print 'Directory responded: ' + response_message
        except socket.error, msg:
            print 'Socket Error: ' + str(msg)
        except Exception as e:
            print 'Error: ' + e.message
        else:
            if response_message is None:
                print 'No response from directory. Login failed'
            else:
                self.session_id = response_message[4:20]
                if self.session_id == '0000000000000000' or self.session_id == '':
                    print 'Troubles with the login procedure.\nPlease, try again.'
                else:
                    print 'Session ID assigned by the directory: ' + self.session_id
                    print 'Login completed'

    def logout(self):
        """
        Esegue il logout dalla directory a cui si è connessi
        """
        print 'Logging out...'
        msg = 'LOGO' + self.session_id
        print 'Logout message: ' + msg

        response_message = None
        try:
            self.directory.send(msg)                                                    # Richeista di logout
            print 'Message sent, waiting for response...'

            response_message = self.directory.recv(7)                                   # Risposta della directory, deve contenere ALGO e il numero di file che erano stati condivisi
            print 'Directory responded: ' + response_message
        except socket.error, msg:
            print 'Socket Error: ' + str(msg)
        except Exception as e:
            print 'Error: ' + e.message
        else:
            if response_message is None:
                print 'No response from directory. Login failed'
            elif response_message[0:4] == 'ALGO':
                self.session_id = None

                number_file = int(response_message[4:7])                                # Numero di file che erano stati condivisi
                print 'You\'d shared ' + str(number_file) + ' files'

                self.directory.close()                                                  # Chiusura della connessione
                print 'Logout completed'
            else:
                print 'Error: unknown response from directory.\n'

    def share(self):
        """
        Aggiunge un file alla directory rendendolo disponibile agli altri peer per il download
        """
        found = False
        while not found:
            print '\nSelect a file to share (\'c\' to cancel):'
            for idx, file in enumerate(self.files_list):
                print str(idx) + ": " + file.name

            try:
                option = raw_input()                                                    # Selezione del file da condividere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None

            if option is None:
                print 'Please select an option'
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    print "A number is required"
                else:
                    for idx, file in enumerate(self.files_list):                        # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            print "Adding file " + file.name
                            msg = 'ADDF' + self.session_id + file.md5 + file.name.ljust(100)
                            print 'Share message: ' + msg

                            response_message = None
                            try:
                                self.directory.send(msg)                                # Richeista di aggiunta del file alla directory, deve contenere session id, md5 e nome del file
                                print 'Message sent, waiting for response...'

                                response_message = self.directory.recv(7)               # Risposta della directory, deve contenere AADD ed il numero di copie del file già condivise
                                print 'Directory responded: ' + response_message
                            except socket.error, msg:
                                print 'Socket Error: ' + str(msg)
                            except Exception as e:
                                print 'Error: ' + e.message
                            else:
                                if response_message is None:
                                    print 'No response from directory.'
                                else:
                                    print "Copies inside the directory: " + response_message[-3:]   # Copie del file nella directory

                    if not found:
                        print 'Option not available'

    def remove(self):
        """
        Rimuove un file condiviso nella directory
        """

        found = False
        while not found:
            print "\nSelect a file to remove ('c' to cancel):"
            for idx, file in enumerate(self.files_list):
                print str(idx) + ": " + file.name
            try:
                option = raw_input()                                                    # Selezione del file da rimuovere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None
            except Exception:
                option = None

            if option is None:
                print 'Please select an option'
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    print "A number is required"
                else:
                    for idx, file in enumerate(self.files_list):                        # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            print "Removing file " + file.name
                            msg = 'DELF' + self.session_id + file.md5
                            print 'Delete message: ' + msg

                            response_message = None
                            try:
                                self.directory.send(msg)                                # Richiesta di rimozione del file dalla directory, deve contenere session id e md5
                                print 'Message sent, waiting for response...'

                                response_message = self.directory.recv(7)               # Risposta della directory, deve contenere ADEL e il numero di copie rimanenti
                                print 'Directory responded: ' + response_message
                            except socket.error, msg:
                                print 'Socket Error: ' + str(msg)
                            except Exception as e:
                                print 'Error: ' + e.message
                            else:
                                if response_message[-3:] == '999':                                  # Il file selezionato nella directory
                                    print "The file you chose doesn't exist in the directory"
                                else:
                                    print "Copies left in the directory: "+response_message[-3:]    # Numero di copie rimanenti

                    if not found:
                            print 'Option not available'

    def search(self):
        """
        Esegue la ricerca di una parola tra i file condivisi nella directory.
        Dai risultati della ricerca sarà possibile scaricare il file.
        Inserendo il termine '*' si richiedono tutti i file disponibili
        """
        print 'Insert search term:'
        try:
            term = raw_input()                                                          # Inserimento del parametro di ricerca
        except SyntaxError:
            term = None
        if term is None:
            print 'Please select an option'
        else:
            print "Searching files that match: " + term

            msg = 'FIND' + self.session_id + term.ljust(20)
            print 'Find message: ' + msg
            response_message = None
            try:
                self.directory.send(msg)                                                # Richeista di ricerca, deve contenere il session id ed il paramentro di ricerca (20 caratteri)
                print 'Message sent, waiting for response...'

                response_message = self.directory.recv(4)                               # Risposta della directory, deve contenere AFIN seguito dal numero di identificativi md5
                                                                                        # disponibili e dalla lista di file e peer che li hanno condivisi
                print 'Directory responded: ' + response_message
            except socket.error, msg:
                print 'Socket Error: ' + str(msg)
            except Exception as e:
                print 'Error: ' + e.message

            if not response_message == 'AFIN':
                print 'Error: unknown response from directory.\n'
            else:
                idmd5 = None
                try:
                    idmd5 = self.directory.recv(3)                                      # Numero di identificativi md5
                except socket.error as e:
                    print 'Socket Error: ' + e.message
                except Exception as e:
                    print 'Error: ' + e.message

                if idmd5 is None:
                    print 'Error: idmd5 is blank'
                else:
                    try:
                        idmd5 = int(idmd5)
                    except ValueError:
                        print "idmd5 is not a number"
                    else:
                        if idmd5 == 0:
                            print "No results found for search term: " + term
                        elif idmd5 > 0:  # At least one result
                            available_files = []

                            try:
                                for idx in range(0, idmd5):                             # Per ogni identificativo diverso si ricevono:
                                                                                        # md5, nome del file, numero di copie, elenco dei peer che l'hanno condiviso

                                    file_i_md5 = self.directory.recv(32)                # md5 dell'i-esimo file (32 caratteri)
                                    file_i_name = self.directory.recv(100).strip()      # nome dell'i-esimo file (100 caratteri compresi spazi)
                                    file_i_copies = self.directory.recv(3)              # numero di copie dell'i-esimo file (3 caratteri)
                                    file_owners = []
                                    for copy in range(0, int(file_i_copies)):                                   # dati del j-esimo peer che ha condiviso l'i-esimo file
                                        owner_j_ipv4 = self.directory.recv(16).replace("|", "")                 # indirizzo ipv4 del j-esimo peer
                                        owner_j_ipv6 = self.directory.recv(39)                                  # indirizzo ipv6 del j-esimo peer
                                        owner_j_port = self.directory.recv(5)                                   # porta del j-esimo peer

                                        file_owners.append(Owner(owner_j_ipv4, owner_j_ipv6, owner_j_port))

                                    available_files.append(SharedFile(file_i_name, file_i_md5, file_owners))

                            except socket.error, msg:
                                print 'Socket Error: ' + str(msg)
                            except Exception as e:
                                print 'Error: ' + e.message

                            if len(available_files) == 0:
                                print "No results found for search term: " + term
                            else:
                                print "Select a file to download ('c' to cancel): "
                                for idx, file in enumerate(available_files):            # visualizza i risultati della ricerca
                                    print str(idx) + ": " + file.name

                                selected_file = None
                                while selected_file is None:
                                    try:
                                        option = raw_input()                            # Selezione del file da scaricare
                                    except SyntaxError:
                                        option = None

                                    if option is None:
                                        print 'Please select an option'
                                    elif option == 'c':
                                        return
                                    else:
                                        try:
                                            selected_file = int(option)
                                        except ValueError:
                                            print "A number is required"

                                file_to_download = available_files[selected_file]       # Recupero del file selezionato dalla lista dei risultati

                                print "Select a peer ('c' to cancel): "
                                for idx, file in enumerate(available_files):            # Visualizzazione la lista dei peer da cui è possibile scaricarlo
                                    if selected_file == idx:
                                        for idx2, owner in enumerate(file.owners):
                                            print str(idx2) + ": " + owner.ipv4 + " | " + owner.ipv6 + " | " + owner.port

                                selected_peer = None
                                while selected_peer is None:
                                    try:
                                        option = raw_input()                            # Selezione di un peer da cui scaricare il file
                                    except SyntaxError:
                                        option = None

                                    if option is None:
                                        print 'Please select an option'
                                    elif option == 'c':
                                        return
                                    else:
                                        try:
                                            selected_peer = int(option)
                                        except ValueError:
                                            print "A number is required"

                                for idx2, owner in enumerate(file_to_download.owners):  # Download del file selezionato
                                    if selected_peer == idx2:
                                        print "Downloading file from: " + owner.ipv4 + " | " + owner.ipv6 + " " + owner.port
                                        Download.get_file(self.session_id, owner.ipv4, owner.ipv6, owner.port, file_to_download, self.directory)
                        else:
                            print "Unknown error, check your code!"
