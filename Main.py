from tkinter import *
from network.TCP_connect import *


def main():

    window = Tk()
    window.title("ProjectBSK")

    server = BSKServer('127.0.0.1', 8080)
    client = BSKClient('127.0.0.1', 8080)

    server.start()
    client.start()


    window.mainloop()


if __name__ == "__main__":
    main()