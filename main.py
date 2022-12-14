
import sys, messager, time, os
from tkinter import *
from math import *

global player_list, usernames
player_list = []
usernames = []
username = ""
singleplayer = False
player_id = 0
winner = " "
looser = " "
SERVER_IP = ""
# 172.16.2.160 

no_option = True
player_temlate = {
    "name" : "",
    "placed" : [],
    "cards_owned" : 0,
    "taken" : False
}

def Exit():
    sys.exit()

def AddUser():
    if len(player_list) < 4 and singleplayer:
        name = INPUT.get()
        if not name in usernames:
            usernames.append(name)
            PLAYERS.append(Label(root, text = name, font = "Arial 8"))
            PLAYERS[-1].place(x = 10, y = 400 + len(PLAYERS) * 20)
            player_list.append({
                "name" : name,
                "placed" : [],
                "cards_owned" : 0,
                "taken" : False
            })

def SetUser():
    global username, SERVER_IP
    SERVER_IP = SERVER_IP_INPUT.get()
    username = INPUT.get()[:32]
    if len(player_list) < 1 and not singleplayer:
        if not username in usernames:
            usernames.append(username)
            player_list.append({
                "name" : username,
                "placed" : [],
                "cards_owned" : 0,
                "taken" : False
            })
    messager.info("singleplayer: " + str(singleplayer) + ", username: " + username + ", server ip: " + SERVER_IP)


def SwitchSingle():
    global singleplayer, usernames, player_list, username, PLAYERS, INPUT, root
    singleplayer = not singleplayer

    if not singleplayer:
        usernames = usernames[:1]
        player_list = player_list[:1]
        for i in range(len(PLAYERS)):
            PLAYERS[i].destroy()

        PLAYERS = []
        username = INPUT.get()[:32]

def Setup():
    global root, INPUT, PLAYERS, SERVER_IP_INPUT
    root = Tk()
    root.geometry('300x600')
    root.resizable(0, 0)

    LOGO_IMG = PhotoImage(file = "./data/logo.png")
    TITLE = Label(root, image = LOGO_IMG)
    SERVER_IP_TITLE = Label(root, text = "Server IP:", font = "Arial 8")
    USERNAME_TITLE = Label(root, text = "Username:", font = "Arial 8")
    SERVER_IP_INPUT = Entry(root)
    INPUT = Entry(root)
    PLAYERS = []
    ADD_BUTTON = Button(root, text = "Add", command = AddUser)
    SET_BUTTON = Button(root, text = "Set", command = SetUser)
    START_BUTTON = Button(root, text = "Start", command = root.destroy)
    EXIT_BUTTON = Button(root, text = "Quit", command = Exit)
    SINGLEPLAYER = Checkbutton(root, text = "SINGLEPLAYER", command = SwitchSingle)

    TITLE.place(x = 0, y = 0)
    SERVER_IP_TITLE.place(x = 10, y = 380)
    USERNAME_TITLE.place(x = 10, y = 400)
    SERVER_IP_INPUT.place(x = 80, y = 380)
    INPUT.place(x = 80, y = 400)
    SINGLEPLAYER.place(x = 10, y = 350)
    ADD_BUTTON.place(x = 240, y = 400)
    SET_BUTTON.place(x = 240, y = 440)
    START_BUTTON.place(x = 10, y = 500)
    EXIT_BUTTON.place(x = 10, y = 540)

    root.mainloop()

Setup()

card_collection = []
turned_ids = []
placed_cards = []
placed_ids = []
hidden_cards_num = 32

waiting = not singleplayer
if singleplayer:
    messager.info("singleplayer enabled")

