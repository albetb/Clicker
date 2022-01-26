import pygame
from typing import Optional, Any
import engine

class Font(pygame.font.Font):
    pass

def load_image(path: str) -> pygame.surface.Surface:
    return pygame.image.load(path)

def scale_image(
    surface: pygame.surface.Surface,
    size: Any,
    dest_surface: Optional[pygame.surface.Surface] = None,
):
    if dest_surface is not None:
         return pygame.transform.scale(surface, size, dest_surface)
    return pygame.transform.scale(surface, size)

def load_saved_game_or_init_new_game() -> engine.Game:
    try:
        with open('savegame.txt', 'r') as file:
            data = file.read()
            if len(data.split("$$")) < 6:
                raise RuntimeError("")
            if len(data) != 0:
                pop = int(data.split("$$")[0])
                food = float(data.split("$$")[1])
                wood = float(data.split("$$")[3])
                harvester = int(data.split("$$")[2])
                lumber = int(data.split("$$")[4])
                house = int(data.split("$$")[5])
                return engine.Game(pop, food, wood, harvester, lumber, house)
            return engine.Game(0, 0, 0, 0, 0, 0)
    except:
        return engine.Game(0, 0, 0, 0, 0, 0)

def save_game(game: engine.Game):
    with open('savegame.txt', 'w+') as file:
        file.write(game.serialize())

def display_number(num, precision = "low") -> str:
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