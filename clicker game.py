
import pygame # pip install pygame
#import time

pygame.init()
GAME_VERSION = "0.0.1"

clock = pygame.time.Clock()
time_delta = 10

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
 
class Image:
    def __init__(self, path, x, y, w, h, text = "", modx = 0.5, mody = 0.5):
        self.path = path
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.counter = not isinstance(text, str)
        self.text = ""
        self.textRect = 0
        self.modx = modx
        self.mody = mody

        self.change(self.path)
        self.set_text(text)

    def set_text(self, text, size = 30, color = (0, 0, 0)):
        if text != "":
            font = pygame.font.Font('freesansbold.ttf', size)
            self.text = font.render(str(text), True, color)
            self.textRect = self.text.get_rect()
            avg = lambda a, l: (2 * a + l) / 2
            self.textRect.center = (avg(self.x, self.w) - (0.5 - self.modx) * self.w, avg(self.y, self.h) - (size // 4) - (0.5 - self.mody) * self.h)

    def change(self, path):
        picture = pygame.image.load(path)
        self.picture = pygame.transform.scale(picture, (self.w, self.h))

    def draw(self):
        display.blit(self.picture, (self.x, self.y))
        if self.text != "":
            display.blit(self.text, self.textRect)

    def collide(self, p):
        return all([self.x <= p[0], p[0] <= self.x + self.w, self.y <= p[1], p[1] <= self.y + self.h])

production = lambda pop: 0.05 * (pop ** 1.05) * (1 + (pop // 10) * 0.5)
population_cost = lambda pop: round(((pop + 1) * 50) ** 1.1)
food_click = lambda pop: 10 + pop ** 1.5

def display_number(num, precision = "low"):
    if num < 10 ** 3 and precision == "low":
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

def autominer(food, pop):
    return round(food + production(pop), 2)
 
def text(text, color, x, y, fsize):
    font = pygame.font.Font('freesansbold.ttf', fsize)
    text = font.render(text, True, color)
    textRect = text.get_rect()
    textRect.center = (x, y)
    display.blit(text, textRect)
 
def main_loop():
    global clock
    global time_delta
    
    food = 1
    pop = 0
    menu = 0
    game_running = True
    with open('savegame.txt', 'r') as file:
        data = file.read()
        if len(data) != 0:
            pop = int(data.split("$$")[0])
            food = float(data.split("$$")[1])
    
    food_button = Image(r".\asset\buttonfood.png", 291, 200, 218, 200, 0, 0.5, 0.68)
    background = Image(r".\asset\background_explore.jpg", 0, 0, display_width, display_height)
    explore_menu = Image(r".\asset\button_large.png", 430, 480, 275, 100, "Explore")
    city_menu = Image(r".\asset\button_large.png", 90, 480, 275, 100, "City")
    food_tag = Image(r".\asset\textboxfood.png", 20, 20, 190, 100, 0, 0.4)
    pop_tag = Image(r".\asset\poptag.png", 20, 140, 190, 100, 0, 0.4)
    pop_plus = Image(r".\asset\buttonroundplus.png", 248, 149, 68, 68)
    pop_cost = Image(r".\asset\button_large_food.png", 230, 140, 275, 100, 0, 0.52)

    while game_running:
        
        food = autominer(food, pop)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

            if event.type == pygame.MOUSEBUTTONUP:

                mopos = pygame.mouse.get_pos()

                if pop_plus.collide(mopos) and menu == 1:
                    if food >= population_cost(pop):
                        food -= population_cost(pop)
                        pop += 1

                if food_button.collide(mopos) and menu == 0:
                    food += food_click(pop)

                if explore_menu.collide(mopos):
                    menu = 0
                    
                if city_menu.collide(mopos):
                    menu = 1

                if food >= 2147483647:
                    print("You Beat the game")
                    game_running = False

        if menu == 0:
            background.change(r".\asset\background_explore.jpg")
            city_menu.change(r".\asset\button_large.png")
            explore_menu.change(r".\asset\button_large_selected.png")
        elif menu == 1:
            background.change(r".\asset\background_city.png")
            city_menu.change(r".\asset\button_large_selected.png")
            explore_menu.change(r".\asset\button_large.png")
        
        background.draw()
        explore_menu.draw()
        city_menu.draw()

        pop_tag.set_text(display_number(pop))
        food_tag.set_text(display_number(food))
        text(f"+{display_number(production(pop) * 10, 'high')}/s", black, 265, 60, 30)

        food_tag.draw()
        pop_tag.draw()

        if menu == 0:
            food_button.set_text(display_number(food_click(pop), "high"))
            food_button.draw()
        elif menu == 1:
            pop_cost.set_text(population_cost(pop))
            pop_cost.draw()
            pop_plus.draw()
        
        with open('savegame.txt', 'w') as file:
            file.write(f"{pop}$${food}")

        pygame.display.update()
        clock.tick(time_delta)

main_loop()
pygame.quit()
quit()