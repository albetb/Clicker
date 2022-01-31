
from pygame import Rect, image, transform, font
from pygame.surface import Surface
from typing import Optional, Any
import engine
import json

class Font(font.Font):
    pass

# ----------> Image <----------------------------------------

def load_image(path: str) -> Surface:
    """ Load an image from a file """
    return image.load(path)

def scale_image(surface: Surface,
                size: Any,
                dest_surface: Optional[Surface] = None):
    """ Return an image scaled to a size """
    if dest_surface is not None:
        return transform.scale(surface, size, dest_surface)
    return transform.scale(surface, (int(size[0]), int(size[1])))

def set_clipping_area(surface: Surface, left: int, top: int, width: int, height: int):
    surface.set_clip(Rect(left, top, width, height))
    

# ----------> Load/save game <----------------------------------------

def load_game() -> engine.Game:
    """ Load a game from a .txt file """
    try:
        with open('savegame.txt', 'r') as file:
            data = json.load(file)
            return engine.Game.deserialize(data)
    except:
        return engine.Game()

def save_game(game: engine.Game):
    """ Save the current game to a .txt file """
    with open('savegame.txt', 'w+') as file:
        file.write(json.dumps(game.serialize()))

# ----------> Formatting <----------------------------------------

def format_number(num: float, precision: str = "low") -> str:
    """ Display a number with less decimal and with a literal notation (es 20k),
        precision 'low' and 'high' determine number of decimal with number < 1000 """
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