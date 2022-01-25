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

        self.display_width = 1024
        self.display_height = self.display_width * 3 // 4
        self.display = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption("Clicker")

        self.init_images()
        self.game = utils.load_saved_game_or_init_new_game()

        self.running = False

        self.current_menu = self.EXPLORE
        self.press_time = 0 # Time when a button pressing started

    def init_images(self):
        self.background = assets.Image(assets.BACKGROUND_EXPLORE, 0, 0, self.display_width, self.display_height)
        # Lambdas who calculate button heigth given width
        large_h = lambda large_w: large_w * 100 // 275
        tag_h = lambda large_w: large_w * 100 // 190
        square_h = lambda square_w: square_w * 109 // 100
        round_h = lambda round_w: round_w * 103 // 100
        arrow_h = lambda round_w: round_w * 100 // 80

        # Central button, give food when clicked
        food_w = 200
        self.food_button = assets.Image(assets.BUTTON_FOOD, (self.display_width - food_w) / 2, (self.display_height - square_h(food_w)) / 2, square_h(food_w), food_w, 0, 0.5, 0.68, 0)

        # Bottom menu button
        menu_w = 275
        self.city_menu = assets.Image(assets.BUTTON_LARGE, (self.display_width - 2 * menu_w) // 3, self.display_height - large_h(menu_w) - 20, menu_w, large_h(menu_w), "City")
        self.explore_menu = assets.Image(assets.BUTTON_LARGE, (self.display_width - 2 * menu_w) * 2 // 3 + menu_w, self.display_height - large_h(menu_w) - 20, menu_w, large_h(menu_w), "Explore")
        
        # Tag with current resources
        resource_w = 190
        production_w = resource_w * 0.9
        self.food_tag = assets.Image(assets.TEXTBOX_FOOD, (self.display_width - 3 * 1.5 * resource_w) // 4, 20, resource_w, tag_h(resource_w), 0, 0.4)
        self.food_prod_tag = assets.Image(assets.BUTTON_LARGE, (self.display_width - 3 * 1.5 * resource_w) // 4 + resource_w * 0.7, 30, production_w, large_h(production_w), 0, 0.65, 0.55)
        self.food_prod_tag.set_text_size(22)
        self.wood_tag = assets.Image(assets.WOOD_TAG, (self.display_width - 3 * 1.5 * resource_w) * 2 // 4 + 1.5 * resource_w, 20, resource_w, tag_h(resource_w), 0, 0.4)
        self.wood_prod_tag = assets.Image(assets.BUTTON_LARGE, (self.display_width - 3 * 1.5 * resource_w) * 2 // 4 + 1.5 * resource_w + resource_w * 0.7, 30, production_w, large_h(production_w), 0, 0.65, 0.55)
        self.wood_prod_tag.set_text_size(22)
        self.pop_tag = assets.Image(assets.POP_TAG, (self.display_width - 3 * 1.5 * resource_w) // 4, 20 + 15 + tag_h(resource_w), resource_w, tag_h(resource_w), 0, 0.4)

        # Buy population button and cost
        arrow_w = 80
        self.pop_plus = assets.Image(assets.RIGHT_BUTTON_PLUS, (self.display_width - 3 * 1.5 * resource_w) // 4 + resource_w + 15 + menu_w * 0.85 + 7, 20 + 15 + 9 + tag_h(resource_w), arrow_w * 0.7, arrow_h(arrow_w * 0.7), menu=1)
        self.pop_cost = assets.Image(assets.BUTTON_LARGE_FOOD, (self.display_width - 3 * 1.5 * resource_w) // 4 + resource_w + 15, 20 + 15 + tag_h(resource_w), menu_w * 0.85, large_h(menu_w * 0.85), 0, 0.4, menu=1)

        # Worker menu
        worker_x, worker_y = 90, 280
        self.harvester_tag = assets.Image(assets.BUTTON_LARGE_HARVESTER, worker_x, worker_y, menu_w, large_h(menu_w), 0, 0.4, menu=1)
        self.harvester_minus = assets.Image(assets.LEFT_BUTTON_MINUS, worker_x + menu_w + 8, worker_y, arrow_w, arrow_h(arrow_w), menu=1)
        self.harvester_plus = assets.Image(assets.RIGHT_BUTTON_PLUS, worker_x + menu_w + arrow_w + 8 * 2, worker_y, arrow_w, arrow_h(arrow_w), menu=1)
        self.lumber_tag = assets.Image(assets.BUTTON_LARGE_LUMBERER, worker_x, worker_y + large_h(menu_w) + 10, menu_w, large_h(menu_w), 0, 0.4, menu=1)
        self.lumber_minus = assets.Image(assets.LEFT_BUTTON_MINUS, worker_x + menu_w + 8, worker_y + large_h(menu_w) + 10, arrow_w, arrow_h(arrow_w), menu=1)
        self.lumber_plus = assets.Image(assets.RIGHT_BUTTON_PLUS, worker_x + menu_w + arrow_w + 8 * 2, worker_y + large_h(menu_w) + 10, arrow_w, arrow_h(arrow_w), menu=1)

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
        mouse = pygame.mouse.get_pos()
        
        if self.press_time > 0: # Fast buy when long press button
            if self.pop_plus.collide(mouse, self.current_menu):
                self.game.increment_population(((pygame.time.get_ticks() - self.press_time) // 1000) ** 2)

            if self.harvester_plus.collide(mouse, self.current_menu):
                self.game.increment_harvester(((pygame.time.get_ticks() - self.press_time) // 1000) ** 2)

            if self.harvester_minus.collide(mouse, self.current_menu):
                self.game.decrement_harvester(((pygame.time.get_ticks() - self.press_time) // 1000) ** 2)

            if self.lumber_plus.collide(mouse, self.current_menu):
                self.game.increment_lumber(((pygame.time.get_ticks() - self.press_time) // 1000) ** 2)

            if self.lumber_minus.collide(mouse, self.current_menu):
                self.game.decrement_lumber(((pygame.time.get_ticks() - self.press_time) // 1000) ** 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.press_time == 0: # Save time when start pressing button
                    self.press_time = pygame.time.get_ticks()

            if event.type == pygame.MOUSEBUTTONUP:

                self.press_time = 0 # Reset time when relase button

                if self.pop_plus.collide(mouse, self.current_menu):
                    self.game.increment_population()

                if self.food_button.collide(mouse, self.current_menu):
                    self.game.increment_food()

                if self.explore_menu.collide(mouse, self.current_menu):
                    self.current_menu = self.EXPLORE
                    
                if self.city_menu.collide(mouse, self.current_menu):
                    self.current_menu = self.CITY

                if self.harvester_plus.collide(mouse, self.current_menu):
                    self.game.increment_harvester()

                if self.harvester_minus.collide(mouse, self.current_menu):
                    self.game.decrement_harvester()

                if self.lumber_plus.collide(mouse, self.current_menu):
                    self.game.increment_lumber()

                if self.lumber_minus.collide(mouse, self.current_menu):
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