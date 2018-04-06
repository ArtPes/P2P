# coding=utf-8
from pymongo import MongoClient
import sys

sys.path.append('/home/art/PycharmProjects/P2P/GNutella/dbmodules')
from checkFiles import *
import re


class MongoConnection():
    def __init__(self, host="localhost", port=27017, db_name='gnutella', conn_type="local", username='', password=''):
        self.host = host
        self.port = port
        try:
            self.conn = MongoClient()
            self.db = self.conn[db_name]
        except:
            print("Could not connect to server")

    def refreshDB(self):
        self.db.files.drop()
        self.db.neighbors.drop()
        self.db.searchFiles.drop()
        self.db.searchPeers.drop()
        self.db.registerPktIds.drop()


    def initializeFiles(self):
        files = checktFiles()
        for file in files:
            result = None
            result2 = None
            try:
                result = self.db.files.find_one({"md5": file['md5']})
                if result is None:
                    try:
                        result2 = self.db.files.insert_one(file)
                    except:
                        print("errore query insert_one " + file)
            except:
                print("errore query find " + file)

    def getNeighbors(self, ipv4='', ipv6=''):
        cursor = self.db.neighbors.find({"ipv4": {"$ne": ipv4}, "ipv6": {"$ne": ipv6}})
        list_peers = []
        for document in cursor:
            list_peers.append({
                "ipv4": document['ipv4'],
                "ipv6": document['ipv6'],
                "port": document['port']
            })

        return list_peers

    def insertFilePktId(self, info):
        result = self.db.searchFiles.insert_one(
            {"pktId": info["pktId"], "searching": True, "queryStr": info["queryStr"]})

    def insertPeersPktId(self, pktId):
        # check = self.db.searchPeers.find({"pktId": pktId)
        result = self.db.searchPeers.insert_one({"pktId": pktId, "searching": True})

    def finishSearchFile(self, pktId):
        print("\nSearch file done.")
        result = self.db.searchFiles.update_one(
            {"pktId": pktId, "searching": True},
            {
                "$set": {
                    "searching": False
                }
            }
        )

    def finishSearchPeers(self, pktId):
        print("\nSearch peers done.")
        result = self.db.searchPeers.delete_one({"pktId": pktId, "searching": True})

    def checkPktId(self, pktId):
        # controllo se l'ID è gia stato registrato allora ritorno False, se no vine inserito nel db è ritorno True
        # TODO: constrollare che non sia uno dei pacchetti che sto cercando erroneamente tornati indietro
        cursor = self.db.registerPktIds.find()
        if cursor.count() == 1:
            register = cursor[0]['register']
            if any(pktId in s for s in register):
                return False
            else:
                register.append(pktId)
                result = self.db.registerPktIds.update(
                    {},
                    {
                        "$set": {
                            "register": register
                        }
                    }
                )
        else:
            result = self.db.registerPktIds.insert_one({"register": [pktId]})
        return True

    def getMatchedFiles(self, queryStr):
        regx = re.compile(queryStr, re.IGNORECASE)
        cursor = self.db.files.find({"name": {'$in': [regx]}})
        listMatched = []
        for document in cursor:
            listMatched.append({
                "name": document['name'],
                "md5": document['md5']
            })
        return listMatched

    def handleQueryAck(self, receivedMsg):
        pktId = receivedMsg[:16]
        result = self.db.searchFiles.update_one(
            {"pktId": pktId, "searching": True},
            {
                "$push": {
                    "donors": {"ipv4": receivedMsg[16:31], "ipv6": receivedMsg[32:71],
                               "port": str(int(receivedMsg[71:76])), "md5": receivedMsg[76:108],
                               "name": receivedMsg[108:].strip(" ")}
                }
            }
        )

    def handleNearAck(self, receivedMsg):  # aggiunta neighbors
        pktId = receivedMsg[:16]
        cursor = self.db.searchPeers.find({"pktId": pktId, "searching": True})
        neighbors = self.db.neighbors.find(
            {"ipv4": receivedMsg[16:31], "ipv6": receivedMsg[32:71], "port": str(int(receivedMsg[71:76])).zfill(4)})
        if cursor.count() == 1 and neighbors.count() == 0:  # check se il neighbor non è presente nel db
            result = self.db.neighbors.insert_one(
                {"ipv4": receivedMsg[16:31], "ipv6": receivedMsg[32:71], "port": str(int(receivedMsg[71:76])).zfill(4)})

    def getFile(self, md5Remoto):
        cursor = self.db.files.find_one({"md5": md5Remoto})
        return cursor

    def getSearchResult(self, pktId):
        cursor = self.db.searchFiles.find_one({"pktId": pktId})
        return cursor

    def getAllQueries(self):
        cursor = self.db.searchFiles.find()
        return list(cursor)
