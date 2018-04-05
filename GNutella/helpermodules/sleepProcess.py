from time import sleep
import sys

sys.path.append('/home/art/PycharmProjects/P2P/GNutella/dbmodules')
from dbconnection import *
#from multiprocessing import Process
import os, signal
sys.path.append('/home/art/PycharmProjects/P2P/GNutella/helpermodules')
from commandFile import *
import threading
import itertools
import time


output_lock = threading.Lock()
ttl = sys.argv[2]

dbClient = MongoConnection()


neighbors = dbClient.getNeighbors()

if sys.argv[1] == "3":
    pktId = find_peers(output_lock, neighbors, ttl)
    dbClient.insertPeersPktId(pktId)

else:
    searchStr = sys.argv[3]
    pktId = sys.argv[4]
    info = find_file(output_lock, neighbors, pktId, searchStr, ttl)
    dbClient.insertFilePktId(info)

sleep(5)
input("Press enter to exit")

if sys.argv[2] == "3":
    dbClient.finishSearchFile(sys.argv[1])
else:
    dbClient.finishSearchPeers(sys.argv[1])
