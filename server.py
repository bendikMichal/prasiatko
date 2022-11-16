import socket, threading, os, time
from messager import *
from random import *
from math import *
from sys import platform

PORT = 5151
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)

MSG_SIZE = 256
FORMAT = "utf-8"
DISCONNECT = "DISCONNECT"
END_TURN = "next"
KICK = "kick"
GO = "go"
TAKEN = "taken"
WINNER = "winner"
LOOSER = "looser"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)

orders = []

users = {}
userTemplate = {
    "name": "",
    "ip": "",
    "addr": "",
    "waiting": True
}
currentID = 0

won = False
lost = False

card_collection = []
card_angles = []
placed_cards = []
hidden_cards_num = 32

def clientListener(connection, addr, userID):
    global users, currentID, placed_cards, card_collection, hidden_cards_num

    connected = True
    while connected:
        time.sleep(0.1)

        msg = connection.recv(MSG_SIZE)
        msg = msg.decode(FORMAT).strip()

        if msg == DISCONNECT:
            connected = False
            info("{0}, {1} has left".format(addr, users[userID]["name"]))
            connection.close()
            del users[userID]

        elif len(msg) > 0:
            if msg[:5] == "name:":
                users[userID]["name"] = msg[5:]

            elif msg == END_TURN:
                currentID += 1
                users[userID]["waiting"] = True
                info("next from {0}".format(users[userID]["name"]))

            elif msg == TAKEN:
                placed_cards[-1]["owner"] = users[userID]["name"]
                placed_cards[-1]["pos_multiplier"] = 1
                #placed_cards[-1]["hidden"] = True
                card_collection.append(placed_cards[-1].copy())
                placed_cards.remove(placed_cards[-1])
                msg = ""
                info("Player " + users[userID]["name"] + " has TAKEN!")

            elif msg[:6] == "turnd:":
                turned_string = msg[6:]
                turned_string = turned_string.split(";")
                for t in turned_string:
                    for card in card_collection:
                        card_id = int(card["x"] + card["y"] * 8)
                        if t != '':
                            if card_id == int(t):
                                card["hidden"] = False
                                card["owner"] = users[userID]["name"]
                                hidden_cards_num -= 1

            elif msg[:6] == "place:":
                placed_string = msg[6:]
                placed_string = placed_string.split(";")
                for p in placed_string:
                    for card in card_collection:
                        card_id = int(card["x"] + card["y"] * 8)
                        if not p == '':
                            if int(p) == card_id:
                                card["pos_multiplier"] = 0
                                placed_cards.append(card)
                                card_collection.remove(card)

            else:
                message(msg)



def handleClient(connection, addr, userID):
    global users, userTemplate, currentID, orders, card_angles, card_collection, placed_cards, won, lost

    def message(text):
        text = (text + ' ' * (MSG_SIZE - len(text))).encode(FORMAT)
        connection.send(text)

    users[userID] = userTemplate.copy()
    users[userID]["ip"] = addr[0]
    users[userID]["addr"] = addr[1]

    listener = threading.Thread(target = clientListener, args = (connection, addr, userID))
    listener.start()

    angles_string = ""
    for a in card_angles:
        angles_string += (";" * (len(angles_string) > 0)) + str(a)[:4]

    message("cards:" + angles_string)

    connected = True
    while connected:
        time.sleep(0.1)

        if hidden_cards_num <= 0 and userID in users:
            if not won and not lost:
                owned = 0
                for card in card_collection:
                    if card["owner"] == users[userID]["name"]:
                        owned += 1
            if not won:
                if owned <= 0:
                    won = True
                    message(WINNER)
            elif not lost:
                if owned > 0 and len(users) <= 1:
                    lost = True
                    message(LOOSER)
            if owned <= 0 and hidden_cards_num <= 0:
                message(DISCONNECT)

        if len(users) > 0 and userID in users:
            if users[userID]["waiting"] and currentID == userID:
                users[userID]["waiting"] = False

                cards_owned = []
                cards_others = []
                for card in card_collection:
                    card_id = int(card["x"] + card["y"] * 8)
                    if card["owner"] == users[userID]["name"] and not card["hidden"]:
                        cards_owned.append(card_id)
                    elif card["owner"] != users[userID]["name"] and not card["hidden"]:
                        cards_others.append(card_id)

                placed_string = ""
                for p in placed_cards:
                    card_id = int(p["x"] + p["y"] * 8)
                    placed_string += (";" * (len(placed_string) > 0)) + str(card_id)

                owned_string = ""
                for o in cards_owned:
                    owned_string += (";" * (len(owned_string) > 0)) + str(o)

                others_string = ""
                for o in cards_others:
                    others_string += (";" * (len(others_string) > 0)) + str(o)

                angles_string = ""
                for a in card_angles:
                    angles_string += (";" * (len(angles_string) > 0)) + str(a)[:4]

                message("cards:" + angles_string)
                message("place:" + placed_string)
                message("owned:" + owned_string)
                message("other:" + others_string)

                message(GO)
                info(users[userID]["name"] + "'s turn")

        for order in orders:
            if order[0] == "kick" and addr[0] == order[1]:
                message(KICK)
                info("{0}, {1} has been kicked".format(addr, users[userID]["name"]))
                connected = False
                connection.close()
                orders.remove(order)


def handleCommand():
    global users, orders, socket

    while True:
        time.sleep(0.1)

        command = input()
        if command == "exit":
            server.close()
            os._exit(1)
        elif command == "list":
            print(users)
        elif len(command.split()) > 1:
            if command.split()[0] == "kick":
                orders.append(["kick", command.split()[1]])

def main():
    global users, currentID, card_collection, card_angles, placed_cards, hidden_cards_num

    all_angles = [i * (6.28 / 32) for i in range(32)]

    for i in range(32):
        angle = choice(all_angles)
        # angle = 6.28 / 32 * i
        y = floor(i / 8)
        x = i - 8 * y + 1
        card_collection.append({
            "x" : x,
            "y" : y,
            "pos_multiplier" : 1,
            "angle" : angle,
            "hidden" : True,
            "owner" : ""
        })
        all_angles.remove(angle)

    for card in card_collection:
        card_angles.append(card["angle"])

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


