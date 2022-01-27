import pygame
from typing import Optional, Any
import engine
import json
import time

class Font(pygame.font.Font):
    pass

# --> Time <--

def current_time():
    return time.strftime("%Y %m %d %H %M %S", time.localtime())

def get_time(time_str):
    time.strptime(time_str, "%Y %m %d %H %M %S")

def get_future_time(seconds = 0, minutes = 0, hours = 0, starting_time = ""):
    if starting_time == "":
        starting_time = current_time()
    time_delta = time.timedelta(hours = hours, minutes = minutes, seconds = seconds)
    return starting_time + time_delta

def get_time_delta(time1, time2 = ""):
    if time2 == "":
        time2 = current_time()
    return time2 - time1

# --> Image <--

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

# --> Load/save game <--

def load_game() -> engine.Game:
    try:
        with open('savegame.txt', 'r') as file:
            data = json.load(file)
            return engine.Game.deserialize(data)
    except:
        return engine.Game(0, 0, 0, 0, 0, 0)

def save_game(game: engine.Game):
    with open('savegame.txt', 'w+') as file:
        file.write(json.dumps(game.serialize()))

# --> Formatting <--

def display_number(num, precision = "low") -> str:
    if num < 10 ** 3 and (precision == "low" or num == round(num)):
        return f"{int(round(num, 0))}"
    elif num < 10 ** 3 and precision == "high":
        return f"{round(num, 2)}"
    elif num < 10 ** 6:
        return f"{round(num / (10 ** 3), 2)}k"
    elif num < 10 ** 9:
        return f"{round(num / (10 ** 6), 2)}M"
    elif num < 10 ** 12:
        return f"{round(num / (10 ** 9), 2)}B"
    elif num < 10 ** 15:
        return f"{round(num / (10 ** 12), 2)}T"