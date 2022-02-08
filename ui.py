import pygame
import assets
from engine import load_game

# Lambdas who calculate button heigth given width
large_h = lambda large_w: int(round(large_w * 0.364, 0))
medium_h = lambda large_w: int(round(large_w * 0.434, 0))
tag_h = lambda large_w: int(round(large_w * 0.526, 0))
square_h = lambda square_w: int(round(square_w * 1.09, 0))
round_h = lambda round_w: int(round(round_w * 1.03, 0))
arrow_h = lambda round_w: int(round(round_w * 1.25, 0))

# Base button width and position
RESOURCE = 230
PRODUCTION = RESOURCE * 0.6
FOOD = 200
MENU = 275
ARROW = 80
WORKER_X, WORKER_Y = 70, 280

# Color
BLACK = (0, 0, 0)
GREY = (97, 83, 74)

class Ui:
    EXPLORE = 0
    MANAGE = 1
    CITY = 2

    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()

        self.W = 1024 # Width
        self.H = self.W * 3 // 4 # Height, display aspect ratio 4:3
        self.display = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Clicker")

        self.init_images()
        self.game = load_game()
        self.fps = self.game.fps # Game frame per second

        self.current_menu = self.EXPLORE
        self.press_time = 0 # Time when a button pressing started
        self.starting_position = (0, 0) # For dragging image
        self.mouse = (0, 0) # Current mouse position

    def init_images(self) -> None:
        """ Initialize image """
        self.background = assets.Image(assets.BACKGROUND_EXPLORE, 0, 0, self.W, self.H)
        # Central button, give food when clicked
        self.food_button = assets.Image(assets.SQUARE_PLUS_FOOD, (self.W - FOOD) / 2, (self.H - square_h(FOOD)) / 2, square_h(FOOD), FOOD, 0, 0.5, 0.68)
        # Wood button
        self.wood_timer = assets.Image(assets.LARGE, self.W * 0.7 + FOOD * 0.25, (self.H - square_h(FOOD)) / 2 + (round_h(FOOD * 0.5) - large_h(FOOD * 0.8)) / 2, FOOD * 0.8, large_h(FOOD * 0.8), "", 0.58, 0.55)
        self.wood_button = assets.Image(assets.ROUND_WOOD, self.W * 0.7, (self.H - square_h(FOOD)) / 2, FOOD * 0.5, round_h(FOOD * 0.5))
        # Bottom menu button
        self.manage_menu = assets.Image(assets.LARGE, (self.W - 3 * MENU) // 4, self.H - large_h(MENU) - 20, MENU, large_h(MENU), "Manage", text_size=30)
        self.explore_menu = assets.Image(assets.LARGE, (self.W - 3 * MENU) * 2 // 4 + MENU, self.H - large_h(MENU) - 20, MENU, large_h(MENU), "Explore", text_size=30)
        self.city_menu = assets.Image(assets.LARGE, (self.W - 3 * MENU) * 3 // 4 + 2 * MENU, self.H - large_h(MENU) - 20, MENU, large_h(MENU), "City", text_size=30)
        # Tag with current resources
        self.food_tag = assets.Image(assets.LARGE_FOOD, 0.03 * self.W, 0.03 * self.H, RESOURCE, large_h(RESOURCE), 0, text_x=0.4, text_size=23)
        self.food_prod_tag = assets.Image(assets.TAG, 0.03 * self.W + RESOURCE * 0.1, 0.03 * self.H + tag_h(PRODUCTION) * 0.82, PRODUCTION, tag_h(PRODUCTION), 0, text_x = 0.44, text_y = 0.53, text_size=18)
        self.wood_tag = assets.Image(assets.LARGE_WOOD, 0.06 * self.W + RESOURCE, 0.03 * self.H, RESOURCE, large_h(RESOURCE), 0, text_x=0.4, text_size=23)
        self.wood_prod_tag = assets.Image(assets.TAG, 0.06 * self.W + RESOURCE + RESOURCE * 0.1, 0.03 * self.H + tag_h(PRODUCTION) * 0.82, PRODUCTION, tag_h(PRODUCTION), 0, text_x = 0.44, text_y = 0.53, text_size=18)
        self.tag_population = assets.Image(assets.MEDIUM_POPULATION, 0.03 * self.W, tag_h(RESOURCE) + 40, RESOURCE * 0.85, medium_h(RESOURCE * 0.85), 0, 0.45)
        # Buy population button and cost
        self.pop_cost = assets.Image(assets.LARGE_FOOD, 0.03 * self.W + RESOURCE * 0.85 + 5, tag_h(RESOURCE) + 40, MENU * 0.85, large_h(MENU * 0.85), 0, 0.4)
        self.pop_plus = assets.Image(assets.RIGHT_ARROW_PLUS, 0.03 * self.W + RESOURCE * 0.85 + MENU * 0.85 + 10, tag_h(RESOURCE) + 44, ARROW * 0.7, arrow_h(ARROW * 0.7))
        # Worker menu
        self.harvester_tag = assets.Image(assets.LARGE_HARVESTER, WORKER_X, WORKER_Y, MENU, large_h(MENU), 0, 0.4)
        self.harvester_minus = assets.Image(assets.LEFT_ARROW_MINUS, WORKER_X + MENU + 8, WORKER_Y, ARROW, arrow_h(ARROW))
        self.harvester_plus = assets.Image(assets.RIGHT_ARROW_PLUS, WORKER_X + MENU + ARROW + 12, WORKER_Y, ARROW, arrow_h(ARROW))
        self.lumber_tag = assets.Image(assets.LARGE_LUMBERER, WORKER_X, WORKER_Y + large_h(MENU) + 10, MENU, large_h(MENU), 0, 0.4)
        self.lumber_minus = assets.Image(assets.LEFT_ARROW_MINUS, WORKER_X + MENU + 8, WORKER_Y + large_h(MENU) + 10, ARROW, arrow_h(ARROW))
        self.lumber_plus = assets.Image(assets.RIGHT_ARROW_PLUS, WORKER_X + MENU + ARROW + 12, WORKER_Y + large_h(MENU) + 10, ARROW, arrow_h(ARROW))
        # City menu
        self.building_frame = assets.Image(assets.FRAME, self.W * 0.625, self.H * 0.336, self.W * 0.273, self.H * 0.439)
        self.square_house = assets.Image(assets.SQUARE_HOUSE, WORKER_X, WORKER_Y - 4, ARROW * 1.3, square_h(ARROW * 1.3), 0, 0.5, 0.46)
        self.house_cost = assets.Image(assets.LARGE_WOOD, WORKER_X + ARROW * 1.3 + 8, WORKER_Y, MENU, large_h(MENU), 0, 0.37, text_size=24)
        self.house_plus = assets.Image(assets.RIGHT_ARROW_PLUS, WORKER_X + ARROW * 1.3 + MENU + 2*  8, WORKER_Y, ARROW, arrow_h(ARROW))
        self.square_granary = assets.Image(assets.SQUARE_GRANARY, WORKER_X, WORKER_Y - 4 + square_h(ARROW * 1.3) + 5, ARROW * 1.3, square_h(ARROW * 1.3), 0, 0.5, 0.46)
        self.granary_cost = assets.Image(assets.LARGE_WOOD, WORKER_X + ARROW * 1.3 + 8, WORKER_Y + square_h(ARROW * 1.3) + 5, MENU, large_h(MENU), 0, 0.37, text_size=24)
        self.granary_plus = assets.Image(assets.RIGHT_ARROW_PLUS, WORKER_X + ARROW * 1.3 + MENU + 2*  8, WORKER_Y + square_h(ARROW * 1.3) + 5, ARROW, arrow_h(ARROW))
        self.square_storage = assets.Image(assets.SQUARE_STORAGE, WORKER_X, WORKER_Y - 4 + 2 * square_h(ARROW * 1.3) + 10, ARROW * 1.3, square_h(ARROW * 1.3), 0, 0.5, 0.46)
        self.storage_cost = assets.Image(assets.LARGE_WOOD, WORKER_X + ARROW * 1.3 + 8, WORKER_Y + 2 * square_h(ARROW * 1.3) + 10, MENU, large_h(MENU), 0, 0.37, text_size=24)
        self.storage_plus = assets.Image(assets.RIGHT_ARROW_PLUS, WORKER_X + ARROW * 1.3 + MENU + 2*  8, WORKER_Y + 2 * square_h(ARROW * 1.3) + 10, ARROW, arrow_h(ARROW))
        self.building0 = assets.Image(assets.LARGE, (self.W * 0.273 - MENU) / 2, 0, MENU, large_h(MENU), text_x = 0.58)
        self.building1 = assets.Image(assets.LARGE, (self.W * 0.273 - MENU) / 2, large_h(MENU) + 5, MENU, large_h(MENU), text_x = 0.58)
        self.building2 = assets.Image(assets.LARGE, (self.W * 0.273 - MENU) / 2, 2 * large_h(MENU) + 10, MENU, large_h(MENU), text_x = 0.58)
        self.house = assets.Image(assets.HOUSE, large_h(MENU) * 0.125, large_h(MENU) * 0.125, large_h(MENU) * 0.75, large_h(MENU) * 0.75)
        self.granary = assets.Image(assets.GRANARY, large_h(MENU) * 0.125, large_h(MENU) * 0.125, large_h(MENU) * 0.75, large_h(MENU) * 0.75)
        self.storage = assets.Image(assets.STORAGE, large_h(MENU) * 0.125, large_h(MENU) * 0.125, large_h(MENU) * 0.75, large_h(MENU) * 0.75)

    def run(self) -> None:
        """ Core loop of the game """
        while True:
            # Generate resource and manage event
            self.game.autominer()
            self.game.manage_event()
            self.mouse = pygame.mouse.get_pos()
            # Before game events / user input
            self.loop_explore_menu()
            self.loop_manage_menu()
            self.loop_city_menu()
            # Game events / user input
            for event in pygame.event.get():
                self.event_menu(event)
                self.event_explore_menu(event)
                self.event_manage_menu(event)
                self.event_city_menu(event)
            # Draw screen
            self.draw_menu()
            self.draw_counters()
            self.draw_explore_menu()
            self.draw_manage_menu()
            self.draw_city_menu()
            # Update screen and save
            pygame.display.update()
            self.clock.tick(self.fps)
            self.game.save_current_time()
            self.game.save_game()

    def event_menu(self, event: pygame.event) -> None:
        """ Manage user event in the all menu """
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEBUTTONUP:
            if self.manage_menu.collide(self.mouse):
                self.current_menu = self.MANAGE
            if self.explore_menu.collide(self.mouse):
                self.current_menu = self.EXPLORE
            if self.city_menu.collide(self.mouse):
                self.current_menu = self.CITY

    def draw_menu(self) -> None:
        """ Draw bottom menu and change background """
        background = {
            self.EXPLORE: assets.BACKGROUND_EXPLORE,
            self.CITY: assets.BACKGROUND_CITY,
            self.MANAGE: assets.BACKGROUND_MANAGE,
        }
        self.background.change(background[self.current_menu])
        self.city_menu.set_text("City", GREY if self.current_menu == self.CITY else BLACK)
        self.explore_menu.set_text("Explore", GREY if self.current_menu == self.EXPLORE else BLACK)
        self.manage_menu.set_text("Manage", GREY if self.current_menu == self.MANAGE else BLACK)
        self.city_menu.change(assets.LARGE_DISABLED if self.current_menu == self.CITY else assets.LARGE)
        self.explore_menu.change(assets.LARGE_DISABLED if self.current_menu == self.EXPLORE else assets.LARGE)
        self.manage_menu.change(assets.LARGE_DISABLED if self.current_menu == self.MANAGE else assets.LARGE)

        self.background.draw(self.display)
        self.city_menu.draw(self.display)
        self.explore_menu.draw(self.display)
        self.manage_menu.draw(self.display)

    def draw_counters(self) -> None:
        """ Update resources and production counter """
        # Food counter
        if self.game.harvester_production() != 0:
            self.food_prod_tag.draw(self.display, text = self.game.format_harvester_production())
        self.food_tag.draw(self.display, text = self.game.format_food())
        # Wood counter
        if self.game.lumber_production() != 0:
            self.wood_prod_tag.draw(self.display, text = self.game.format_lumber_production())
        self.wood_tag.draw(self.display, text = self.game.format_wood())
        # Population counter
        self.tag_population.draw(self.display, text = self.game.format_population())

    # --------------------> 🔭 EXPLORE 🔭 <---------------------------------------------

    def loop_explore_menu(self) -> None:
        """ Executed at the start of every loop in the explore menu """
        if self.current_menu == self.EXPLORE:
            pass

    def event_explore_menu(self, event: pygame.event) -> None:
        """ Manage user event in the explore menu """
        if self.current_menu == self.EXPLORE:

            if event.type == pygame.MOUSEBUTTONUP:
                if self.food_button.collide(self.mouse):
                    self.game.food_gathering()
                elif self.wood_button.collide(self.mouse):
                    self.game.wood_gathering()

    def draw_explore_menu(self) -> None:
        """ Draw button in the explore menu """
        if self.current_menu == self.EXPLORE:
            
            ## Wood+ button and timer
            if self.game.event_list.event_exist("WoodPlus"):
                self.wood_timer.draw(self.display, text = self.game.event_list.select_event("WoodPlus").format_lasting_time())
                self.food_button.change(assets.SQUARE_PLUS_FOOD_DISABLED)
                self.food_button.set_text(self.game.format_food_gathering(), GREY) # Set text grey
            else:
                self.food_button.change(assets.SQUARE_PLUS_FOOD)
                self.food_button.set_text(self.game.format_food_gathering())
            self.wood_button.draw(self.display)
            ## Central food+ button
            self.food_button.draw(self.display)

    # --------------------> 🪓 MANAGE 🪓 <---------------------------------------------

    def loop_manage_menu(self) -> None:
        """ Executed at the start of every loop in the manage menu """
        if self.current_menu == self.MANAGE:

            fast_buy = lambda collide: collide * (((pygame.time.get_ticks() - self.press_time) // 1000) ** 2)
            if self.press_time > 0: # Fast buy when long press button
                self.game.increment_population(fast_buy(self.pop_plus.collide(self.mouse)))
                self.game.increment_harvester(fast_buy(self.harvester_plus.collide(self.mouse)))
                self.game.decrement_harvester(fast_buy(self.harvester_minus.collide(self.mouse)))
                self.game.increment_lumber(fast_buy(self.lumber_plus.collide(self.mouse)))
                self.game.decrement_lumber(fast_buy(self.lumber_minus.collide(self.mouse)))

    def event_manage_menu(self, event: pygame.event) -> None:
        """ Manage user event in the manage menu """
        if self.current_menu == self.MANAGE:

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.press_time == 0: # Save time when start pressing button
                    self.press_time = pygame.time.get_ticks()

            if event.type == pygame.MOUSEBUTTONUP:
                press_time = self.press_time
                self.press_time = 0
                if pygame.time.get_ticks() - press_time > 1000:
                    return # Otherwise this will buy an item more when relasing the button

                self.game.increment_population(self.pop_plus.collide(self.mouse))
                self.game.increment_harvester(self.harvester_plus.collide(self.mouse))
                self.game.decrement_harvester(self.harvester_minus.collide(self.mouse))
                self.game.increment_lumber(self.lumber_plus.collide(self.mouse))
                self.game.decrement_lumber(self.lumber_minus.collide(self.mouse))

    def draw_manage_menu(self) -> None:
        """ Draw button in the manage menu """
        if self.current_menu == self.MANAGE:

            ## Harvester buttons
            self.harvester_tag.draw(self.display, text = self.game.format_harvester())
            self.harvester_plus.draw(self.display)
            self.harvester_minus.draw(self.display)
            ## Lumber buttons
            self.lumber_tag.draw(self.display, text = self.game.format_lumber())
            self.lumber_plus.draw(self.display)
            self.lumber_minus.draw(self.display)
            ## Population+ button and cost
            self.pop_cost.draw(self.display, text = self.game.format_population_cost())
            self.pop_plus.draw(self.display)
            
    # --------------------> 🏡 CITY 🏡 <---------------------------------------------

    def loop_city_menu(self) -> None:
        """ Executed at the start of every loop in the city menu """
        if self.current_menu == self.CITY:

            y_mov = 0
            if self.starting_position != (0, 0):
                y_mov = self.mouse[1] - self.starting_position[1] # If y_mov up image down
                self.starting_position = self.mouse
            elif self.building0.y > 0:
                y_mov = -1 * max(self.building1.y / 5, 1) # Slowly pushes queue up
            self.building0.move(down = y_mov, lock = True, max_w = self.building_frame.w, max_h = self.building_frame.h)
            self.building1.y = self.building0.y + self.building0.h + 5
            self.building2.y = self.building1.y + self.building1.h + 5

    def event_city_menu(self, event: pygame.event) -> None:
        """ Manage user event in the city menu """
        if self.current_menu == self.CITY:

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.building_frame.collide(self.mouse) and self.starting_position == (0, 0):
                    self.starting_position = self.mouse

            if event.type == pygame.MOUSEBUTTONUP:
                self.starting_position = (0, 0)
                self.game.increment_house(self.house_plus.collide(self.mouse))
                self.game.increment_granary(self.granary_plus.collide(self.mouse))
                self.game.increment_storage(self.storage_plus.collide(self.mouse))

    def draw_city_menu(self) -> None:
        """ Draw button in the city menu """
        if self.current_menu == self.CITY:

            self.building_frame.change()

            house_enabled = (self.game.wood >= self.game.house_cost() and self.game.event_list.count_event_type("Building") < 3)
            self.house_plus.change(assets.RIGHT_ARROW_PLUS if house_enabled else assets.RIGHT_ARROW_PLUS_DISABLED)
            self.square_house.draw(self.display, text = int(self.game.house))
            self.house_cost.draw(self.display, text = self.game.format_house_cost())
            self.house_plus.draw(self.display)

            granary_enabled = (self.game.wood >= self.game.granary_cost() and self.game.event_list.count_event_type("Building") < 3)
            self.granary_plus.change(assets.RIGHT_ARROW_PLUS if granary_enabled else assets.RIGHT_ARROW_PLUS_DISABLED)
            self.square_granary.draw(self.display, text = int(self.game.granary))
            self.granary_cost.draw(self.display, text = self.game.format_granary_cost())
            self.granary_plus.draw(self.display)

            storage_enabled = (self.game.wood >= self.game.storage_cost() and self.game.event_list.count_event_type("Building") < 3)
            self.storage_plus.change(assets.RIGHT_ARROW_PLUS if storage_enabled else assets.RIGHT_ARROW_PLUS_DISABLED)
            self.square_storage.draw(self.display, text = int(self.game.storage))
            self.storage_cost.draw(self.display, text = self.game.format_storage_cost())
            self.storage_plus.draw(self.display)

            if self.game.event_list.event_type_exist("Building"):
                image = {
                    "House": self.house,
                    "Granary": self.granary,
                    "Storage": self.storage
                }

                if len(self.game.event_list.building_queue()) > 0:
                    self.building0.change()
                    building0 = self.game.event_list.building_queue()[0]
                    image[building0.name].draw(self.building0.picture)
                    self.building0.draw(self.building_frame.picture, text = building0.format_lasting_time())
                if len(self.game.event_list.building_queue()) > 1:
                    self.building1.change()
                    building1 = self.game.event_list.building_queue()[1]
                    image[building1.name].draw(self.building1.picture)
                    self.building1.draw(self.building_frame.picture, text = building1.format_lasting_time())
                if len(self.game.event_list.building_queue()) > 2:
                    self.building2.change()
                    building2 = self.game.event_list.building_queue()[2]
                    image[building2.name].draw(self.building2.picture)
                    self.building2.draw(self.building_frame.picture, text = building2.format_lasting_time())

                self.building_frame.draw(self.display)