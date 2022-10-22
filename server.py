import socket, threading, os
from messager import *
from sys import platform

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)

MSG_SIZE = 64
FORTMAT = "utf-8"
DISCONNECT = "DISCONNECT"
END_TURN = "next"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)


users = {}
userTemplate = {
    "name": ""
}
currentID = 0


def handleClient(connection, addr, userID):
    global users, userTemplate, currentID
    users[userID] = userTemplate

    connected = True
    while connected:
        msg = connection.recv(MSG_SIZE)
        msg = msg.decode(FORTMAT).strip()

        if msg == DISCONNECT:
            connected = False
        elif len(msg) > 0 and currentID == userID:
            if msg[:5] == "name:":
                users[userID]["name"] = msg[5:]
            elif msg == END_TURN:
                currentID += 1
                info("next from {0}".format(users[userID]["name"]))
            else:
                message(msg)

    info("{0}, {1} has left".format(addr, users[userID]["name"]))
    connection.close()

def handleCommand():
    command = input()
    if command == "exit":
        os._exit(1)


def startServer():
    inputThread = threading.Thread(target = handleCommand)
    inputThread.start()

    userID = 0
    server.listen()
    while True:

        connection, addr = server.accept()

        newThread = threading.Thread(target = handleClient, args = (connection, addr, userID))

        userID += 1
        info(f"{addr} joined")
        newThread.start()



if platform == "linux":
    os.system("clear")
elif platform == "win32":
    os.system("cls")

info(f"server is running at {SERVER_IP}")
startServer()


