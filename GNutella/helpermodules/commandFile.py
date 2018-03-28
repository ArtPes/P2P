# coding=utf-8
import random, string, socket, errno, hashlib
from helpermodules.output_monitor import *
from helpermodules.connection import Connection

import config

my_ipv4 = config.CONFIG['my_ipv4']
my_ipv6 = config.CONFIG['my_ipv6']
my_port = config.CONFIG['my_port']
partialIpv4 = config.CONFIG['partialIpv4']
partialIpv6 = config.CONFIG['partialIpv6']
'''
my_ipv4 = "172.016.004.003"
my_ipv6 = "fc00:0000:0000:0000:0000:0000:0004:0003"
my_port = "06000"
partialIpv4 = "172.016."
partialIpv6 = "fc00:0000:0000:0000:0000:0000:"
'''

# TTL = "02"

def add_neighbor(output_lock, db):
    group_number = None
    output(output_lock, 'Insert group number:')

    while group_number is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert group number:')
        else:
            try:
                group_number = int(option)
            except ValueError:
                output(output_lock, "A number is required")


    member_number = None
    output(output_lock, 'Insert member number:')
    while member_number is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert group number:')
        else:
            try:
                member_number = int(option)
            except ValueError:
                output(output_lock, "A number is required")

    port_number = None
    output(output_lock, 'Insert port number:')
    while port_number is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert port number:')
        else:
            try:
                port_number = int(option)
            except ValueError:
                output(output_lock, "A number is required")

    found = db.db.neighbors.find(
        {"ipv4": partialIpv4 + str(group_number).zfill(3) + "." + str(member_number).zfill(3),
         "ipv6": partialIpv6 + str(group_number).zfill(4) + ":" + str(member_number).zfill(4),
         "port": str(port_number).zfill(5)}).count()

    if not found:
        db.db.neighbors.insert_one({"ipv4": partialIpv4 + str(group_number).zfill(3) + "." + str(member_number).zfill(3),
                                    "ipv6": partialIpv6 + str(group_number).zfill(4) + "." + str(
                                     member_number).zfill(4),
                                    "port": str(port_number).zfill(5)})
        output(output_lock,
               "Added neighbor " + "\t" + partialIpv4 + str(group_number).zfill(3) + "." + str(member_number).zfill(3) +
               "\t" + partialIpv6 + str(group_number).zfill(4) + ":" + str(member_number).zfill(4) +
               "\t " + str(port_number).zfill(5))


def set_ttl(output_lock):
    output(output_lock, "Insert new TTL:")
    new_ttl = None
    while new_ttl is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert new TTL:')
        else:
            try:
                new_ttl = int(option)
            except ValueError:
                output(output_lock, "A number is required")

    return new_ttl


def find_file(output_lock, neighbors, pktId, searchStr, TTL):

    msg = "QUER" + pktId + my_ipv4 + '|' + my_ipv6 + my_port + str(TTL).zfill(2) + searchStr

    send_near(output_lock, neighbors, msg)

    return {"pktId": pktId, "queryStr": searchStr}


def find_peers(output_lock, neighbors, TTL):
    pktId = id_generator(16)

    msg = "NEAR" + pktId + my_ipv4 + '|' + my_ipv6 + my_port + str(TTL).zfill(2)

    send_near(output_lock, neighbors, msg)


    return pktId


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def send_near(output_lock, neighbors, msg):
    for peer in neighbors:
        # Non invio all'indirizzo da cui è arrivato il pacchetto
        # if sender is None or (peer['ipv4'] != sender and peer['ipv6'] != sender):
        try:
            output(output_lock, "\nConnecting to: " + peer['ipv4'] + "\t" + peer['ipv6'] + "\t" + peer['port'])

            c = Connection(output_lock, peer['ipv4'], peer['ipv6'],
                           peer['port'])  # Creazione connessione con un peer noto
            c.connect()
            peerSock = c.socket

            peerSock.send(msg.encode('utf-8'))

            output(output_lock, "\nMessage sent : ")
            output(output_lock,
                   msg[0:4] + "\t" + msg[4:20] + "\t" + msg[20:35] + "\t" + msg[36:75] + "\t" + msg[76:80] + "\t" + msg[
                                                                                                                    80:112])

            peerSock.close()
        except IOError as e:
            output(output_lock, 'send_near-Socket Error: ' + str(e))
        except socket.error as msg:
            output(output_lock, 'send_near-Socket Error: ' + str(msg))
            continue
        except Exception as e:
            output(output_lock, 'send_near-Error: ' + str(e))
            continue


