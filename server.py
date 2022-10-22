import socket, threading, os, time
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

orders = []

users = {}
userTemplate = {
    "name": "",
    "ip": ""
}
currentID = 0


def handleClient(connection, addr, userID):
    global users, userTemplate, currentID
    users[userID] = userTemplate
    users[userID]["ip"] = addr[0]

    connected = True
    while connected:
        time.sleep(0.1)
        for order in orders:
            if order[0] == "kick" and addr[0] == order[1]:
                info("{0}, {1} has been kicked".format(addr, users[userID]["name"]))
                connection.close()
                del users[userID]
                return

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
    del users[userID]

def handleCommand():
    global users, orders

    while True:
        time.sleep(0.1)

        command = input()
        if command == "exit":
            os._exit(1)
        elif command == "list":
            print(users)
        elif len(command.split()) > 1:
            if command.split()[0] == "kick":
                orders.append(["kick", command.split()[1]])

def main():
    global users, currentID

    while True:
        time.sleep(0.1)

        if len(users) < currentID:
            currentID = 0


def startServer():
    inputThread = threading.Thread(target = handleCommand)
    inputThread.start()

    mainThread = threading.Thread(target = main)
    mainThread.start()

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


