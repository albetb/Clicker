# -*- coding: utf-8 -*-
from logging import exception
import pygame # pip install pygame
#import time
import os

pygame.init()
GAME_VERSION = "0.0.1b"

clock = pygame.time.Clock()
fps = 10 # Frame per second

white = (255, 255, 255)
black = (0, 0, 0)
grey = (128, 128, 128)
light_grey = (224, 224, 224)
light_blue = (173, 216, 230)
grey = (128, 128, 128)
blue = (0, 100, 250)

display_width = 800
display_height = 600
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Clicker")

ASSET_DIR = os.path.join(".", "asset")
BACKGROUND_EXPLORE = os.path.join(ASSET_DIR, "background_explore.jpg")
BACKGROUND_CITY = os.path.join(ASSET_DIR, "background_city.png")
BUTTON_FOOD = os.path.join(ASSET_DIR, "buttonfood.png")
BUTTON_LARGE = os.path.join(ASSET_DIR, "button_large.png")
BUTTON_LARGE_SELECTED = os.path.join(ASSET_DIR, "button_large_selected.png")
BUTTON_LARGE_FOOD = os.path.join(ASSET_DIR, "button_large_food.png")
BUTTON_LARGE_HARVESTER = os.path.join(ASSET_DIR, "button_large_harvester.png")
BUTTON_LARGE_LUMBERER = os.path.join(ASSET_DIR, "button_large_lumberer.png")
BUTTON_ROUND_PLUS = os.path.join(ASSET_DIR, "buttonroundplus.png")
LEFT_BUTTON_MINUS = os.path.join(ASSET_DIR, "leftbuttonminus.png")
POP_TAG = os.path.join(ASSET_DIR, "poptag.png")
RIGHT_BUTTON_PLUS = os.path.join(ASSET_DIR, "rightbuttonplus.png")
TEXTBOX_FOOD = os.path.join(ASSET_DIR, "textboxfood.png")
WOOD_TAG = os.path.join(ASSET_DIR, "woodtag.png")

class Image:
    def __init__(self, path, x, y, w, h, text = "", textx = 0.5, texty = 0.5, menu = -1):
        self.path = path # Image relative path
        self.x = x # X positioning, if x ↑ image →
        self.y = y # Y positioning, if y ↑ image ↓
        self.w = w # Image width
        self.h = h # Image height
        self.text = "" # Text of image
        self.textRect = 0 # Needed to display text
        self.textx = textx # X positioning of text [0, 1], 1 is 100% right
        self.texty = texty # Y positioning of text [0, 1], 1 is 100% down
        self.menu = menu # Set in what case image is displayed, -1 everytime

        self.change(self.path)
        self.set_text(text)

    def set_text(self, text, size = 30, color = (0, 0, 0)):
        if text != "":
            font = pygame.font.Font('freesansbold.ttf', size)
            self.text = font.render(str(text), True, color)
            self.textRect = self.text.get_rect()
            avg = lambda a, l: (2 * a + l) / 2
            self.textRect.center = (avg(self.x, self.w) - (0.5 - self.textx) * self.w, avg(self.y, self.h) - (size / 6) - (0.5 - self.texty) * self.h)

    def change(self, path):
        picture = pygame.image.load(path)
        self.picture = pygame.transform.scale(picture, (self.w, self.h))

    def draw(self, menu):
        if self.menu < 0 or self.menu == menu:
            display.blit(self.picture, (self.x, self.y))
            if self.text != "":
                display.blit(self.text, self.textRect)

    def collide(self, p, menu):
        return all([self.x <= p[0], p[0] <= self.x + self.w, self.y <= p[1], p[1] <= self.y + self.h, self.menu < 0 or menu == self.menu])

