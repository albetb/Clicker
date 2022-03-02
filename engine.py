from enum import Enum, unique
from json import load, dumps
from math import log10, floor
import events

FRAME_PER_SECOND = 60
OFFLINE_PRODUCTION_MULTIPLIER = 0.8
MAX_OFFLINE_TIME = 60 * 60 * 24 # In seconds

def load_game():
    """ Load a game from a .txt file """
    try:
        with open('savegame.txt', 'r') as file:
            return Game.deserialize(load(file))
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
    granary = "granary"
    storage = "storage"

class Game:
    def __init__(self, population: int = 0, food: float = 0, wood: float = 0, harvester: int = 0, lumber: int = 0, house: int = 0, granary: int = 0, storage: int = 0, time: str = "", events_list = "") -> None:
        self.fps = FRAME_PER_SECOND
        self.population = population
        self.time = time
        self.harvester = harvester
        self.lumber = lumber
        self.food = food
        self.wood = wood
        self.house = house
        self.granary = granary
        self.storage = storage
        self.events = events.Events()
        self.max_buildings = 3

        # Offline production
        if self.time != "":
            offline_production = min(events.offline_time(self.time), MAX_OFFLINE_TIME) * OFFLINE_PRODUCTION_MULTIPLIER
            self.food += self.harvester_production() * offline_production
            self.wood += self.lumber_production() * offline_production

        # Initialize event list
        if events_list != "":
            self.events.deserialize_events(events_list)
            self.init_event()

    # ----------> Save game <----------------------------------------

    def save_current_time(self) -> None:
        """ Save current time as a formatted string in self.time """
        self.time = events.current_time()

    def save_game(self):
        """ Save the current game to a .txt file as JSON """
        with open('savegame.txt', 'w+') as file:
            file.write(dumps(self.serialize()))

    def serialize(self) -> dict:
        """ Serialize game stats as a dictionary to save it in a JSON file """
        return {
            "population": self.population,
            "resource": {
                "food": self.food,
                "wood": self.wood
                },
            "building": {
                "house": self.house,
                "granary": self.granary,
                "storage": self.storage
                },
            "occupation": {
                "harvester": self.harvester,
                "lumber": self.lumber
                },
            "time": self.time,
            "events": self.events.serialize_events()
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
                granary = data["building"]["granary"]
                storage = data["building"]["storage"]
                time = data["time"]
                events = data["events"]
                return cls(population, food, wood, harvester, lumber, house, granary, storage, time, events)
        except:
            pass
        return cls()

    # ----------> Production <----------------------------------------

    def production(self, stat: GameStats) -> float:
        """ Base function for worker production calculation, 
            return production PER SECOND for a resource """
        stats = {
            GameStats.harvester: self.harvester,
            GameStats.lumber: self.lumber
        }
        return stats[stat] ** 1.05 * (1 + (stats[stat] // 10) * 0.5)

    def harvester_production(self) -> float:
        """ Return food production PER SECOND from harvester minus population eating food """
        return self.production(GameStats.harvester) - 0.1 * self.population

    def lumber_production(self) -> float:
        """ Return wood production PER SECOND from lumber """
        return self.production(GameStats.lumber) * 0.8

    def population_cost(self) -> int:
        """ Return cost in food for a unit of population """
        return int(round(50 * 1.1 ** self.population))

    def house_cost(self) -> int:
        """ Return cost in wood for a house """
        return int(round(1000 * 1.2 ** self.house_total()))

    def house_total(self) -> int:
        """ Return total house constructed + in construction """
        return self.house + self.events.count("House")

    def granary_cost(self) -> int:
        """ Return cost in wood for a granary """
        return int(round(3000 * 1.2 ** self.granary_total()))

    def granary_total(self) -> int:
        """ Return total granary constructed + in construction """
        return self.granary + self.events.count("Granary")

    def storage_cost(self) -> int:
        """ Return cost in wood for a storage """
        return int(round(8000 * (1 + self.storage_total())))

    def storage_total(self) -> int:
        """ Return total storage constructed + in construction """
        return self.storage + self.events.count("Storage")

    def population_limit(self) -> int:
        """ Return population limit """
        return int(10 * (1 + self.house))

    def food_limit(self) -> int:
        """ Return food limit """
        return int(round((1 + self.granary) ** 1.5) * 1000)

    def wood_limit(self) -> int:
        """ Return wood limit """
        return int(10000 * (1 + self.storage))

    def food_gathering(self, dry_run: bool = False) -> float:
        """ Add food when the central button is clicked, 
            if dry_run is True return food production,
            don't work during wood gathering  """
        value = 10 + self.harvester ** 1.5
        if not dry_run and not self.events.exist("WoodPlus"):
            self.food += value
        return value

    def wood_gathering(self) -> None:
        """ Add wood after a period of time, clicking again the button shorten that time,
            disable food gathering button, time delta is 2 min + 1 sec * lumberer """
        if not self.events.exist("WoodPlusDebuff"):
            if self.events.exist("WoodPlus"):
                self.event_wood_plus_production(seconds = 2)
                self.events.get("WoodPlus").subtract_time(seconds = 2)
            else:
                self.events.push(events.Event("WoodPlus", "Resources", seconds = 2 * 60 + self.lumber))

    def autominer(self) -> None:
        """ Add food and wood for worker production """
        if not self.events.exist("Food"):
            food_value = self.harvester_production()
            self.events.push(events.Event("Food", "Production", food_value, milliseconds = 1000))
        if not self.events.exist("Wood"):
            wood_value = self.lumber_production()
            self.events.push(events.Event("Wood", "Production", wood_value, milliseconds = 1000))
        self.starving()

    def starving(self) -> None:
        """ Reduce people if food is too low """
        if self.food < -100: # If food < -100 population is reduced
            self.food = 0
            self.population = max(0, self.population - 1)
            if self.unemployed() <= 0:
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
        lumber_added = min(self.unemployed(), int(num))
        self.lumber += lumber_added
        if self.events.exist("WoodPlus"):
            self.events.get("WoodPlus").add_time(seconds = lumber_added)

    def decrement_lumber(self, num: int = 1) -> None:
        """ Subtract a number of people to lumber """
        lumber_removed = min(self.lumber, int(num))
        self.lumber -= lumber_removed
        if self.events.exist("WoodPlus"):
            self.events.get("WoodPlus").subtract_time(seconds = lumber_removed)

    def increment_house(self, check: bool) -> None:
        """ Add a house to production, will be added after some times """
        if check and self.wood >= self.house_cost() and self.events.count_type("Building") < self.max_buildings:
            self.wood -= self.house_cost()
            self.events.push(events.Event("House", "Building", minutes = self.house_total() + 1))

    def increment_granary(self, check: bool) -> None:
        """ Add a granary to production, will be added after some times """
        if check and self.wood >= self.granary_cost() and self.events.count_type("Building") < self.max_buildings:
            self.wood -= self.granary_cost()
            self.events.push(events.Event("Granary", "Building", minutes = (self.granary_total() * 1.5) + 1))

    def increment_storage(self, check: bool) -> None:
        """ Add a storage to production, will be added after some times """
        if check and self.wood >= self.storage_cost() and self.events.count_type("Building") < self.max_buildings:
            self.wood -= self.storage_cost()
            self.events.push(events.Event("Storage", "Building", minutes = (self.storage_total() + 1) * 5))

    # ----------> Formatting <----------------------------------------

    def format_food(self) -> str:
        """ Return food as a formatted string for displaying """
        return f"{self.format_number(min(self.food, self.food_limit()))}/{self.format_number(self.food_limit())}"

    def format_wood(self) -> str:
        """ Return wood as a formatted string for displaying """
        return f"{self.format_number(min(self.wood, self.wood_limit()))}/{self.format_number(self.wood_limit())}"

    def format_population(self) -> str:
        """ Return population/max_populaation as a formatted string for displaying """
        return f"{self.format_number(self.population)}/{self.format_population_limit()}"

    def format_food_gathering(self) -> str:
        """ Return food produced form food gathering as a formatted string for displaying """
        return self.format_number(self.food_gathering(dry_run = True), "high")
        
    def format_harvester(self) -> str:
        """ Return harvester as a formatted string for displaying """
        return self.format_number(self.harvester)

    def format_lumber(self) -> str:
        """ Return lumber as a formatted string for displaying """
        return self.format_number(self.lumber)

    def format_harvester_production(self) -> str:
        """ Return food production as a formatted string for displaying """
        return self.format_number(self.harvester_production(), "high") + "/s"

    def format_lumber_production(self) -> str:
        """ Return wood production as a formatted string for displaying """
        return self.format_number(self.lumber_production(), "high") + "/s"

    def format_population_cost(self) -> str:
        """ Return population cost as a formatted string for displaying """
        return self.format_number(self.population_cost())

    def format_population_limit(self) -> str:
        """ Return population limit as a formatted string for displaying """
        return self.format_number(self.population_limit())
    
    def format_house_cost(self) -> str:
        """ Return house cost as a formatted string for displaying """
        return f"{events.format_time_delta_str(minutes = (self.house_total() + 1))} - {self.format_number(self.house_cost())}"

    def format_granary_cost(self) -> str:
        """ Return granary cost as a formatted string for displaying """
        return f"{events.format_time_delta_str(minutes = (self.granary_total() * 1.5) + 2)} - {self.format_number(self.granary_cost())}"

    def format_storage_cost(self) -> str:
        """ Return storage cost as a formatted string for displaying """
        return f"{events.format_time_delta_str(minutes = (self.storage_total() + 1) * 5)} - {self.format_number(self.storage_cost())}"
        
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
        events_expired = self.events.expired()
        self.events.remove_expired()
        if len(events_expired) > 0:
            for event in events_expired:
                match event.name:
                    case "Food":
                        self.food = round(min(self.food + event.counter, self.food_limit()), 2)
                    case "Wood":
                        self.wood = round(min(self.wood + event.counter, self.wood_limit()), 2)
                    case "WoodPlus":
                        self.wood = round(min(self.wood + event.counter, self.wood_limit()), 2)
                        self.events.push(events.Event("WoodPlusDebuff", "Debuff", seconds = 3)) # Can't reactivate gathering wood for 3 sec
                    case "House":
                        self.house += 1
                    case "Granary":
                        self.granary += 1
                    case "Storage":
                        self.storage += 1

        if self.events.exist("WoodPlus"):
            self.event_wood_plus_production(tick = 1)

    def init_event(self) -> None:
        """ Init event at the start of the game, add value to counter for time passed """
        if self.events.exist("WoodPlus"):
            end_time = events.now()
            if self.events.get("WoodPlus").is_passed():
                end_time = self.events.get("WoodPlus").ending_time()
            time_elapsed = end_time - events.get_time(self.time)
            self.event_wood_plus_production(seconds = time_elapsed.seconds)

    def event_wood_plus_production(self, seconds: int = 0, tick: int = 0) -> None:
        """ Add value to counter of the wood gathering event, depends to the number of lumber """
        if self.events.exist("WoodPlus"):
            total_time = seconds * self.fps + tick
            self.events.get("WoodPlus").counter += total_time * (0.2 + self.lumber_production() * 0.5 / self.fps)
