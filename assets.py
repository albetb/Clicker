import os
import utils

ASSET_DIR = os.path.join(".", "asset")
BACKGROUND_EXPLORE = os.path.join(ASSET_DIR, "background_explore.jpg")
BACKGROUND_CITY = os.path.join(ASSET_DIR, "background_city.png")
BACKGROUND_MANAGE = os.path.join(ASSET_DIR, "background_manage.png")
BUTTON_FOOD = os.path.join(ASSET_DIR, "buttonfood.png")
BUTTON_LARGE = os.path.join(ASSET_DIR, "button_large.png")
BUTTON_SQUARE = os.path.join(ASSET_DIR, "button_square.png")
HOUSE_TAG = os.path.join(ASSET_DIR, "house_tag.png")
BUTTON_LARGE_SELECTED = os.path.join(ASSET_DIR, "button_large_selected.png")
BUTTON_LARGE_FOOD = os.path.join(ASSET_DIR, "button_large_food.png")
BUTTON_LARGE_WOOD = os.path.join(ASSET_DIR, "button_large_wood.png")
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