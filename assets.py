import os

from pygame import Rect
import utils

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

class Image:
    def __init__(self, path: str, x: float, y: float, w: float, h: float, text: str = "", textx: float = 0.5, texty: float = 0.5, menu: int = -1) -> None:
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
        self.textSize = 25 # Default text size
        self.clipping_area: Rect = None # Clipping area for not showing part of a button
        self.text_clipping_area: Rect = None # Clipping area for not showing part of a button

        self.change(self.path)
        self.set_text(text)

    def set_text(self, text: str, color: tuple = (0, 0, 0)) -> None:
        """ Set text over image, default color: black """
        if text != "":
            font = utils.Font('freesansbold.ttf', self.textSize)
            self.text = font.render(str(text), True, color)
            self.textRect = self.text.get_rect()
            avg = lambda a, l: (2 * a + l) / 2
            self.textRect.center = (avg(self.x, self.w) - (0.5 - self.textx) * self.w, avg(self.y, self.h) - (self.textSize / 6) - (0.5 - self.texty) * self.h)
    
    def set_text_size(self, textSize: float) -> None:
        """ Change default text size """
        self.textSize = textSize

    def change(self, path: str) -> None:
        """ Change picture of image """
        picture = utils.load_image(path)
        self.picture = utils.scale_image(picture, (self.w, self.h))
    
    def refresh(self) -> None:
        self.picture = utils.scale_image(utils.load_image(self.path), (self.w, self.h))

    def draw(self, menu: int, display, area: tuple = None) -> None:
        """ Display image on screen based on the menu,
            with area you can set clipping area """
        if area != None:
            self.clipping_area = Rect(*area)
        if self.menu < 0 or self.menu == menu:
            display.blit(self.picture, (self.x, self.y), self.clipping_area)
            if self.text != "":
                display.blit(self.text, self.textRect)

    def collide(self, p: tuple, menu: int) -> bool:
        """ Return True if mouse collide with button """
        is_inside = self.x <= p[0] <= self.x + self.w and self.y <= p[1] <= self.y + self.h
        is_correct_menu = self.menu < 0 or menu == self.menu
        is_not_clipped = self.clipping_area == None
        if not is_not_clipped:
            is_not_clipped = self.x + self.clipping_area.left <= p[0] <= self.x + self.clipping_area.left + self.clipping_area.width
            is_not_clipped = is_not_clipped and self.y + self.clipping_area.top <= p[1] <= self.y + self.clipping_area.top + self.clipping_area.height
        return is_inside and is_correct_menu and is_not_clipped

    def move(self, x: float = 0, y: float = 0, lock = False, max_w = 0, max_h = 0) -> None:
        """ Move the image of x, y pixels """
        if lock:
            self.x = min(max(0, self.x + x), max_w - self.w)
            self.y = min(max(0, self.y + y), max_h - self.h)
        else:
            self.x += x
            self.y += y
