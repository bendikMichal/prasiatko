import socket, threading, os, time
from messager import *
from sys import platform

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)

MSG_SIZE = 128
FORTMAT = "utf-8"
DISCONNECT = "DISCONNECT"
END_TURN = "next"
KICK = "kick"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)

orders = []

users = {}
userTemplate = {
    "name": "",
    "ip": "",
    "addr": ""
}
currentID = 0


def clientListener(connection, addr, userID):
    global users, currentID

    connected = True
    while connected:
        time.sleep(0.1)

        msg = connection.recv(MSG_SIZE)
        msg = msg.decode(FORTMAT).strip()

        if msg == DISCONNECT:
            connected = False
            info("{0}, {1} has left".format(addr, users[userID]["name"]))
            connection.close()
            del users[userID]

        elif len(msg) > 0 and users[userID]["addr"] == addr[1]:
            if msg[:5] == "name:":
                users[userID]["name"] = msg[5:]
            elif msg == END_TURN:
                currentID += 1
                info("next from {0}".format(users[userID]["name"]))
            else:
                message(msg)

def handleClient(connection, addr, userID):
    global users, userTemplate, currentID, orders

    if len(users) == 0:
        users[userID] = userTemplate.copy()
        users[userID]["ip"] = addr[0]
        users[userID]["addr"] = addr[1]

    elif not userID in users:
        users[userID] = userTemplate.copy()
        users[userID]["ip"] = addr[0]
        users[userID]["addr"] = addr[1]

    listener = threading.Thread(target = clientListener, args = (connection, addr, userID))
    listener.start()

    connected = True
    while connected:
        time.sleep(0.1)

        for order in orders:
            if order[0] == "kick" and addr[0] == order[1]:
                connection.send(KICK.encode(FORTMAT))
                info("{0}, {1} has been kicked".format(addr, users[userID]["name"]))
                connected = False
                connection.close()
                orders.remove(order)


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

        if len(users) > 0:
            if max(users) < currentID:
                currentID = 0
                if not currentID in users:
                    currentID += 1


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


