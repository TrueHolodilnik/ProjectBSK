import datetime
import socket
import threading
import queue
import json
import time
import os

from cryptom.Encryption import Encryptor


class Connector:

    def __init__(self):

        self.__portToBind = 54321
        self.__portToConnect = 54322
        self.__encryptor = Encryptor()

        self_ip = socket.gethostbyname(socket.gethostname())
        self.__socketSender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socketReceiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socketReceiver.bind(("25.70.194.69", 54322))
        self.__socketReceiver.listen(5)
        self.__receiver = Receiver(self.__socketReceiver, self.__encryptor)
        self.__sender = Sender(self.__socketSender, self.__encryptor)
        self.__receiver.start()

        self.selfPublicKey = None
        self.targetPublicKey = None

    def __del__(self):
        self.__receiver.kill()
        return

    def createSender(self, ip):
        if self.__socketSender:
            self.__socketSender.close()

        self.__socketSender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socketSender.bind(("25.70.194.69", self.__portToBind))
        self.__socketSender.connect((ip, self.__portToConnect))

        self.__sender.setSock(self.__socketSender)

    def getEncryptor(self):
        return self.__encryptor

    def getSender(self):
        return self.__sender

    def getReciever(self):
        return self.__receiver

    def getSocketSender(self):
        return self.__socketSender

    def getSocketReciever(self):
        return self.__socketReceiver


class Receiver(threading.Thread):

    def __init__(self, socketReciver, __encryptor):

        threading.Thread.__init__(self)
        self.__encryptor = __encryptor
        self.__target_address = None
        self.__socketReceiver = socketReciver
        self.__running = True
        self.__messages_to_show = queue.LifoQueue()
        self.__fileToSend = None
        self.__fileToSendPar = None
        self.__conn = None
        self.__downloadsPath = None

    def __del__(self):
        self.kill()
        return

    def setDownloadsPath(self, path):
        self.__downloadsPath = path

    def run(self):

        msg = None
        while self.__running:
            if self.__target_address is None:
                self.__conn, self.__target_address = self.__socketReceiver.accept()
                print(self.__target_address)
            try:
                msg = self.__conn.recv(1024).decode()
            except socket.error:
                print("Socket recieving error, " + socket.error.with_traceback().strerror)
            if msg:
                msg = self.__encryptor.decryptBlock(msg)
                try:
                    test = json.loads(msg)
                    print("JSON test acc")
                    if type(test) == int:
                        continue
                    if test["ext"]:
                        print("received marker:")
                        print(test)
                        f = open(self.__downloadsPath + os.path.basename(test["name"]) + test["ext"], "wb")
                        buff = self.__conn.recv(8 * 1024)
                        while buff != b"DONE":
                            if buff:
                                f.write(buff)
                            buff = self.__conn.recv(8 * 1024)
                        print("received DONE")
                        f.close()
                except ValueError as e:
                    print("JSON test failed")
                    msg = msg + '\n'
                    self.__messages_to_show.put(msg)
                    continue

    def getMsgToShow(self):
        if self.__messages_to_show.empty():
            return None
        return self.__messages_to_show.get_nowait()

    def getAddress(self):
        return self.__target_address

    def setAddress(self, address):
        self.__target_address = address

    def kill(self):
        self.__running = False

    def getConn(self):
        return self.__conn


class Sender:

    def __init__(self, ___socketSender, __encryptor):
        self.__encryptor = __encryptor
        self.__conn = None
        self.__target_address = None
        self.__socketSender = ___socketSender
        self.__messages_to_show = queue.LifoQueue()

    def __del__(self):
        return

    def setTargetAddress(self, address):
        self.__target_address = address

    def setSock(self, _sock):
        self.__socketSender = _sock

    def sendMessage(self, msg):
        self.__socketSender.send(msg.encode())

    def sendFile(self, file):
        file_name, file_extension = os.path.splitext(file)
        filePar = json.dumps({
            "name": file_name,
            "ext": file_extension
        })
        msg = filePar.encode()
        msg = self.__encryptor.encryptBlock(msg)
        self.__socketSender.send(msg)

        f = open(file, 'rb')
        buff = f.read(8 * 1024)
        print("Sending...")
        while buff:
            self.__socketSender.send(self.__encryptor.encryptBlock(buff))
            buff = f.read(8 * 1024)

        time.sleep(3)

        self.__socketSender.send(self.__encryptor.encryptBlock(b"DONE"))
        print("Sending DONE")
        f.close()
