import pygame
import assets
import utils
from engine import GameStats as stats

class Ui:
    EXPLORE = 0
    CITY = 1

    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.fps = 10

        self.display_width = 800
        self.display_height = 600
        self.display = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption("Clicker")

        self.init_images()
        self.game = utils.load_saved_game_or_init_new_game()

        self.running = False

        self.current_menu = self.EXPLORE

    def init_images(self):
        self.background = assets.Image(assets.BACKGROUND_EXPLORE, 0, 0, self.display_width, self.display_height)

        self.food_button = assets.Image(assets.BUTTON_FOOD, 291, 200, 218, 200, 0, 0.5, 0.68, 0)
        self.explore_menu = assets.Image(assets.BUTTON_LARGE, 430, 480, 275, 100, "Explore")
        self.city_menu = assets.Image(assets.BUTTON_LARGE, 90, 480, 275, 100, "City")
        self.food_tag = assets.Image(assets.TEXTBOX_FOOD, 20, 20, 190, 100, 0, 0.4)
        self.food_prod_tag = assets.Image(assets.BUTTON_LARGE, 110, 30, 240, 80, 0, 0.68)
        self.wood_tag = assets.Image(assets.WOOD_TAG, 380, 20, 190, 100, 0, 0.4)
        self.wood_prod_tag = assets.Image(assets.BUTTON_LARGE, 460, 30, 240, 80, 0, 0.68)
        self.pop_tag = assets.Image(assets.POP_TAG, 20, 135, 190, 100, 0, 0.4)
        self.pop_plus = assets.Image(assets.BUTTON_ROUND_PLUS, 248, 139, 68, 68, menu=1)
        self.pop_cost = assets.Image(assets.BUTTON_LARGE_FOOD, 230, 130, 275, 100, 0, 0.52, menu=1)
        self.harvester_tag = assets.Image(assets.BUTTON_LARGE_HARVESTER, 90, 250, 275, 100, 0, 0.50, menu=1)
        self.harvester_plus = assets.Image(assets.RIGHT_BUTTON_PLUS, 475, 250, 80, 100, menu=1)
        self.harvester_minus = assets.Image(assets.LEFT_BUTTON_MINUS, 380, 250, 80, 100, menu=1)
        self.lumber_tag = assets.Image(assets.BUTTON_LARGE_LUMBERER, 90, 365, 275, 100, 0, 0.50, menu=1)
        self.lumber_plus = assets.Image(assets.RIGHT_BUTTON_PLUS, 475, 365, 80, 100, menu=1)
        self.lumber_minus = assets.Image(assets.LEFT_BUTTON_MINUS, 380, 365, 80, 100, menu=1)

    def run(self):
        self.running = True
        while self.running:
            # Update state
            self.loop()

            self.draw_menu()
            self.update_counters()
            self.update_buttons()

            pygame.display.update()
            self.clock.tick(self.fps)
            utils.save_game(self.game)
        pygame.quit()

    def loop(self):
        self.game.autominer()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONUP:

                mopos = pygame.mouse.get_pos()

                if self.pop_plus.collide(mopos, self.current_menu):
                    self.game.increment_population()

                if self.food_button.collide(mopos, self.current_menu):
                    self.game.increment_food()

                if self.explore_menu.collide(mopos, self.current_menu):
                    self.current_menu = self.EXPLORE
                    
                if self.city_menu.collide(mopos, self.current_menu):
                    self.current_menu = self.CITY

                if self.harvester_plus.collide(mopos, self.current_menu):
                    self.game.increment_harvester()

                if self.harvester_minus.collide(mopos, self.current_menu):
                    self.game.decrement_harvester()

                if self.lumber_plus.collide(mopos, self.current_menu):
                    self.game.increment_lumber()

                if self.lumber_minus.collide(mopos, self.current_menu):
                    self.game.decrement_lumber()

                if self.game.food >= 2147483647:
                    print("You Beat the game")
                    self.running = False

    def draw_menu(self):
        if self.current_menu == self.EXPLORE:
            self.background.change(assets.BACKGROUND_EXPLORE)
            self.city_menu.change(assets.BUTTON_LARGE)
            self.explore_menu.change(assets.BUTTON_LARGE_SELECTED)
        elif self.current_menu == self.CITY:
            self.background.change(assets.BACKGROUND_CITY)
            self.city_menu.change(assets.BUTTON_LARGE_SELECTED)
            self.explore_menu.change(assets.BUTTON_LARGE)
        
        self.background.draw(self.current_menu, self.display)
        self.explore_menu.draw(self.current_menu, self.display)
        self.city_menu.draw(self.current_menu, self.display)

    def update_counters(self):
        self.pop_tag.set_text(self.game.get_formatted_stats(stats.population))
        self.food_tag.set_text(self.game.get_formatted_stats(stats.food))
        self.wood_tag.set_text(self.game.get_formatted_stats(stats.wood))
        self.food_prod_tag.set_text(self.game.harvester_production_per_second(self.fps))

        self.food_prod_tag.draw(self.current_menu, self.display)
        self.food_tag.draw(self.current_menu, self.display)
        self.wood_prod_tag.set_text(self.game.lumber_production_per_second(self.fps))
        self.wood_prod_tag.draw(self.current_menu, self.display)
        self.wood_tag.draw(self.current_menu, self.display)
        self.pop_tag.draw(self.current_menu, self.display)

    def update_buttons(self):
        self.food_button.set_text(self.game.get_earn_per_click())
        self.food_button.draw(self.current_menu, self.display)

        self.harvester_tag.set_text(self.game.format_harvester())
        self.harvester_tag.draw(self.current_menu, self.display)
        self.harvester_plus.draw(self.current_menu, self.display)
        self.harvester_minus.draw(self.current_menu, self.display)

        self.lumber_tag.set_text(self.game.format_lumber())
        self.lumber_tag.draw(self.current_menu, self.display)
        self.lumber_plus.draw(self.current_menu, self.display)
        self.lumber_minus.draw(self.current_menu, self.display)

        self.pop_cost.set_text(self.game.format_population_cost())
        self.pop_cost.draw(self.current_menu, self.display)
        self.pop_plus.draw(self.current_menu, self.display)