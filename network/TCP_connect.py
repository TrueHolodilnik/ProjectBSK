import datetime
import socket
import threading
import queue

class BSKServer(threading.Thread):

    def __init__(self, self_ip, self_port):

        threading.Thread.__init__(self)
        self.is_running = True
        self.self_ip = self_ip
        self.self_port = self_port
        self.messages_to_show = queue.LifoQueue()

    def sendMsg(self, msg):
        self.messages_to_show.put(msg)

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
            msg = self.messages_to_show.get()
            if msg:
                self.conn, self.target_address = self.sock.accept()
                self.conn.send(msg.encode())
                self.conn.close()

    def kill(self):
        self.is_running = False


class BSKClient(threading.Thread):

    def __init__(self, target_host, target_port):
        threading.Thread.__init__(self)
        self.host = target_host
        self.target_port = target_port
        self.running = 1
        self.messages_to_show = queue.LifoQueue()

    def getMsgToShow(self):
        if self.messages_to_show.empty():
            return None
        return self.messages_to_show.get_nowait()

    def run(self):

        print("Client starting")

        while self.running:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.target_port))
            msg = self.sock.recv(1024).decode()
            if msg:
                self.messages_to_show.put(msg)

            self.sock.close()

    def kill(self):
        self.running = 0


