import threading, os, signal

from dbmodules.dbconnection import MongoConnection
from helpermodules.commandFile import *
from helpermodules.output_monitor import output
import subprocess

output_lock = threading.Lock()
#dbname = input('Inserisci nome db:')
#db = MongoConnection('localhost', 27017, dbname)
db = MongoConnection()
db.initializeFiles()
counterProcesses = []

proc = subprocess.Popen(args=["gnome-terminal", "--command=python3 server/server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=os.setpgrp)

#proc = subprocess.Popen(args=["xfce4-terminal", "-e", "bash -c 'python3 server/server.py;bash'"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=os.setpgrp)

counterProcesses.append(proc)
ttl="02"

while True:
    output(output_lock, "\nSelect one of the following options:")
    output(output_lock, "1: Add neighbor")
    output(output_lock, "2: Find File")
    output(output_lock, "3: Find Peers")
    output(output_lock, "4: List of queries")
    output(output_lock, "5: Exit")
    output(output_lock, '6: Show all neighbors')
    output(output_lock, '7: Remove neighbor')

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
            else:
                if int_option == 1:
                    add_neighbor(output_lock, db)

                elif int_option == 2:

                    output(output_lock, "Insert the search string...")
                    searchStr = input()
                    pktId = id_generator(16)
                    command = "helpermodules/sleepProcess.py"
                    counterProcesses.append(subprocess.Popen(args=["gnome-terminal", "--command=python3 " + command + " " + str(int_option)+ " " + str(ttl)+ " " + searchStr + " " + str(pktId)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=os.setpgrp))
                    #counterProcesses.append(subprocess.Popen(["xfce4-terminal", "-e", "bash -c '" + command + " " + str(int_option) + " " + str(ttl) + " " + searchStr + " " + str(pktId) + ";bash'"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=os.setpgrp))

                    whatNow(output_lock, db, pktId)

                elif int_option == 3:
                    command = "helpermodules/sleepProcess.py"
                    counterProcesses.append(subprocess.Popen(args=["gnome-terminal", "--command=python3 " + command + " " + str(int_option) + " " + str(ttl)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=os.setpgrp))


                elif int_option == 4:
                    queries = db.getAllQueries()
                    viewAllQueries(output_lock, queries)
                elif int_option == 5:
                    db.db.files.drop()
                    db.db.searchFiles.drop()
                    db.db.searchPeers.drop()
                    #s.stop()
                    for p in counterProcesses:
                        os.killpg(p.pid, signal.SIGTERM)
                    os._exit(0)
                elif int_option == 6:
                    list_nb = db.getNeighbors()
                    if len(list_nb) == 0:
                        output(output_lock, 'There are no neighbors.')
                    else:
                        for n in range(0, len(list_nb)):
                            output(output_lock, str(n + 1) + ':\t Ipv4 ' + list_nb[n]['ipv4'] + ', Ipv6 ' + list_nb[n]['ipv6'] + ', Port ' + list_nb[n]['port'])
                elif int_option == 7:
                    list_nb = db.getNeighbors()
                    if len(list_nb) == 0:
                        output(output_lock, 'There are no neighbors')
                    else:
                        output(output_lock, 'Enter the number of the neighbor to be deleted:')
                        for n in range(0, len(list_nb)):
                            output(output_lock, str(n + 1) + ':\t Ipv4 ' + list_nb[n]['ipv4'] + ', Ipv6 ' + list_nb[n]['ipv6'] + ', Port ' + list_nb[n]['port'])
                        output(output_lock, str(len(list_nb) + 1) + ':\t Delete all neighbors')
                        output(output_lock, str(len(list_nb) + 2) + ':\t Return to main menu')
                        del_option = input()
                        if int(del_option) !=  len(list_nb) + 2:
                            if int(del_option) == len(list_nb) + 1:   #li cancello tutti
                                db.db.neighbors.drop()
                            else:
                                n = list_nb[int(del_option) - 1]
                                db.db.neighbors.remove({'ipv4': n['ipv4'], 'ipv6': n['ipv6'], 'port': n['port']})
                else:
                    output(output_lock, 'Option ' + str(int_option) + ' not available')
