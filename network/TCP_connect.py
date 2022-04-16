import datetime
import socket
import threading
import select
import time

class BSKServer(threading.Thread):

    def __init__(self, self_ip, self_port):

        threading.Thread.__init__(self)
        self.is_running = True
        self.self_ip = self_ip
        self.self_port = self_port

    def run(self):

        print("Server starting")

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Connect the socket to the port where the server is listening
        self.self_address = (self.self_ip, self.self_port)
        self.sock.bind(('', self.self_port))
        self.sock.listen(5)


        # Select loop for listen
        while self.is_running:
            self.conn, self.target_address = self.sock.accept()

            print("con to addr", self.target_address)

            self.conn.send("asddd".encode())

            self.conn.close()



class BSKClient(threading.Thread):

    def __init__(self, target_host, target_port):
        threading.Thread.__init__(self)
        self.host = target_host
        self.target_port = target_port
        self.running = 1

    def run(self):

        print("Client starting")

        # Select loop for listen
        while self.running:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.target_port))
            message = self.sock.recv(16).decode()
            if message:
                print("Recieved: " + message)

            self.sock.close()

    def kill(self):
        self.running = 0