def send_aque(output_lock, ipv4, ipv6, port, msg):
    try:
        output(output_lock, "\nConnecting to: " + ipv4 + "\t" + ipv6 + "\t" + port)

        c = Connection(output_lock, ipv4, ipv6, port)  # Creazione connessione con un peer noto
        c.connect()
        peerSock = c.socket

        peerSock.send(msg.encode('utf-8'))

        output(output_lock, "\nMessage sent: ")
        output(output_lock,
               msg[0:4] + "\t" + msg[4:20] + "\t" + msg[20:35] + "\t" + msg[36:75] + "\t" + msg[76:80] + "\t" + msg[80:112])

        peerSock.close()
    except IOError as e:
        if e.errno == errno.EPIPE:
            pass
    except socket.error as msg:
        output(output_lock, 'send_aque-Socket Error: ' + str(msg))
    except Exception as e:
        output(output_lock, 'send_aque-Error: ' + str(e))


def whatNow(output_lock, dbClient, pktId):
    while True:
        output(output_lock, "\nSelect one of the following options:")
        output(output_lock, "1: See results of current search and download")
        output(output_lock, "2: Return to Main Menu")

        int_option = None
        while int_option is None:
            try:
                option = input()
            except SyntaxError:
                option = None

            if option is None:
                output(output_lock, 'Please select an option')
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    output(output_lock, "A number is required")

            if int_option == 1:
                result = dbClient.getSearchResult(pktId)
                output(output_lock, "Search string: " + result['queryStr'])
                output(output_lock, "Available files")
                if "donors" in result:
                    for idx, file in enumerate(result['donors']):
                        idx += 1
                        output(output_lock,
                               "" + str(idx) + ": " + file['name'] + " from " + file['ipv4'] + " | " + file[
                                   'ipv6'] + " | " + file['port'])
                    try:
                        output(output_lock, "Choose the file to download:")
                        option = input()
                    except SyntaxError:
                        option = None

                    if option is None:
                        output(output_lock, 'Please select an option')
                    else:
                        try:
                            int_option = int(option)
                        except ValueError:
                            output(output_lock, "A number is required")

                    for idx, file in enumerate(result['donors']):
                        if idx == (int_option - 1):
                            output(output_lock,
                                   "Download " + file['name'] + " from " + file['ipv4'] + " | " + file['ipv6'] + " | " +
                                   file['port'])
                            get_file(output_lock, file)
                else:
                    output(output_lock, "No peer answered the query")
            elif int_option == 2:
                return 0
            else:
                output(output_lock, 'Option ' + str(int_option) + ' not available')


def recvall(socket, chunk_size):
    data = socket.recv(chunk_size)  # Lettura di chunk_size byte dalla socket
    actual_length = len(data)

    # Se sono stati letti meno byte di chunk_size continua la lettura finchè non si raggiunge la dimensione specificata
    while actual_length < chunk_size:
        new_data = socket.recv(chunk_size - actual_length)
        actual_length += len(new_data)
        data += new_data

    return data


