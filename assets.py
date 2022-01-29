import os
import utils

ASSET_DIR = os.path.join(".", "asset")
# Name of button: shape_symbol_other.png
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
        self.textSize = 25

        self.change(self.path)
        self.set_text(text)

    def set_text(self, text, color = (0, 0, 0)):
        if text != "":
            font = utils.Font('freesansbold.ttf', self.textSize)
            self.text = font.render(str(text), True, color)
            self.textRect = self.text.get_rect()
            avg = lambda a, l: (2 * a + l) / 2
            self.textRect.center = (avg(self.x, self.w) - (0.5 - self.textx) * self.w, avg(self.y, self.h) - (self.textSize / 6) - (0.5 - self.texty) * self.h)
    
    def set_text_size(self, textSize):
        self.textSize = textSize

    def change(self, path):
        picture = utils.load_image(path)
        self.picture = utils.scale_image(picture, (self.w, self.h))

    def draw(self, menu, display):
        if self.menu < 0 or self.menu == menu:
            display.blit(self.picture, (self.x, self.y))
            if self.text != "":
                display.blit(self.text, self.textRect)

    def collide(self, p, menu):
        return all([self.x <= p[0], p[0] <= self.x + self.w, self.y <= p[1], p[1] <= self.y + self.h, self.menu < 0 or menu == self.menu])