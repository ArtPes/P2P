# coding=utf-8
import socket
import hashlib
import Connection
import helpers


def recvall(socket, chunk_size):
    """
    Legge dalla socket un certo numero di byte, evitando letture inferiori alla dimensione specificata

    :param socket: socket per le comunicazioni
    :type socket: object
    :param chunk_size: lunghezza (numero di byte) di una parte di file
    :type chunk_size: int
    :return: dati letti dalla socket
    :rtype: bytearray
    """

    data = socket.recv(chunk_size)  # Lettura di chunk_size byte dalla socket
    actual_length = len(data)

    # Se sono stati letti meno byte di chunk_size continua la lettura finchè non si raggiunge la dimensione specificata
    while actual_length < chunk_size:
        new_data = socket.recv(chunk_size - actual_length)
        actual_length += len(new_data)
        data += new_data

    return data


def get_file(session_id, host_ipv4, host_ipv6, host_port, file, directory):
    """
    Effettua il download di un file da un altro peer

    :param session_id: id sessione corrente assegnato dalla directory
    :type session_id: str
    :param host_ipv4: indirizzo ipv4 del peer da cui scaricare il file
    :type host_ipv4: str
    :param host_ipv6: indirizzo ipv6 del peer da cui scaricare il file
    :type host_ipv6: str
    :param host_port: porta del peer da cui scaricare il file
    :type host_port: str
    :param file: file da scaricare
    :type file: file
    :param directory: socket verso la directory (per la segnalazione del download)
    :type directory: object
    """

    c = Connection.Connection(host_ipv4, host_ipv6, host_port)                      # Inizializzazione della connessione verso il peer
    c.connect()
    download = c.socket

    msg = 'RETR' + file.md5
    print 'Download Message: ' + msg
    try:
        download.send(msg)                                                          # Richiesta di download al peer
        print 'Message sent, waiting for response...'
        response_message = download.recv(10)                                        # Risposta del peer, deve contenere il codice ARET seguito dalle parti del file
    except socket.error as e:
        print 'Error: ' + e.message
    except Exception as e:
        print 'Error: ' + e.message
    else:
        if response_message[:4] == 'ARET':
            n_chunks = response_message[4:10]                                       # Numero di parti del file da scaricare
            #tmp = 0

            filename = file.name
            fout = open('received/' + filename, "wb")                               # Apertura di un nuovo file in write byte mode (sovrascrive se già esistente)

            n_chunks = int(str(n_chunks).lstrip('0'))                               # Rimozione gli 0 dal numero di parti e converte in intero

            for i in range(0, n_chunks):
                if i == 0:
                    print 'Download started...'

                helpers.update_progress(i, n_chunks, 'Downloading ' + fout.name)    # Stampa a video del progresso del download

                try:
                    chunk_length = recvall(download, 5)                             # Ricezione dal peer la lunghezza della parte di file
                    data = recvall(download, int(chunk_length))                     # Ricezione dal peer la parte del file
                    fout.write(data)                                                # Scrittura della parte su file
                except socket.error as e:
                    print 'Socket Error: ' + e.message
                    break
                except IOError as e:
                    print 'IOError: ' + e.message
                    break
                except Exception as e:
                    print 'Error: ' + e.message
                    break
            fout.close()                                                            # Chiusura file a scrittura ultimata
            print '\nDownload completed'

            warns_directory(session_id, file.md5, directory)                        # Invocazione del metododo che segnala il download alla directory
            print 'Checking file integrity...'
            downloaded_md5 = helpers.hashfile(open(fout.name, 'rb'), hashlib.md5()) # Controllo dell'integrità del file appena scarcato tramite md5
            if file.md5 == downloaded_md5:
                print 'The downloaded file is intact'
            else:
                print 'Something is wrong. Check the downloaded file'
        else:
            print 'Error: unknown response from directory.\n'


def warns_directory(session_id, file_md5, directory):
    """
    Notifica il download alla directory

    :param session_id: id sessione corrente assegnato dalla directory
    :type session_id: str
    :param file_md5: hash md5 del
    :type file_md5:
    :param directory:
    :type directory:
    """

    cmd = 'DREG' + session_id + file_md5
    try:
        directory.sendall(cmd)                                                      # Notifica del download alla directory
        print 'Message sent, waiting for response...'
        response_message = directory.recv(9)                                        # Risposta della directory, deve contenere il codice ADRE seguito dal numero totale di download
        print 'Directory responded: ' + response_message
    except socket.error as e:
        print 'Socket Error: ' + e.message
    except Exception as e:
        print 'Error: ' + e.message

    num_down = int(response_message[-5:])
    if response_message[0:4] == 'ADRE' and isinstance(num_down, int):
        print 'Other peers downloaded ' + str(num_down) + ' copies of the same file'
    else:
        print 'Error: unknown response from directory.\n'



