# coding=utf-8
'''
Created by:
-Arturo Pesaro
-Luca Padovan
-Daniele Lovato
'''
from modules import Peer
import sys
from modules import PeerServer
import time
from modules import config


# main
# Inizializzazione del peer
# configurazione iniziale

print(r"""
          _____                    _____                    _____                    _____                _____                    _____                    _____          
         /\    \                  /\    \                  /\    \                  /\    \              /\    \                  /\    \                  /\    \         
        /::\____\                /::\    \                /::\    \                /::\    \            /::\    \                /::\    \                /::\    \        
       /::::|   |               /::::\    \              /::::\    \              /::::\    \           \:::\    \              /::::\    \              /::::\    \       
      /:::::|   |              /::::::\    \            /::::::\    \            /::::::\    \           \:::\    \            /::::::\    \            /::::::\    \      
     /::::::|   |             /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \           \:::\    \          /:::/\:::\    \          /:::/\:::\    \     
    /:::/|::|   |            /:::/__\:::\    \        /:::/__\:::\    \        /:::/__\:::\    \           \:::\    \        /:::/__\:::\    \        /:::/__\:::\    \    
   /:::/ |::|   |           /::::\   \:::\    \      /::::\   \:::\    \       \:::\   \:::\    \          /::::\    \      /::::\   \:::\    \      /::::\   \:::\    \   
  /:::/  |::|   | _____    /::::::\   \:::\    \    /::::::\   \:::\    \    ___\:::\   \:::\    \        /::::::\    \    /::::::\   \:::\    \    /::::::\   \:::\    \  
 /:::/   |::|   |/\    \  /:::/\:::\   \:::\    \  /:::/\:::\   \:::\____\  /\   \:::\   \:::\    \      /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/\:::\   \:::\____\ 
/:: /    |::|   /::\____\/:::/  \:::\   \:::\____\/:::/  \:::\   \:::|    |/::\   \:::\   \:::\____\    /:::/  \:::\____\/:::/__\:::\   \:::\____\/:::/  \:::\   \:::|    |
\::/    /|::|  /:::/    /\::/    \:::\  /:::/    /\::/    \:::\  /:::|____|\:::\   \:::\   \::/    /   /:::/    \::/    /\:::\   \:::\   \::/    /\::/   |::::\  /:::|____|
 \/____/ |::| /:::/    /  \/____/ \:::\/:::/    /  \/_____/\:::\/:::/    /  \:::\   \:::\   \/____/   /:::/    / \/____/  \:::\   \:::\   \/____/  \/____|:::::\/:::/    / 
         |::|/:::/    /            \::::::/    /            \::::::/    /    \:::\   \:::\    \      /:::/    /            \:::\   \:::\    \            |:::::::::/    /  
         |::::::/    /              \::::/    /              \::::/    /      \:::\   \:::\____\    /:::/    /              \:::\   \:::\____\           |::|\::::/    /   
         |:::::/    /               /:::/    /                \::/____/        \:::\  /:::/    /    \::/    /                \:::\   \::/    /           |::| \::/____/    
         |::::/    /               /:::/    /                  ~~               \:::\/:::/    /      \/____/                  \:::\   \/____/            |::|  ~|          
         /:::/    /               /:::/    /                                     \::::::/    /                                 \:::\    \                |::|   |          
        /:::/    /               /:::/    /                                       \::::/    /                                   \:::\____\               \::|   |          
        \::/    /                \::/    /                                         \::/    /                                     \::/    /                \:|   |          
         \/____/                  \/____/                                           \/____/                                       \/____/                  \|___|          
                                                                                                                                                                           


                """)

# port number
if config.CONFIG['my_port'] == "":
    print("Insert a port number for this device... ( Ex. 06000 MUST BE 5 char )")
    config.CONFIG['my_port'] = input()
# set ipv4 for this machine
if config.CONFIG['my_ipv4'] == "":
    print("Insert IPv4 Address for this device ( Ex: 172.016.00X.00Y ) ")
    config.CONFIG['my_ipv4'] = input()
# set ipv6 for this machine
if config.CONFIG['my_ipv6'] == "":
    print("Insert IPv6 Address for this device ( Ex: fc00:0000:0000:0000:0000:0000:000X:000Y )")
    config.CONFIG['my_ipv6'] = input()
# set ipv4 for directory
if config.CONFIG['dir_ipv4'] == "":
    print("Insert IPv4 Address for directory ( Ex: 172.016.00X.00Y )")
    config.CONFIG['my_ipv4'] = input()
# set ipv6 for directory
if config.CONFIG['dir_ipv4'] == "":
    print("Insert IPv6 Address for directory ( Ex: fc00:0000:0000:0000:0000:0000:000X:000Y )")
    config.CONFIG['my_ipv6'] = input()

print("Configuration is:\n\tMy IPv4: %s\n\tMy IPv6: %s\n\tMy Port: %s\n\tDirectory IPv4: %s\n\tDirectory IPv6: %s\n\n" %
                                    (config.CONFIG['my_ipv4'],
                                     config.CONFIG['my_ipv6'],
                                     config.CONFIG['my_port'],
                                     config.CONFIG['dir_ipv4'],
                                     config.CONFIG['dir_ipv6']))
# inizializzo il peer
p = Peer.Peer(port)

while p.session_id is None:
    print ('Select one of the following options (\'e\' to exit):')
    print ('1: Log In')
    int_option = None
    while int_option is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            print ('Please select an option')
        elif option == 'e':
            print ('Bye bye')
            sys.exit()          # Interrompo l'esecuzione
        else:
            try:
                int_option = int(option)
            except ValueError:
                print("A number is required")

    if int_option != 1:
        print('Option ' + str(option) + ' not available')
    else:
        p.login()           # Effettua il login

        if p.session_id is not None:
            # Inizializzazione del server multithread che risponde alle richieste di download
            peerserver = PeerServer.PeerServer(p.my_ipv4, p.my_ipv6, p.my_port, p.files_list)
            peerserver.start()
        else:
            break
        time.sleep(2) # senza timeout scritte vengono stampate male
        while p.session_id is not None:     # Utente loggato
            print ("\nSelect one of the following options:")
            print ("1: Add File")
            print ("2: Remove File")
            print ("3: Search File")
            print ("4: LogOut")

            int_option = None
            while int_option is None:
                try:
                    option = input()    # Input da tastiera
                except SyntaxError:
                    option = None

                if option is None:
                    print ('Please select an option')
                else:
                    try:
                        int_option = int(option)
                    except ValueError:
                        print ("A number is required")

            if int_option == 1:
                p.share()           # Aggiunta di un file alla directory
            elif int_option == 2:
                p.remove()          # Rimozione di un file dalla directory
            elif int_option == 3:
                p.search()          # Ricerca ed eventuale download di un file
            elif int_option == 4:
                p.logout()          # Logout
                peerserver.stop()   # Terminazione del server multithread che risponde alle richieste di download
                sys.exit()          # Interrompo l'esecuzione
            else:
                print ('Option ' + str(int_option) + ' not available')


