
import sys, messager
from tkinter import *

global player_list, usernames
player_list = []
usernames = []
username = ""
singleplayer = False
player_id = 0
SERVER_IP = ""
# 172.16.2.160 

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
            PLAYERS[-1].place(x = 10, y = 200 + len(PLAYERS) * 20)
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
    global singleplayer
    singleplayer = not singleplayer

def Setup():
    global root, INPUT, PLAYERS, SERVER_IP_INPUT
    root = Tk()
    root.geometry('300x600')
    root.resizable(0, 0)


    TITLE = Label(root, text = "Prasiatko", font = "Arial 20")
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

    TITLE.place(x = 10, y = 100)
    SERVER_IP_TITLE.place(x = 10, y = 180)
    USERNAME_TITLE.place(x = 10, y = 200)
    SERVER_IP_INPUT.place(x = 80, y = 180)
    INPUT.place(x = 80, y = 200)
    SINGLEPLAYER.place(x = 10, y = 150)
    ADD_BUTTON.place(x = 240, y = 200)
    SET_BUTTON.place(x = 240, y = 240)
    START_BUTTON.place(x = 10, y = 500)
    EXIT_BUTTON.place(x = 10, y = 540)

    root.mainloop()

Setup()

if singleplayer:
    messager.info("singleplayer enabled")

else:
    import socket, sys

    PORT = 5050
    ADDR = (SERVER_IP, PORT)

    MSG_SIZE = 64
    FORTMAT = "utf-8"
    DISCONNECT = "DISCONNECT"
    END_TURN = "next"

    try:
        messager.info("attempting to connect to server")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
    except:
        messager.info("No such server is available.")
        sys.exit()


    def message(text):
        text = (text + ' ' * (MSG_SIZE - len(text))).encode(FORTMAT)
        client.send(text)

    # message(DISCONNECT)
    message(f"name:{username}")


import pygame, time
from random import *
from math import *

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

card_collection = []
placed_cards = []
hidden_cards_num = 32

center = [width / 2, height / 2]
radius = 250

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
    elif keys[pygame.K_n] and timeout <= 0 and (len(player_list[player_id]["placed"]) > 0 or player_list[player_id]["taken"]) and not singleplayer:
        message(END_TURN)

    Window.fill((250, 240, 240))


    no_option = True
    for card in card_collection:
        radiusEx = 0
        if abs(card["angle"] - mouse_angle) < pi / 32:
            radiusEx = 40
            if mousepressed and not end and not player_list[player_id]["taken"]:
                if card["hidden"] and len(player_list[player_id]["placed"]) == 0:
                    hidden_cards_num -= 1
                    player_list[player_id]["cards_owned"] += 1
                    card["hidden"] = not card["hidden"]
                    card["owner"] = player_list[player_id]["name"]

                elif card["owner"] == player_list[player_id]["name"]:
                    if (len(player_list[player_id]["placed"]) == 0 and len(placed_cards) == 0):
                        card["pos_multiplier"] = 0
                        player_list[player_id]["cards_owned"] -= 1
                        placed_cards.append(card)
                        player_list[player_id]["placed"].append(card)
                        card_collection.remove(card)

                    elif len(player_list[player_id]["placed"]) > 0:
                        if player_list[player_id]["placed"][0]["x"] == card["x"]:
                            card["pos_multiplier"] = 0
                            player_list[player_id]["cards_owned"] -= 1
                            placed_cards.append(card)
                            player_list[player_id]["placed"].append(card)
                            card_collection.remove(card)

                    elif (placed_cards[-1]["y"] == card["y"] or placed_cards[-1]["x"] == card["x"]) and len(player_list[player_id]["placed"]) < 1:
                        card["pos_multiplier"] = 0
                        player_list[player_id]["cards_owned"] -= 1
                        placed_cards.append(card)
                        player_list[player_id]["placed"].append(card)
                        card_collection.remove(card)

        if len(placed_cards) > 0:
            if (placed_cards[-1]["y"] == card["y"] or placed_cards[-1]["x"] == card["x"]) and card["owner"] == player_list[player_id]["name"]:
                no_option = False

        if card["hidden"] or card["owner"] == player_list[player_id]["name"]:
            blitCard(Window, cards_img, [card["x"], card["y"]], [center[0] - card_size[0] / 2 + cos(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"], center[1] - card_size[1] / 2 - sin(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"]], card_size, card["angle"] / 6.28 * 360 - 90, card["hidden"])

    # giving player a card when he has nothing to place
    if no_option and len(placed_cards) > 0 and hidden_cards_num <= 0 and len(player_list[player_id]["placed"]) <= 0 and not player_list[player_id]["taken"]:
        placed_cards[-1]["owner"] = player_list[player_id]["name"]
        placed_cards[-1]["pos_multiplier"] = 1
        card_collection.append(placed_cards[-1])
        placed_cards.remove(placed_cards[-1])
        player_list[player_id]["cards_owned"] += 1
        if len(placed_cards) > 0:
            player_list[player_id]["placed"].append(placed_cards[-1])
        player_list[player_id]["taken"] = True

    # displaying placed cards
    for card in placed_cards:
        radiusEx = 0
        blitCard(Window, cards_img, [card["x"], card["y"]], [center[0] - card_size[0] / 2 + cos(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"], center[1] - card_size[1] / 2 - sin(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"]], card_size, card["angle"] / 6.28 * 360 - 90, card["hidden"])


    # checking if someone has won
    if hidden_cards_num <= 0:
        winner = " "
        for player in player_list:
            if player["cards_owned"] <= 0:
                winner = player["name"]
                end = True

        if winner != " ":
            text = font.render(winner + ' has won!', False, (0, 0, 0))
            Window.blit(text, (10, 0))

    text = font.render(player_list[player_id]["name"] + "'s turn'", False, (0, 0, 0))
    Window.blit(text, (10, height - 40))

    pygame.display.update()

pygame.quit()
if not singleplayer:
    message(DISCONNECT)
sys.exit()
