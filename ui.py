import pygame
import assets
from engine import load_game

class Ui:
    EXPLORE = 0
    MANAGE = 1
    CITY = 2

    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()

        self.display_width = 1024
        self.display_height = self.display_width * 3 // 4 # Display aspect ratio 4:3
        self.display = pygame.display.set_mode((self.display_width, self.display_height))
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
        self.background = assets.Image(assets.BACKGROUND_EXPLORE, 0, 0, self.display_width, self.display_height)
        # Lambdas who calculate button heigth given width
        large_h = lambda large_w: large_w * 100 // 275
        tag_h = lambda large_w: large_w * 100 // 190
        square_h = lambda square_w: square_w * 109 // 100
        round_h = lambda round_w: round_w * 103 // 100
        arrow_h = lambda round_w: round_w * 100 // 80
        # Central button, give food when clicked
        food_w = 200
        self.food_button = assets.Image(assets.SQUARE_PLUS_FOOD, (self.display_width - food_w) / 2, (self.display_height - square_h(food_w)) / 2, square_h(food_w), food_w, 0, 0.5, 0.68)
        # Wood button
        self.wood_timer = assets.Image(assets.LARGE, self.display_width * 0.7 + food_w * 0.25, (self.display_height - square_h(food_w)) / 2 + (round_h(food_w * 0.5) - large_h(food_w * 0.8)) / 2, food_w * 0.8, large_h(food_w * 0.8), "", 0.58, 0.55)
        self.wood_button = assets.Image(assets.ROUND_WOOD, self.display_width * 0.7, (self.display_height - square_h(food_w)) / 2, food_w * 0.5, round_h(food_w * 0.5))
        # Bottom menu button
        menu_w = 275
        self.manage_menu = assets.Image(assets.LARGE, (self.display_width - 3 * menu_w) // 4, self.display_height - large_h(menu_w) - 20, menu_w, large_h(menu_w), "Manage")
        self.explore_menu = assets.Image(assets.LARGE, (self.display_width - 3 * menu_w) * 2 // 4 + menu_w, self.display_height - large_h(menu_w) - 20, menu_w, large_h(menu_w), "Explore")
        self.city_menu = assets.Image(assets.LARGE, (self.display_width - 3 * menu_w) * 3 // 4 + 2 * menu_w, self.display_height - large_h(menu_w) - 20, menu_w, large_h(menu_w), "City")
        self.manage_menu.set_text_size(30)
        self.explore_menu.set_text_size(30)
        self.city_menu.set_text_size(30)
        # Tag with current resources
        resource_w = 190
        production_w = resource_w * 0.9
        self.food_tag = assets.Image(assets.TAG_FOOD, (self.display_width - 3 * 1.5 * resource_w) // 4, 20, resource_w, tag_h(resource_w), 0, 0.4, 0.45)
        self.food_prod_tag = assets.Image(assets.LARGE, (self.display_width - 3 * 1.5 * resource_w) // 4 + resource_w * 0.7, 30, production_w, large_h(production_w), 0, 0.65, 0.55)
        self.food_prod_tag.set_text_size(22)
        self.teg_wood = assets.Image(assets.TAG_WOOD, (self.display_width - 3 * 1.5 * resource_w) * 2 // 4 + 1.5 * resource_w, 20, resource_w, tag_h(resource_w), 0, 0.4, 0.45)
        self.wood_prod_tag = assets.Image(assets.LARGE, (self.display_width - 3 * 1.5 * resource_w) * 2 // 4 + 1.5 * resource_w + resource_w * 0.7, 30, production_w, large_h(production_w), 0, 0.65, 0.55)
        self.wood_prod_tag.set_text_size(22)
        self.tag_population = assets.Image(assets.TAG_POPULATION, (self.display_width - 3 * 1.5 * resource_w) // 4, 20 + 15 + tag_h(resource_w), resource_w, tag_h(resource_w), 0, 0.4, 0.45)
        # Buy population button and cost
        arrow_w = 80
        self.pop_plus = assets.Image(assets.RIGHT_ARROW_PLUS, (self.display_width - 3 * 1.5 * resource_w) // 4 + resource_w + 15 + menu_w * 0.85 + 7, 20 + 15 + 9 + tag_h(resource_w), arrow_w * 0.7, arrow_h(arrow_w * 0.7))
        self.pop_cost = assets.Image(assets.LARGE_FOOD, (self.display_width - 3 * 1.5 * resource_w) // 4 + resource_w + 15, 20 + 15 + tag_h(resource_w), menu_w * 0.85, large_h(menu_w * 0.85), 0, 0.4)
        # Worker menu
        worker_x, worker_y = 70, 280
        self.harvester_tag = assets.Image(assets.LARGE_HARVESTER, worker_x, worker_y, menu_w, large_h(menu_w), 0, 0.4)
        self.harvester_minus = assets.Image(assets.LEFT_ARROW_MINUS, worker_x + menu_w + 8, worker_y, arrow_w, arrow_h(arrow_w))
        self.harvester_plus = assets.Image(assets.RIGHT_ARROW_PLUS, worker_x + menu_w + arrow_w + 8 * 2, worker_y, arrow_w, arrow_h(arrow_w))
        self.lumber_tag = assets.Image(assets.LARGE_LUMBERER, worker_x, worker_y + large_h(menu_w) + 10, menu_w, large_h(menu_w), 0, 0.4)
        self.lumber_minus = assets.Image(assets.LEFT_ARROW_MINUS, worker_x + menu_w + 8, worker_y + large_h(menu_w) + 10, arrow_w, arrow_h(arrow_w))
        self.lumber_plus = assets.Image(assets.RIGHT_ARROW_PLUS, worker_x + menu_w + arrow_w + 8 * 2, worker_y + large_h(menu_w) + 10, arrow_w, arrow_h(arrow_w))
        # City menu
        self.building_frame = assets.Image(assets.FRAME, self.display_width * 0.625, self.display_height * 0.336, self.display_width * 0.273, self.display_height * 0.439)
        self.square_house = assets.Image(assets.SQUARE_HOUSE, worker_x, worker_y - 4, arrow_w * 1.3, square_h(arrow_w * 1.3), 0, 0.5, 0.46)
        self.house_cost = assets.Image(assets.LARGE_WOOD, worker_x + arrow_w * 1.3 + 8, worker_y, menu_w, large_h(menu_w), 0, 0.37)
        self.house_plus = assets.Image(assets.RIGHT_ARROW_PLUS, worker_x + arrow_w * 1.3 + menu_w + 2*  8, worker_y, arrow_w, arrow_h(arrow_w))
        self.house_time = assets.Image(assets.LARGE, (self.display_width * 0.273 - menu_w) / 2, 0, menu_w, large_h(menu_w), textx = 0.58)
        self.house = assets.Image(assets.HOUSE, large_h(menu_w) * 0.125, large_h(menu_w) * 0.125, large_h(menu_w) * 0.75, large_h(menu_w) * 0.75)

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
        self.city_menu.change(assets.LARGE_SELECTED if self.current_menu == self.CITY else assets.LARGE)
        self.explore_menu.change(assets.LARGE_SELECTED if self.current_menu == self.EXPLORE else assets.LARGE)
        self.manage_menu.change(assets.LARGE_SELECTED if self.current_menu == self.MANAGE else assets.LARGE)

        self.background.draw(self.display)
        self.city_menu.draw(self.display)
        self.explore_menu.draw(self.display)
        self.manage_menu.draw(self.display)

    def draw_counters(self) -> None:
        """ Update resources and production counter """
        # Food counter
        self.food_prod_tag.set_text(self.game.format_harvester_production())
        self.food_tag.set_text(self.game.format_food())
        self.food_prod_tag.draw(self.display)
        self.food_tag.draw(self.display)
        # Wood counter
        self.wood_prod_tag.set_text(self.game.format_lumber_production())
        self.teg_wood.set_text(self.game.format_wood())
        self.wood_prod_tag.draw(self.display)
        self.teg_wood.draw(self.display)
        # Population counter
        self.tag_population.set_text(self.game.format_population())
        self.tag_population.draw(self.display)

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
                self.wood_timer.set_text(self.game.event_list.select_event("WoodPlus").format_lasting_time())
                self.wood_timer.draw(self.display)
                self.food_button.change(assets.SQUARE_PLUS_FOOD_DISABLED)
                self.food_button.set_text(self.game.format_food_gathering(), (97, 83, 74)) # Set text grey
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
            self.harvester_tag.set_text(self.game.format_harvester())
            self.harvester_tag.draw(self.display)
            self.harvester_plus.draw(self.display)
            self.harvester_minus.draw(self.display)
            ## Lumber buttons
            self.lumber_tag.set_text(self.game.format_lumber())
            self.lumber_tag.draw(self.display)
            self.lumber_plus.draw(self.display)
            self.lumber_minus.draw(self.display)
            ## Population+ button and cost
            self.pop_cost.set_text(self.game.format_population_cost())
            self.pop_cost.draw(self.display)
            self.pop_plus.draw(self.display)
            
    # --------------------> 🏡 CITY 🏡 <---------------------------------------------

    def loop_city_menu(self) -> None:
        """ Executed at the start of every loop in the city menu """
        if self.current_menu == self.CITY:

            if self.starting_position != (0, 0):
                y_mov = self.mouse[1] - self.starting_position[1] # If y_mov up image down
                self.house_time.move(down = y_mov, lock = True, max_w = self.building_frame.w, max_h = self.building_frame.h)
                self.starting_position = self.mouse
            elif self.house_time.y > 0:
                y_mov = -1 * max(self.house_time.y / 5, 1) # Slowly pushes queue up
                self.house_time.move(down = y_mov, lock = True, max_w = self.building_frame.w, max_h = self.building_frame.h)

    def event_city_menu(self, event: pygame.event) -> None:
        """ Manage user event in the city menu """
        if self.current_menu == self.CITY:

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.building_frame.collide(self.mouse) and self.starting_position == (0, 0):
                    self.starting_position = self.mouse

            if event.type == pygame.MOUSEBUTTONUP:
                self.starting_position = (0, 0)
                self.game.increment_house(self.house_plus.collide(self.mouse))

    def draw_city_menu(self) -> None:
        """ Draw button in the city menu """
        if self.current_menu == self.CITY:

            self.building_frame.change()
            self.square_house.set_text(int(self.game.house))
            self.house_cost.set_text(self.game.format_house_cost())
            self.square_house.draw(self.display)
            self.house_cost.draw(self.display)

            if self.game.event_list.event_exist("House"):
                self.house_time.set_text(self.game.event_list.select_event("House").format_lasting_time())
                self.house.draw(self.house_time.picture)
                self.house_time.draw(self.building_frame.picture)
                self.house_plus.change(assets.RIGHT_ARROW_PLUS_DISABLED)
            else:
                self.house_plus.change(assets.RIGHT_ARROW_PLUS)

            self.building_frame.draw(self.display)
            self.house_plus.draw(self.display)