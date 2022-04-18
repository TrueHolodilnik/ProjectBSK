from tkinter import *
from network.TCP_connect import *
from tkinter import messagebox
import ctypes

class AppGUI():

    address_server = ''
    address_client = None
    port_server = ''
    port_client = None
    is_quit = False
    is_msg_quit = False
    to_send = False

    def __init__(self):
        self.window = Tk()
        self.window.title("ProjectBSK")

        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        self.window.geometry('300x200-'+str(int(self.screen_width/2))+'+'+str(int(self.screen_height/2)))

        B = Button(self.window, text="Connect", command=self.startConn).grid(row=0, column=3)
        B = Button(self.window, text="Quit", command=self.quitApp).grid(row=1, column=3)

        Label(self.window, text="Enter self ip").grid(row=0)
        Label(self.window, text="Enter self port").grid(row=1)
        Label(self.window, text="Enter target ip").grid(row=2)
        Label(self.window, text="Enter target port").grid(row=3)

        self.e1 = Entry(self.window)
        self.e2 = Entry(self.window)
        self.e3 = Entry(self.window)
        self.e4 = Entry(self.window)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)

        while not self.is_quit:
            self.address_client = self.e1.get()
            self.port_client = self.e2.get()
            self.address_server = self.e3.get()
            self.port_server = self.e4.get()
            self.window.update()

    def toSend(self):
        self.to_send = True

    def startConn(self):
        self.address_client = self.e1.get()
        self.port_client = self.e2.get()
        if not (self.address_server or self.port_server or self.address_client or self.port_client):
            messagebox.showerror("Warning", "Please enter correct data")
            return

        self.server = BSKServer(self.address_server, int(self.port_server))
        self.client = BSKClient(self.address_client, int(self.port_client))
        self.server.start()
        self.client.start()

        self.window.destroy()
        self.window = Tk()
        self.window.title("ProjectBSK Messenger")
        self.window.geometry('300x200-' + str(int(self.screen_width / 2)) + '+' + str(int(self.screen_height / 2)))
        B = Button(self.window, text="Quit", command=self.quitApp).grid(row=1, column=3)
        B = Button(self.window, text="Send", command=self.toSend).grid(row=0, column=3)
        T = Text(self.window, height = 11, width = 11)
        T.grid(row=2, column=0)
        self.e1 = Entry(self.window)
        self.e1.grid(row=0, column=0)

        while not self.is_quit:
            msg = self.e1.get()
            if msg and self.to_send:
                self.server.sendMsg(msg)
                self.to_send = False
            msg = self.client.getMsgToShow()
            if msg:
                msg = msg + '\n'
                T.insert(END, msg)
            self.window.update()

        self.server.kill()
        self.client.kill()
        self.window.destroy()

    def quitApp(self):
        self.is_quit = True


