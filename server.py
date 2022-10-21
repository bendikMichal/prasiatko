import socket, threading, os
from messager import *
from sys import platform

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)

MSG_SIZE = 64
FORTMAT = "utf-8"
DISCONNECT = "DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)


names = []


def handleClient(connection, addr):
    global names

    connected = True
    while connected:
        msg = connection.recv(MSG_SIZE)
        msg = msg.decode(FORTMAT).strip()

        if msg == DISCONNECT:
            connected = False
        elif len(msg) > 0:
            if msg[:5] == "name:":
                names.append(msg[5:])
            else:
                message(msg)

    info(f"{addr} has left")
    connection.close()

def handleCommand():
    command = input()
    if command == "exit":
        os._exit(1)


def startServer():
    inputThread = threading.Thread(target = handleCommand)
    inputThread.start()

    server.listen()
    while True:

        connection, addr = server.accept()

        newThread = threading.Thread(target = handleClient, args = (connection, addr))

        info(f"{addr} joined")
        newThread.start()



if platform == "linux":
    os.system("clear")
elif platform == "win32":
    os.system("cls")

info(f"server is running at {SERVER_IP}")
startServer()


