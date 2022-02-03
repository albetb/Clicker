from enum import Enum, unique
import events
import json
from math import log10, floor

FRAME_PER_SECOND = 60
OFFLINE_PRODUCTION_MULTIPLIER = 0.8
MAX_OFFLINE_TIME = 60 * 60 * 24 # In seconds

def load_game():
    """ Load a game from a .txt file """
    try:
        with open('savegame.txt', 'r') as file:
            return Game.deserialize(json.load(file))
    except:
        return Game()

@unique
class GameStats(str, Enum):
    food = "food"
    wood = "wood"
    harvester = "harvester"
    lumber = "lumber"
    population = "population"
    house = "house"

class Game:
    def __init__(self, population: int = 0, food: float = 0, wood: float = 0, harvester: int = 0, lumber: int = 0, house: int = 0, time: str = "", event_list = "") -> None:
        self.fps = FRAME_PER_SECOND
        self.population = population
        self.time = time
        self.harvester = harvester
        self.lumber = lumber
        self.food = food
        self.wood = wood
        self.house = house
        self.event_list = events.EventQueue()

        # Offline production
        if self.time != "":
            offline_production = min(events.offline_time(self.time), MAX_OFFLINE_TIME) * self.fps * OFFLINE_PRODUCTION_MULTIPLIER
            self.food += self.harvester_production() * offline_production / self.fps
            self.wood += self.lumber_production() * offline_production / self.fps

        # Initialize event list
        if event_list != "":
            self.event_list.deserialize_event_list(event_list)
            self.init_event()

    # ----------> Save game <----------------------------------------

    def save_current_time(self) -> None:
        """ Save current time as a formatted string in self.time """
        self.time = events.current_time()

    def save_game(self):
        """ Save the current game to a .txt file as JSON """
        with open('savegame.txt', 'w+') as file:
            file.write(json.dumps(self.serialize()))

    def serialize(self) -> dict:
        """ Serialize game stats as a dictionary to save it in a JSON file """
        return {
            "population": self.population,
            "resource": {
                "food": self.food,
                "wood": self.wood
                },
            "building": {
                "house": self.house
                },
            "occupation": {
                "harvester": self.harvester,
                "lumber": self.lumber
                },
            "time": self.time,
            "event_list": self.event_list.serialize_event_list()
            }

    @classmethod
    def deserialize(cls, data: str):
        """ Deserialize game stats and return it as a Game class,
            if there is some error load new game """
        try:
            if len(data) != 0:
                population = data["population"]
                food = data["resource"]["food"]
                wood = data["resource"]["wood"]
                harvester = data["occupation"]["harvester"]
                lumber = data["occupation"]["lumber"]
                house = data["building"]["house"]
                time = data["time"]
                event_list = data["event_list"]
                return cls(population, food, wood, harvester, lumber, house, time, event_list)
        except:
            pass
        return cls()

    # ----------> Production <----------------------------------------

    def production(self, stat: GameStats) -> int:
        """ Base function for worker production calculation, 
            return production PER SECOND for a resource """
        stats = {
            GameStats.harvester: self.harvester,
            GameStats.lumber: self.lumber
        }
        return stats[stat] ** 1.05 * (1 + (stats[stat] // 10) * 0.5)

    def harvester_production(self) -> int:
        """ Return food production PER SECOND from harvester minus population eating food """
        return self.production(GameStats.harvester) - 0.1 * self.population

    def lumber_production(self) -> int:
        """ Return wood production PER SECOND from lumber """
        return self.production(GameStats.lumber) * 0.8

    def population_cost(self) -> int:
        """ Return cost in food for a unit of population """
        return int(round(50 * 1.1 ** self.population))

    def house_cost(self) -> int:
        """ Return cost in wood for a house """
        return int(round(1000 * 1.2 ** self.house))

    def population_limit(self) -> int:
        """ Return population limit """
        return int(10 * (1 + self.house))

    def food_gathering(self, dry_run: bool = False) -> float:
        """ Add food when the central button is clicked, 
            if dry_run is True return food production,
            don't work during wood gathering  """
        value = 10 + self.harvester ** 1.5
        if not dry_run and not self.event_list.event_exist("WoodPlus"):
            self.food += value
        return value

    def wood_gathering(self) -> None:
        """ Add wood after a period of time, clicking again the button shorten that time,
            disable food gathering button, time delta is 2 min + 1 sec * lumberer """
        if not self.event_list.event_exist("WoodPlusDebuff"):
            if self.event_list.event_exist("WoodPlus"):
                self.event_wood_plus_production(seconds = 2)
                self.event_list.select_event("WoodPlus").subtract_time(seconds = 2)
            else:
                self.event_list.push(events.Event("WoodPlus", "Resources", seconds = 2 * 60 + self.lumber))

    def autominer(self) -> None:
        """ Add food and wood for worker production, reduce food for people eating in harvester_production(),
            if food < -100 population is reduced """
        self.food += self.harvester_production() / self.fps
        self.wood += self.lumber_production() / self.fps
        if self.food < -100:
            self.food = 0
            self.population = max(0, self.population - 1)
            if self.harvester + self.lumber > self.population:
                if self.lumber == max(self.harvester, self.lumber):
                    self.lumber -= 1
                elif self.harvester == max(self.harvester, self.lumber):
                    self.harvester -= 1

    # ----------> Managing <----------------------------------------

    def employed(self) -> int:
        """ Return number of people working """
        return int(self.harvester + self.lumber)

    def unemployed(self) -> int:
        """ Return number of people NOT working """
        return int(self.population - self.employed())

    # Some function are made with this "for _ in range(num)" for working with fast buying when a button is long pressed
    def increment_population(self, num: int = 1) -> None:
        """ Add a number of people to total population, food will be subtracted """
        for _ in range(num):
            if self.food >= self.population_cost() and self.population < self.population_limit():
                self.food -= self.population_cost()
                self.population += 1

    def increment_harvester(self, num: int = 1) -> None:
        """ Add a number of people to harvester """
        self.harvester += min(self.unemployed(), int(num))

    def decrement_harvester(self, num: int = 1) -> None:
        """ Subtract a number of people to harvester """
        self.harvester -= min(self.harvester, int(num))

    def increment_lumber(self, num: int = 1) -> None:
        """ Add a number of people to lumber """
        lumber_plus = min(self.unemployed(), int(num))
        self.lumber += lumber_plus
        if self.event_list.event_exist("WoodPlus"):
            self.event_list.select_event("WoodPlus").add_time(seconds = lumber_plus)

    def decrement_lumber(self, num: int = 1) -> None:
        """ Subtract a number of people to lumber """
        lumber_minus = min(self.lumber, int(num))
        self.lumber -= lumber_minus
        if self.event_list.event_exist("WoodPlus"):
            self.event_list.select_event("WoodPlus").subtract_time(seconds = lumber_minus)

    def increment_house(self, check: bool) -> None:
        """ Add a house to production, will be added after some times """
        if check and self.wood >= self.house_cost() and not self.event_list.event_type_exist("Building"):
            self.wood -= self.house_cost()
            self.event_list.push(events.Event("House", "Building", counter = 1, minutes = self.house + 1))

    # ----------> Formatting <----------------------------------------

    def format_food(self) -> str:
        """ Return food as a formatted string for displaying """
        return self.format_number(self.food)

    def format_wood(self) -> str:
        """ Return wood as a formatted string for displaying """
        return self.format_number(self.wood)

    def format_population(self) -> str:
        """ Return population/max_populaation as a formatted string for displaying """
        return f"{self.format_number(self.population)}/{self.format_population_limit()}"

    def format_food_gathering(self) -> str:
        """ Return food produced form food gathering as a formatted string for displaying """
        return self.format_number(self.food_gathering(dry_run=True), "high")
        
    def format_harvester(self) -> str:
        """ Return harvester as a formatted string for displaying """
        return self.format_number(self.harvester)

    def format_lumber(self) -> str:
        """ Return lumber as a formatted string for displaying """
        return self.format_number(self.lumber)

    def format_harvester_production(self) -> str:
        """ Return a formatted string for displaying food production """
        return self.format_number(self.harvester_production(), "high") + "/s"

    def format_lumber_production(self) -> str:
        """ Return a formatted string for displaying wood production """
        return self.format_number(self.lumber_production(), "high") + "/s"

    def format_population_cost(self) -> str:
        """ Return population cost as a formatted string for displaying """
        return self.format_number(self.population_cost())

    def format_population_limit(self) -> str:
        """ Return population limit as a formatted string for displaying """
        return self.format_number(self.population_limit())
    
    def format_house_cost(self) -> str:
        """ Return house cost as a formatted string for displaying """
        return f"{events.format_time_delta_str(minutes = (self.house + 1))} - {self.format_number(self.house_cost())}"
        
    def format_number(self, num: float, precision: str = "low") -> str:
        """ Display a number with less decimal and with a literal notation (es 20k),
            precision 'low' and 'high' determine number of decimal with number < 1000 """
        if num < 1000 and (precision == "low" or num == round(num)):
            return str(int(floor(num)))
        suffix = "", "k", "M", "B", "T"
        position = floor(log10(max(num, 1))) // 3
        return f"{round(num / (10 ** (position * 3)), 2)}{suffix[position]}"

    # ----------> Events <----------------------------------------

    def manage_event(self) -> None:
        """ Manage event list every tick, for adding value to counter or checking if an event is expired """
        if len(self.event_list.expired_event()) > 0:
            for event in self.event_list.expired_event():
                if event.name == "WoodPlus":
                    self.wood += event.counter
                    self.event_list.push(events.Event("WoodPlusDebuff", "Debuff", seconds = 3)) # Can't reactivate gathering wood for 3 sec
                if event.name == "House":
                    self.house += event.counter
            self.event_list.remove_expired()

        if self.event_list.event_exist("WoodPlus"):
            self.event_wood_plus_production(tick = 1)

    def init_event(self) -> None:
        """ Init event at the start of the game, add value to counter for time passed """
        if self.event_list.event_exist("WoodPlus"):
            if self.event_list.select_event("WoodPlus").is_event_passed():
                time_elapsed = self.event_list.select_event("WoodPlus").ending_time() - events.get_time(self.time)
            else:
                time_elapsed = events.now() - events.get_time(self.time)
            self.event_wood_plus_production(seconds = time_elapsed.seconds)

    def event_wood_plus_production(self, seconds: int = 0, tick: int = 0) -> None:
        """ Add value to counter of the wood gathering event, depends to the number of lumber """
        if self.event_list.event_exist("WoodPlus"):
            total_time = seconds * self.fps + tick
            self.event_list.select_event("WoodPlus").counter += total_time * (0.2 + self.lumber_production() * 0.5 / self.fps)