def get_file(output_lock, host):
    c = Connection(output_lock, host['ipv4'], host['ipv6'],
                   host['port'])  # Inizializzazione della connessione verso il peer
    c.connect()
    download = c.socket

    msg = 'RETR' + host['md5']
    output(output_lock, 'Download Message: ')
    output(output_lock, msg[0:4] + "\t" + msg[4:36])

    try:
        download.send(msg.encode('utf-8'))  # Richiesta di download al peer
        output(output_lock, 'Message sent, waiting for response...')
        response_message = download.recv(
            10)  # Risposta del peer, deve contenere il codice ARET seguito dalle parti del file
    except socket.error as e:
        output(output_lock, 'get_file-Error: ' + e.message)
    except Exception as e:
        output(output_lock, 'get_file-Error: ' + e.message)
    else:
        if response_message[:4] == 'ARET':
            n_chunks = response_message[4:10]  # Numero di parti del file da scaricare
            # tmp = 0


            fout = open('fileCondivisi/' + host['name'],
                        "wb")  # Apertura di un nuovo file in write byte mode (sovrascrive se già esistente)

            n_chunks = int(str(n_chunks).lstrip('0'))  # Rimozione gli 0 dal numero di parti e converte in intero

            # dlg = wx.ProgressDialog("Download progress",
            #                         "Downlading file " + fout.name,
            #                         maximum=n_chunks,
            #                         parent=None,
            #                         style= wx.PD_AUTO_HIDE
            #                               | wx.PD_ELAPSED_TIME
            #                               | wx.DIALOG_NO_PARENT
            #                               | wx.PD_REMAINING_TIME
            #                         )

            for i in range(0, n_chunks):
                if i == 0:
                    output(output_lock, 'Download started...')

                try:
                    chunk_length = recvall(download, 5)  # Ricezione dal peer la lunghezza della parte di file
                    data = recvall(download, int(chunk_length))  # Ricezione dal peer la parte del file

                    # dlg.Update(i)
                    update_progress(output_lock, i, n_chunks,
                                    'Downloading ' + fout.name)  # Stampa a video del progresso dell'upload

                    fout.write(data)  # Scrittura della parte su file
                except socket.error as e:
                    output(output_lock, 'get_file-Socket Error: ' + e.message)
                    break
                except IOError as e:
                    output(output_lock, 'get_file-IOError: ' + e.message)
                    break
                except Exception as e:
                    output(output_lock, 'get_file-Error: ' + e.message)
                    break

            # dlg.Destroy()
            fout.close()  # Chiusura file a scrittura ultimata
            output(output_lock, '\r\nDownload completed')
            output(output_lock, 'Checking file integrity...')

            downloaded_md5 = hashfile(open(fout.name, 'rb'),
                                      hashlib.md5())  # Controllo dell'integrità del file appena scarcato tramite md5
            if host['md5'] == downloaded_md5:
                output(output_lock, 'The downloaded file is intact')
            else:
                output(output_lock, 'Something is wrong. Check the downloaded file')
        else:
            output(output_lock, 'get_file-Error: unknown response from peer.\n')


def hashfile(file, hasher, blocksize=65536):
    buf = file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file.read(blocksize)
    return hasher.hexdigest()


def viewAllQueries(output_lock, queries):
    while True:

        for idx, file in enumerate(queries):
            idx += 1

            if "donors" in file:
                output(output_lock,
                       str(idx) + ": Query string (" + file['queryStr'] + ") with " + str(len(file['donors'])) + "answers")
            else:
                output(output_lock, str(idx) + ": Query string (" + file['queryStr'] + ") with none answers")
        output(output_lock, "\nSelect one to see the peers or \"c\" to return to the Main Menu:")

        option = input()

        if option == "c":
            return 0
        else:
            try:
                int_option = int(option)
            except ValueError:
                output(output_lock, "A number is required")

            host = []
            checkPoint = False

            while checkPoint is False:
                for idx0, file in enumerate(queries):
                    if idx0 == (int_option - 1):
                        checkPoint = True
                        if 'donors' in queries[idx0]:
                            host = queries[idx0]['donors']
                        else:
                            checkPoint = False

                        for idx2, file in enumerate(host):
                            output(output_lock, "" + str(idx2 + 1) + ": " + host[idx0]['name'] + " from " + host[idx0][
                                'ipv4'] + " | " + host[idx0]['ipv6'] + " | " + host[idx0]['port'])

                        if checkPoint == True:
                            try:
                                output(output_lock, "Choose the file to download or \"c\" to step back:")
                                option = raw_input()
                            except SyntaxError:
                                option = None

                            if option == "c":
                                break
                            else:
                                try:
                                    int_option = int(option)
                                except ValueError:
                                    output(output_lock, "A number is required")
                                    checkPoint = False

                            if checkPoint == True:
                                for idx, file in enumerate(host):
                                    if idx == (int_option - 1):
                                        output(output_lock,
                                               "Download " + file['name'] + " from " + file['ipv4'] + " | " + file[
                                                   'ipv6'] + " | " + file['port'])
                                        get_file(output_lock, file)
                        else:
                            output(output_lock, "No peers answered the query")
                            break
