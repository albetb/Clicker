import os
from pygame import Rect, image, transform, font
from pygame.surface import Surface
from typing import Optional, Any

class Font(font.Font):
    pass

FONT = "freesansbold.ttf"
ASSET_DIR = os.path.join(".", "asset")

# ----------> Button files <----------------------------------------
# Name of buttons: shape_symbol_other.png

BACKGROUND_EXPLORE = os.path.join(ASSET_DIR, "background_explore.jpg")
BACKGROUND_CITY = os.path.join(ASSET_DIR, "background_city.png")
BACKGROUND_MANAGE = os.path.join(ASSET_DIR, "background_manage.png")

SQUARE_PLUS_FOOD = os.path.join(ASSET_DIR, "square_plus_food.png")
SQUARE_PLUS_FOOD_DISABLED = os.path.join(ASSET_DIR, "square_plus_food_disabled.png")
SQUARE = os.path.join(ASSET_DIR, "square.png")
SQUARE_HOUSE = os.path.join(ASSET_DIR, "square_house.png")

ROUND_PLUS = os.path.join(ASSET_DIR, "round_plus.png")
ROUND_WOOD = os.path.join(ASSET_DIR, "round_wood.png")

LARGE = os.path.join(ASSET_DIR, "large.png")
LARGE_SELECTED = os.path.join(ASSET_DIR, "large_selected.png")
LARGE_FOOD = os.path.join(ASSET_DIR, "large_food.png")
LARGE_WOOD = os.path.join(ASSET_DIR, "large_wood.png")
LARGE_HARVESTER = os.path.join(ASSET_DIR, "large_harvester.png")
LARGE_LUMBERER = os.path.join(ASSET_DIR, "large_lumberer.png")

LEFT_ARROW_MINUS = os.path.join(ASSET_DIR, "left_arrow_minus.png")
RIGHT_ARROW_PLUS = os.path.join(ASSET_DIR, "right_arrow_plus.png")
RIGHT_ARROW_PLUS_DISABLED = os.path.join(ASSET_DIR, "right_arrow_plus_disabled.png")

TAG_POPULATION = os.path.join(ASSET_DIR, "tag_population.png")
TAG_FOOD = os.path.join(ASSET_DIR, "tag_food.png")
TAG_WOOD = os.path.join(ASSET_DIR, "tag_wood.png")

FRAME = os.path.join(ASSET_DIR, "no_image.png")
HOUSE = os.path.join(ASSET_DIR, "house.png")

# ----------> Image <----------------------------------------

def load_image(path: str) -> Surface:
    """ Load an image from a file """
    return image.load(path)

def scale_image(surface: Surface,
                size: Any,
                dest_surface: Optional[Surface] = None) -> Surface:
    """ Return an image scaled to a size """
    if dest_surface is not None:
        return transform.scale(surface, size, dest_surface)
    return transform.scale(surface, (int(size[0]), int(size[1])))

class Image:
    def __init__(self, path: str, x: float, y: float, w: float, h: float, 
                 text: str = "", text_x: float = 0.5, text_y: float = 0.5, text_size: int = 25) -> None:
        self.path = path # Image relative path
        self.x = x # X positioning, if x ↑ image →
        self.y = y # Y positioning, if y ↑ image ↓
        self.w = w # Image width
        self.h = h # Image height
        self.clipping_area: Rect = None # Clipping area for not showing part of a button
        self.text = "" # Text of image
        self.text_x = text_x # X positioning of text [0, 1], 1 is 100% right
        self.text_y = text_y # Y positioning of text [0, 1], 1 is 100% down
        self.textSize = text_size # Default text size
        self.textRect: Rect = None # Needed to display text
        self.text_clipping_area: Rect = None # Clipping area for not showing part of a button

        self.change(self.path)
        self.set_text(text)

    def set_text(self, text: str, color: tuple = (0, 0, 0)) -> None:
        """ Set text over image, default color: black """
        if text != "":
            self.text = Font(FONT, self.textSize).render(str(text), True, color)
            self.textRect = self.text.get_rect()
            avg = lambda xy, wh: (2 * xy + wh) / 2
            self.textRect.center = (avg(self.x, self.w) - (0.5 - self.text_x) * self.w, avg(self.y, self.h) - (self.textSize / 6) - (0.5 - self.text_y) * self.h)
    
    def set_text_size(self, textSize: float) -> None:
        """ Change default text size """
        self.textSize = textSize

    def change(self, path: str = "") -> None:
        """ Change picture of image,
            note that you have to change picture before drawing it """
        self.picture = scale_image(load_image(self.path if path == "" else path), (self.w, self.h))

    def draw(self, display, clipping_area: tuple = None, text = "") -> None:
        """ Display image on screen based on the menu,
            with clipping_area you can set clipping area """
        self.clipping_area = self.clipping_area if clipping_area == None else Rect(*clipping_area)
        display.blit(self.picture, (self.x, self.y), self.clipping_area)
        if text != "":
            self.set_text(text)
        if self.text != "":
            display.blit(self.text, self.textRect)

    def collide(self, p: tuple) -> bool:
        """ Return True if mouse collide with button """
        return self.x <= p[0] <= self.x + self.w and self.y <= p[1] <= self.y + self.h

    def move(self, right: float = 0, down: float = 0, lock: bool = False, max_w: float = 0, max_h: float = 0) -> None:
        """ Move the image of right →, down ↓ pixels """
        self.x = min(max(0, self.x + right), max_w - self.w) if lock else self.x + right
        self.y = min(max(0, self.y + down), max_h - self.h) if lock else self.y + down