else:
    import socket, sys, threading

    PORT = 5151
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

    try:
        messager.info("attempting to connect to server")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
    except:
        messager.info("No such server is available.")
        os._exit(1)


    def message(text):
        text = (text + ' ' * (MSG_SIZE - len(text))).encode(FORMAT)
        client.send(text)

    # message(DISCONNECT)
    message(f"name:{username}")

    def listener():
        global client, waiting, card_angles, card_collection, placed_cards, player_list, player_id, no_option, winner, looser

        while True:
            time.sleep(0.1)

            msg = client.recv(MSG_SIZE)
            msg = msg.decode(FORMAT).strip()

            if msg == KICK:
                message(DISCONNECT)
                os._exit(1)

            elif msg == WINNER:
                winner = player_list[player_id]["name"]
                message(DISCONNECT)

            elif msg == LOOSER:
                looser = player_list[player_id]["name"]
                message(DISCONNECT)

            elif msg == GO:
                waiting = False
                no_option = True
                messager.info("my TURRRN")
                player_list[player_id]["placed"] = []
                player_list[player_id]["taken"] = False

            elif msg[:6] == "cards:":
                card_angles = msg[6:]
                card_angles = card_angles.split(";")

                card_collection = []
                for i in range(32):
                    if not card_angles[i] == '':
                        angle = float(card_angles[i])
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

            elif msg[:6] == "place:":
                cards_placed = msg[6:]
                cards_placed = cards_placed.split(";")
                placed_cards = []
                for p in cards_placed:
                    for card in card_collection:
                        card_id = int(card["x"] + card["y"] * 8)
                        if not p == '':
                            if card_id == int(p):
                                card["pos_multiplier"] = 0
                                card["hidden"] = False
                                placed_cards.append(card)
                                card_collection.remove(card)

            elif msg[:6] == "owned:":
                cards_owned = msg[6:]
                cards_owned = cards_owned.split(";")
                for o in cards_owned:
                    for card in card_collection:
                        card_id = int(card["x"] + card["y"] * 8)
                        if not o == '':
                            if card_id == int(o):
                                card["owner"] = player_list[player_id]["name"]
                                card["hidden"] = False

            elif msg[:6] == "other:":
                cards_others = msg[6:]
                cards_others = cards_others.split(";")
                for o in cards_others:
                    for card in card_collection:
                        card_id = int(card["x"] + card["y"] * 8)
                        if not o == '':
                            if card_id == int(o):
                                #card_collection.remove(card)
                                card["owner"] = "1234567890abcdefghijklmnopqrstuvwxyz1234567890"
                                card["hidden"] = False


    serverListener = threading.Thread(target = listener)
    serverListener.start()


import pygame
from random import *

pygame.init()

width, height = 800, 800
Window = pygame.display.set_mode((width, height))
pygame.display.set_caption("prasiatka")
font = pygame.font.SysFont('Arial', 30)

def blitCard(Window, cards_img, card_pos, pos, card_size, angle, hidden):
    if not hidden:
        temp = cards_img.subsurface([(card_pos[0] - 1) * card_size[0], (card_pos[1]) * card_size[1], card_size[0], card_size[1]])
    else:
        temp = cards_img.subsurface([0 * card_size[0], 4 * card_size[1], card_size[0], card_size[1]])

    temp = pygame.transform.rotate(temp, angle)
    Window.blit(temp, pos)


cards_img = pygame.image.load("data/karty.png")

card_size = [77, 123]


center = [width / 2, height / 2]
radius = 250

all_angles = [i * (6.28 / 32) for i in range(32)]

if singleplayer:
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

    for i in range(32):
        for j in range(i + 1, 32):
            if card_collection[i]["angle"] > card_collection[j]["angle"]:
                temp = card_collection[i].copy()
                card_collection[i] = card_collection[j].copy()
                card_collection[j] = temp.copy()

timeout = 0
clock = pygame.time.Clock()
fps = 20