production = lambda pop: 0.05 * (pop ** 1.05) * (1 + (pop // 10) * 0.5)
population_cost = lambda pop: round(((pop + 1) * 50) ** 1.1)
food_click = lambda pop: 10 + pop ** 1.5

def display_number(num, precision = "low"):
    if num < 10 ** 3 and (precision == "low" or num == round(num)):
        return f"{int(round(num, 0))}"
    elif num < 10 ** 3 and precision == "high":
        return f"{round(num, 2)}"
    elif num < 10 ** 6:
        return f"{round(num / (10 ** 3), 2)} k"
    elif num < 10 ** 9:
        return f"{round(num / (10 ** 6), 2)} M"
    elif num < 10 ** 12:
        return f"{round(num / (10 ** 9), 2)} B"
    elif num < 10 ** 15:
        return f"{round(num / (10 ** 12), 2)} T"

def autominer(food, wood, pop, harvester, lumber):
    return round(food + production(harvester) - pop * 0.005, 3), round(wood + 0.8 * production(lumber), 3)
 
def text(text, color, x, y, fsize):
    font = pygame.font.Font('freesansbold.ttf', fsize)
    text = font.render(text, True, color)
    textRect = text.get_rect()
    textRect.center = (x, y)
    display.blit(text, textRect)
 
def main_loop():
    global clock
    global fps
    
    food = 0
    wood = 0
    pop = 0
    harvester = 0
    lumber = 0
    menu = 0
    game_running = True

    try:
        with open('savegame.txt', 'r') as file:
            if len(file.read().split("$$")) < 5:
                raise exception
    except:
        file = open("savegame.txt", "w")
        file.write("")
        file.close()

    with open('savegame.txt', 'r') as file:
        data = file.read()
        if len(data) != 0:
            pop = int(data.split("$$")[0])
            food = float(data.split("$$")[1])
            harvester = int(data.split("$$")[2])
            wood = float(data.split("$$")[3])
            lumber = int(data.split("$$")[4])
    
    background = Image(BACKGROUND_EXPLORE, 0, 0, display_width, display_height)

    food_button = Image(BUTTON_FOOD, 291, 200, 218, 200, 0, 0.5, 0.68, 0)
    explore_menu = Image(BUTTON_LARGE, 430, 480, 275, 100, "Explore")
    city_menu = Image(BUTTON_LARGE, 90, 480, 275, 100, "City")
    food_tag = Image(TEXTBOX_FOOD, 20, 20, 190, 100, 0, 0.4)
    food_prod_tag = Image(BUTTON_LARGE, 110, 30, 240, 80, 0, 0.68)
    wood_tag = Image(WOOD_TAG, 380, 20, 190, 100, 0, 0.4)
    wood_prod_tag = Image(BUTTON_LARGE, 460, 30, 240, 80, 0, 0.68)
    pop_tag = Image(POP_TAG, 20, 135, 190, 100, 0, 0.4)
    pop_plus = Image(BUTTON_ROUND_PLUS, 248, 139, 68, 68, menu=1)
    pop_cost = Image(BUTTON_LARGE_FOOD, 230, 130, 275, 100, 0, 0.52, menu=1)
    harvester_tag = Image(BUTTON_LARGE_HARVESTER, 90, 250, 275, 100, 0, 0.50, menu=1)
    harvester_plus = Image(RIGHT_BUTTON_PLUS, 475, 250, 80, 100, menu=1)
    harvester_minus = Image(LEFT_BUTTON_MINUS, 380, 250, 80, 100, menu=1)
    lumber_tag = Image(BUTTON_LARGE_LUMBERER, 90, 365, 275, 100, 0, 0.50, menu=1)
    lumber_plus = Image(RIGHT_BUTTON_PLUS, 475, 365, 80, 100, menu=1)
    lumber_minus = Image(LEFT_BUTTON_MINUS, 380, 365, 80, 100, menu=1)

    while game_running:
        
        food, wood = autominer(food, wood, pop, harvester, lumber)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

            if event.type == pygame.MOUSEBUTTONUP:

                mopos = pygame.mouse.get_pos()

                if pop_plus.collide(mopos, menu):
                    if food >= population_cost(pop):
                        food -= population_cost(pop)
                        pop += 1

                if food_button.collide(mopos, menu):
                    food += food_click(harvester)

                if explore_menu.collide(mopos, menu):
                    menu = 0
                    
                if city_menu.collide(mopos, menu):
                    menu = 1

                if harvester_plus.collide(mopos, menu):
                    if pop > harvester + lumber:
                        harvester += 1

                if harvester_minus.collide(mopos, menu):
                    if harvester > 0:
                        harvester -= 1

                if lumber_plus.collide(mopos, menu):
                    if pop > harvester + lumber:
                        lumber += 1

                if lumber_minus.collide(mopos, menu):
                    if lumber > 0:
                        lumber -= 1

                if food >= 2147483647:
                    print("You Beat the game")
                    game_running = False

        if menu == 0:
            background.change(BACKGROUND_EXPLORE)
            city_menu.change(BUTTON_LARGE)
            explore_menu.change(BUTTON_LARGE_SELECTED)
        elif menu == 1:
            background.change(BACKGROUND_CITY)
            city_menu.change(BUTTON_LARGE_SELECTED)
            explore_menu.change(BUTTON_LARGE)
        
        background.draw(menu)
        explore_menu.draw(menu)
        city_menu.draw(menu)

        pop_tag.set_text(display_number(pop))
        food_tag.set_text(display_number(food))
        wood_tag.set_text(display_number(wood))
        food_prod_tag.set_text(f"{display_number(production(harvester) * 10 - 0.05 * pop, 'high')}/s")
        wood_prod_tag.set_text(f"{display_number(production(lumber) * 10 * 0.8, 'high')}/s")

        food_prod_tag.draw(menu)
        food_tag.draw(menu)
        wood_prod_tag.draw(menu)
        wood_tag.draw(menu)
        pop_tag.draw(menu)

        food_button.set_text(display_number(food_click(harvester), "high"))
        food_button.draw(menu)

        harvester_tag.set_text(display_number(harvester))
        harvester_tag.draw(menu)
        harvester_plus.draw(menu)
        harvester_minus.draw(menu)

        lumber_tag.set_text(display_number(lumber))
        lumber_tag.draw(menu)
        lumber_plus.draw(menu)
        lumber_minus.draw(menu)

        pop_cost.set_text(population_cost(pop))
        pop_cost.draw(menu)
        pop_plus.draw(menu)
        
        with open('savegame.txt', 'w') as file:
            file.write(f"{pop}$${food}$${harvester}$${wood}$${lumber}")

        pygame.display.update()
        clock.tick(fps)

main_loop()
pygame.quit()
quit()