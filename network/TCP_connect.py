import datetime
import socket
import threading
import queue
import json
import time
import os
from crypto import *

class BSKServer(threading.Thread):

    def __init__(self, self_ip, self_port):

        threading.Thread.__init__(self)
        self.is_running = True
        self.self_ip = self_ip
        self.self_port = self_port
        self.messages_to_show = queue.LifoQueue()
        self.fileToSend = None
        self.fileToSendPar = None

    def sendMsg(self, msg):
        self.messages_to_show.put(msg)

    def sendFile(self, file, par):
        print("Server file accepted to sending")
        self.fileToSend = file
        self.fileToSendPar = par



    def run(self):

        print("Server starting")

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Connect the socket to the port where the server is listening
        self.self_address = (self.self_ip, self.self_port)
        self.sock.bind((self.self_ip, self.self_port))
        self.sock.listen(5)

        while self.is_running:
            msg = self.getMsgToShow()
            if msg:
                self.conn, self.target_address = self.sock.accept()
                self.conn.send(msg.encode())
                self.conn.close()
            elif self.fileToSend:
                self.conn, self.target_address = self.sock.accept()
                print("sent marker" + self.fileToSendPar)
                self.conn.send(self.fileToSendPar.encode())
                print("file to send " + self.fileToSend)
                f = open(self.fileToSend, 'rb')
                l = f.read(1024)
                while (l):
                    print("Sending...")
                    self.conn.send(l)
                    l = f.read(1024)
                time.sleep(3)
                self.conn.send(b"DONE")
                print("Sending DONE")
                f.close()
                self.conn.close()
                self.fileToSend = None
                self.fileToSendPar = None

    def getMsgToShow(self):
        if self.messages_to_show.empty():
            return None
        return self.messages_to_show.get_nowait()

    def kill(self):
        self.is_running = False


class BSKClient(threading.Thread):

    def __init__(self, target_host, target_port):
        threading.Thread.__init__(self)
        self.host = target_host
        self.target_port = target_port
        self.running = 1
        self.messages_to_show = queue.LifoQueue()
        self.downloadsPath = None

    def getMsgToShow(self):
        if self.messages_to_show.empty():
            return None
        return self.messages_to_show.get_nowait()

    def setDownloadsPath(self, path):
        self.downloadsPath = path

    def run(self):

        print("Client starting")

        while self.running:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.target_port))
            msg = self.sock.recv(1024).decode()
            if msg:
                test = None
                try:
                    test = json.loads(msg)
                    print("JSON test acc")
                    if type(test) == int:
                        continue
                    if test["ext"]:
                        print("recieved marker:")
                        print(test)
                        f = open(self.downloadsPath + os.path.basename(test["name"]) + test["ext"], "wb")
                        l = self.sock.recv(1024)
                        while (l != b"DONE"):
                            if l:
                                f.write(l)
                            l = self.sock.recv(1024)
                        print("recieved DONE")
                        f.close()
                except ValueError as e:
                    print("JSON test failed")
                    self.messages_to_show.put(msg)
                    continue

            self.sock.close()

    def kill(self):
        self.running = 0