end = False
main = True
while main:
    clock.tick(fps)

    mousepressed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousepressed = True

    mouse = pygame.mouse.get_pos()
    mouse_angle = (atan2(mouse[0] - center[0], mouse[1] - center[1]) - pi / 2) % (2 * pi)

    if timeout > 0:
        timeout -= 1

    keys = pygame.key.get_pressed()

    # next player in singleplayer mode
    if keys[pygame.K_n] and timeout <= 0 and (len(player_list[player_id]["placed"]) > 0 or player_list[player_id]["taken"]) and singleplayer:
        timeout = 30
        player_list[player_id]["placed"] = []
        player_list[player_id]["taken"] = False
        player_id += 1
        if player_id >= len(player_list):
            player_id = 0
    elif keys[pygame.K_n] and timeout <= 0 and (len(player_list[player_id]["placed"]) > 0 or player_list[player_id]["taken"]) and not singleplayer and not waiting:
        turned_string = ""
        for t in turned_ids:
            turned_string += (";" * (len(turned_string) > 0)) + str(t)[:4]
        message("turnd:" + turned_string)
        turned_ids = []

        placed_string = ""
        for p in placed_ids:
            placed_string += (";" * (len(placed_string) > 0)) + str(p)[:4]
        message("place:" + placed_string)
        placed_ids = []

        if player_list[player_id]["taken"]:
            message(TAKEN)

        message(END_TURN)

        player_list[player_id]["placed"] = []
        player_list[player_id]["taken"] = False
        waiting = True

    Window.fill((250, 240, 240))

    if not singleplayer:
        hidden_cards_num = 0

    if singleplayer:
        no_option = True
    for card in card_collection:
        if not singleplayer and card["hidden"]:
            hidden_cards_num += 1

        radiusEx = 0
        if abs(card["angle"] - mouse_angle) < pi / 32:
            radiusEx = 40
            i = card["x"] + card["y"] * 8
            if mousepressed and not end and not player_list[player_id]["taken"] and not waiting:
                if card["hidden"] and len(player_list[player_id]["placed"]) == 0:
                    hidden_cards_num -= 1
                    player_list[player_id]["cards_owned"] += 1
                    card["hidden"] = not card["hidden"]
                    card["owner"] = player_list[player_id]["name"]
                    turned_ids.append(i)

                elif card["owner"] == player_list[player_id]["name"]:
                    if (len(player_list[player_id]["placed"]) == 0 and len(placed_cards) == 0):
                        card["pos_multiplier"] = 0
                        player_list[player_id]["cards_owned"] -= 1
                        placed_cards.append(card)
                        player_list[player_id]["placed"].append(card)
                        card_collection.remove(card)
                        placed_ids.append(i)

                    elif len(player_list[player_id]["placed"]) > 0:
                        if player_list[player_id]["placed"][0]["x"] == card["x"]:
                            card["pos_multiplier"] = 0
                            player_list[player_id]["cards_owned"] -= 1
                            placed_cards.append(card)
                            player_list[player_id]["placed"].append(card)
                            card_collection.remove(card)
                            placed_ids.append(i)

                    elif (placed_cards[-1]["y"] == card["y"] or placed_cards[-1]["x"] == card["x"]) and len(player_list[player_id]["placed"]) < 1:
                        card["pos_multiplier"] = 0
                        player_list[player_id]["cards_owned"] -= 1
                        placed_cards.append(card)
                        player_list[player_id]["placed"].append(card)
                        card_collection.remove(card)
                        placed_ids.append(i)

        if len(placed_cards) > 0:
            if (placed_cards[-1]["y"] == card["y"] or placed_cards[-1]["x"] == card["x"]) and card["owner"] == player_list[player_id]["name"]:
                no_option = False

        if card["hidden"] or card["owner"] == player_list[player_id]["name"]:
            blitCard(Window, cards_img, [card["x"], card["y"]], [center[0] - card_size[0] / 2 + cos(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"], center[1] - card_size[1] / 2 - sin(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"]], card_size, card["angle"] / 6.28 * 360 - 90, card["hidden"])

    # giving player a card when he has nothing to place
    if keys[pygame.K_t] and no_option and len(placed_cards) > 0 and hidden_cards_num <= 0 and len(player_list[player_id]["placed"]) <= 0 and not player_list[player_id]["taken"] and not waiting and player_list[player_id]["cards_owned"] > 0:
        print("no_option:", no_option)
        print("placed_cards:", len(placed_cards))
        print("hidden_cards_num:", hidden_cards_num)
        print("player_list[player_id][placed]:", player_list[player_id]["placed"])
        print("not player_list[player_id][taken]:", not player_list[player_id]["taken"])
        print("player_list[player_id][cards_owned]:", player_list[player_id]["cards_owned"])
        print("not waiting:", not waiting)

        placed_cards[-1]["owner"] = player_list[player_id]["name"]
        placed_cards[-1]["pos_multiplier"] = 1
        card_collection.append(placed_cards[-1].copy())
        placed_cards.remove(placed_cards[-1])
        player_list[player_id]["cards_owned"] += 1
        if len(placed_cards) > 0:
            player_list[player_id]["placed"].append(placed_cards[-1].copy())
        player_list[player_id]["taken"] = True
        no_option = False

    # displaying placed cards
    for card in placed_cards:
        radiusEx = 0
        blitCard(Window, cards_img, [card["x"], card["y"]], [center[0] - card_size[0] / 2 + cos(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"], center[1] - card_size[1] / 2 - sin(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"]], card_size, card["angle"] / 6.28 * 360 - 90, card["hidden"])


    # checking if someone has won
    if hidden_cards_num <= 0 and singleplayer:
        for player in player_list:
            if player["cards_owned"] <= 0:
                winner = player["name"]
                end = True

    if winner != " ":
        text = font.render(winner + ' has won!', False, (0, 0, 0))
        Window.blit(text, (10, 0))
    if looser != " ":
        text = font.render(looser + ' has lost!', False, (0, 0, 0))
        Window.blit(text, (10, 0))

    if not waiting:
        text = font.render(player_list[player_id]["name"] + "'s turn", False, (0, 0, 0))
    else:
        text = font.render("waiting...", False, (0, 0, 0))
    Window.blit(text, (10, height - 40))

    pygame.display.update()

pygame.quit()
if not singleplayer:
    message(DISCONNECT)
os._exit(1)
