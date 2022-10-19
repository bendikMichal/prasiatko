from faulthandler import cancel_dump_traceback_later
import pygame, sys
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

for i in range(32):
    angle = 6.28 / 32 * i
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

player_list = [
    {
    "name" : "robko",
    "placed" : [],
    "cards_owned" : 0
    }, 
    {
    "name" : "timco",
    "placed" : [],
    "cards_owned" : 0
    }
]
player_id = 0
player_temlate = {
    "name" : "",
    "placed" : []
}

timeout = 0

main = True
while main:
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
    if keys[pygame.K_n] and timeout <= 0 and len(player_list[player_id]["placed"]) > 0:
        timeout = 60
        player_list[player_id]["placed"] = []
        player_id += 1
        if player_id >= len(player_list):
            player_id = 0

    Window.fill((250, 240, 240))


    for card in card_collection:
        radiusEx = 0
        if abs(card["angle"] - mouse_angle) < pi / 32:
            radiusEx = 40
            if mousepressed:
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
                    
                         
                        
        if card["hidden"] or card["owner"] == player_list[player_id]["name"]:
            blitCard(Window, cards_img, [card["x"], card["y"]], [center[0] - card_size[0] / 2 + cos(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"], center[1] - card_size[1] / 2 - sin(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"]], card_size, card["angle"] / 6.28 * 360 - 90, card["hidden"])

    for card in placed_cards:
        radiusEx = 0
        blitCard(Window, cards_img, [card["x"], card["y"]], [center[0] - card_size[0] / 2 + cos(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"], center[1] - card_size[1] / 2 - sin(card["angle"]) * (radius + radiusEx) * card["pos_multiplier"]], card_size, card["angle"] / 6.28 * 360 - 90, card["hidden"])
        

    if hidden_cards_num <= 0:
        winner = " "
        for player in player_list:
            if player["cards_owned"] <= 0:
                winner = player["name"]
        
        if winner != " ":
            text = font.render(winner + ' has won!', False, (0, 0, 0))
            Window.blit(text, (0, 0))
            

    pygame.display.update()

pygame.quit()
sys.exit()
