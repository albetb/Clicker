from datetime import timedelta
from enum import Enum, unique
import utils
import events

OFFLINE_PRODUCTION_MULTIPLIER = 0.9
FRAME_PER_SECOND = 10
MAX_OFFLINE_TIME = 60 * 60 * 24 # In seconds

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
        self.event_list = events.EventList()

        # Add a value to resources for offline production
        if self.time != "":
            offline_production = min(events.offline_time(self.time), MAX_OFFLINE_TIME) * self.fps * OFFLINE_PRODUCTION_MULTIPLIER
            self.food += self.harvester_production() * offline_production
            self.wood += self.lumber_production() * offline_production

        # Initialize event list
        if event_list != "":
            self.event_list.deserialize_event_list(event_list)
            self.init_event()

    # ----------> Save game <----------------------------------------

    def save_current_time(self) -> None:
        """ Save current time as a formatted string in self.time """
        self.time = events.current_time()
        
    def serialize(self) -> str:
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
            return production PER FRAME for a resource """
        stats = {
            GameStats.harvester: self.harvester,
            GameStats.lumber: self.lumber
        }
        return 0.05 * stats[stat] ** 1.05 * (1 + (stats[stat] // 10) * 0.5)

    def harvester_production(self) -> int:
        """ Return food production PER FRAME from harvester minus population eating food """
        return self.production(GameStats.harvester) - 0.005 * self.population

    def harvester_production_per_second(self) -> str:
        """ Return a formatted string for displaying food production """
        return utils.format_number(self.harvester_production() * self.fps, "high") + "/s"

    def lumber_production(self) -> int:
        """ Return wood production PER FRAME from lumber """
        return self.production(GameStats.lumber) * 0.8

    def lumber_production_per_second(self) -> str:
        """ Return a formatted string for displaying wood production """
        return utils.format_number(self.lumber_production() * self.fps, "high") + "/s"

    def population_cost(self) -> int:
        """ Return cost in food for a unit of population """
        return int(round(50 * 1.1 ** self.population))

    def format_population_cost(self) -> str:
        """ Return population cost as a formatted string for displaying """
        return utils.format_number(self.population_cost())

    def house_cost(self) -> int:
        """ Return cost in wood for a house """
        return int(round(150 * 1.2 ** self.house))
    
    def format_house_cost(self) -> str:
        """ Return house cost as a formatted string for displaying """
        return f"{events.format_time_delta_str(minutes = (self.house + 1))} - {utils.format_number(self.house_cost())}"

    def population_limit(self) -> int:
        """ Return population limit """
        return int(10 * (1 + self.house))

    def format_population_limit(self) -> str:
        """ Return population limit as a formatted string for displaying """
        return utils.format_number(self.population_limit())
        
    def format_harvester(self) -> str:
        """ Return harvester as a formatted string for displaying """
        return utils.format_number(self.harvester)

    def format_lumber(self) -> str:
        """ Return lumber as a formatted string for displaying """
        return utils.format_number(self.lumber)

    def food_gathering(self, dry_run = False) -> float:
        """ Add food when the central button is clicked, 
            if dry_run is True return food production,
            don't work during wood gathering  """
        value = 10 + self.harvester ** 1.5
        if not dry_run and not self.event_list.event_exist("WoodPlus"):
            self.food += value
        return value

    def format_food_gathering(self) -> str:
        """ Return food produced form food gaathering as a formatted string for displaying """
        value = self.food_gathering(dry_run=True)
        return utils.format_number(self.food_gathering(dry_run=True), "high")

    def wood_gathering(self) -> None:
        """ Add wood after a period of time, clicking again the button shorten that time,
            disable food gathering button, time delta is 2 min + 1 sec * lumberer """
        if not self.event_list.event_exist("WoodPlusDebuff"):
            if self.event_list.event_exist("WoodPlus"):
                self.event_wood_plus_production(seconds = 2)
                self.event_list.select_event("WoodPlus").subtract_time(seconds = 2)
            else:
                time_delta_seconds = 2 * 60 + self.lumber
                self.event_list.push(events.Event("WoodPlus", "Resources", seconds = time_delta_seconds))

    def autominer(self) -> None:
        """ Add food and wood for worker production, reduce food for people eating in harvester_production(),
            if food < -100 population is reduced """
        self.food = round(self.food + self.harvester_production(), 3)
        self.wood = round(self.wood + self.lumber_production(), 3)
        if self.food < -100:
            self.population = max(0, self.population - 1)
            self.food += 100

    # ----------> Managing <----------------------------------------

    # Some function are made with this "for _ in range(num)" for working with fast buying when a button is long pressed
    def increment_population(self, num = 1) -> None:
        """ Add a number of people to total population, food will be subtracted """
        for _ in range(num):
            if self.food >= self.population_cost() and self.population < self.population_limit():
                self.food -= self.population_cost()
                self.population += 1

    def increment_harvester(self, num = 1) -> None:
        """ Add a number of people to harvester """
        for _ in range(num):
            self.harvester += self.population > self.harvester + self.lumber

    def decrement_harvester(self, num = 1) -> None:
        """ Subtract a number of people to harvester """
        for _ in range(num):
            self.harvester -= self.harvester > 0

    def increment_lumber(self, num = 1) -> None:
        """ Add a number of people to lumber """
        for _ in range(num):
            if self.population > self.harvester + self.lumber:
                self.lumber += 1
                if self.event_list.event_exist("WoodPlus"):
                    self.event_list.select_event("WoodPlus").add_time(seconds = 1)

    def decrement_lumber(self, num = 1) -> None:
        """ Subtract a number of people to lumber """
        for _ in range(num):
            if self.lumber > 0:
                self.lumber -= 1
                if self.event_list.event_exist("WoodPlus"):
                    self.event_list.select_event("WoodPlus").subtract_time(seconds = 1)

    def increment_house(self, check) -> None:
        """ Add a house to production, will be added after some times """
        if check and not self.event_list.event_exist("BuyHouse") and self.wood >= self.house_cost():
            self.wood -= self.house_cost()
            self.event_list.push(events.Event("BuyHouse", "Construction", counter = 1, minutes = self.house + 1))

    def get_formatted_stats(self, stat: GameStats, precision = "low") -> str:
        """ Used for formatting stats, return a string for displaying the number """
        stats = {
            GameStats.harvester: self.harvester,
            GameStats.lumber: self.lumber,
            GameStats.food: self.food,
            GameStats.wood: self.wood,
            GameStats.population: self.population
        }
        return utils.format_number(stats[stat], precision)

    # ----------> Events <----------------------------------------

    def manage_event(self) -> None:
        """ Manage event list every tick, for adding value to counter or checking if an event is expired """
        if len(self.event_list.event_list) > 0:
            if len(self.event_list.expired_event()) > 0:
                for event in self.event_list.expired_event():
                    if event.name == "WoodPlus":
                        self.wood += event.counter
                        self.event_list.push(events.Event("WoodPlusDebuff", "Debuff", seconds = 3)) # Can't reactivate gathering wood for 3 sec
                    if event.name == "BuyHouse":
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

    def event_wood_plus_production(self, seconds = 0, tick = 0) -> None:
        """ Add value to counter of the wood gathering event, depends to the number of lumber """
        if self.event_list.event_exist("WoodPlus"):
            mult = seconds * self.fps + tick
            self.event_list.select_event("WoodPlus").counter += mult * (1 + round(self.lumber_production() * 0.5, 3))