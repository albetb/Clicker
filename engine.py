from enum import Enum, unique
import utils
import events

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
        self.fps = 10
        self.population = population
        self.food = food
        self.wood = wood
        self.harvester = harvester
        self.lumber = lumber
        self.house = house
        self.time = time
        self.event_list = events.EventList()
        if event_list != "":
            self.event_list.load_from_dict(event_list)
            self.init_event()

    def save_current_time(self):
        self.time = events.current_time()

    def production(self, stat: GameStats) -> int:
        if stat == GameStats.harvester:
            data = self.harvester
        elif stat == GameStats.lumber:
            data = self.lumber
        else:
            raise RuntimeError("cannot call production on food and wood")

        return 0.05 * data ** 1.05 * (1 + (data // 10) * 0.5)

    def harvester_production_per_second(self, clocks_per_second: int) -> str:
        value = (self.production(GameStats.harvester) - 0.005 * self.population) * clocks_per_second
        return utils.display_number(value, "high") + "/s"

    def lumber_production_per_second(self, clocks_per_second: int) -> str:
        value = self.production(GameStats.lumber) * clocks_per_second * 0.8
        return utils.display_number(value, "high") + "/s"

    def population_cost(self) -> float:
        return round(50 * 1.1 ** self.population)

    def format_population_cost(self) -> str:
        return utils.display_number(self.population_cost())

    def house_cost(self) -> float:
        return round(150 * 1.15 ** self.house)
    
    def format_house_cost(self) -> float:
        return f"{events.format_time_delta_str(minutes = (self.house + 1))} - {utils.display_number(self.house_cost())}"

    def population_limit(self) -> float:
        return int(10 * (1 + self.house))

    def format_population_limit(self) -> float:
        return utils.display_number(self.population_limit())

    def increment_food(self, dry_run = False) -> float:
        value = 10 + self.harvester ** 1.5
        if not dry_run and not self.event_list.event_exist("WoodPlus"):
            self.food += value
        return value

    def increment_wood(self):
        if not self.event_list.event_exist("WoodPlusDebuff"):
            if self.event_list.event_exist("WoodPlus"):
                self.event_wood_plus_production(seconds = 5)
                self.event_list.select_event("WoodPlus").subtract_time(seconds = 5)
            else:
                self.event_list.push(events.Event("WoodPlus", "Resources", minutes = 5))

    def format_harvester(self) -> str:
        return utils.display_number(self.harvester)

    def format_lumber(self) -> str:
        return utils.display_number(self.lumber)

    def get_earn_per_click(self) -> str:
        value = self.increment_food(dry_run=True)
        return utils.display_number(value, "high")

    def autominer(self):
        self.food = round(self.food + self.production(GameStats.harvester) - self.population * 0.005, 3)
        self.wood = round(self.wood + 0.8 * self.production(GameStats.lumber), 3)
        if self.food < -100:
            self.population = max(0, self.population - 1)
            self.food += 100

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

    def increment_population(self, num = 1):
        for _ in range(num):
            if self.food >= self.population_cost() and self.population < self.population_limit():
                self.food -= self.population_cost()
                self.population += 1

    def increment_harvester(self, num = 1):
        for _ in range(num):
            self.harvester += self.population > self.harvester + self.lumber

    def decrement_harvester(self, num = 1):
        for _ in range(num):
            self.harvester -= self.harvester > 0

    def increment_lumber(self, num = 1):
        for _ in range(num):
            self.lumber += self.population > self.harvester + self.lumber

    def decrement_lumber(self, num = 1):
        for _ in range(num):
            self.lumber -= self.lumber > 0

    def increment_house(self, check):
        if not self.event_list.event_exist("BuyHouse") and check and self.wood >= self.house_cost():
            self.wood -= self.house_cost()
            self.event_list.push(events.Event("BuyHouse", "Construction", counter = 1, minutes = self.house + 1))

    def get_formatted_stats(self, stat: GameStats, precision = "low") -> str:
        if stat == GameStats.harvester:
            data = self.harvester
        elif stat == GameStats.lumber:
            data = self.lumber
        elif stat == GameStats.food:
            data = self.food
        elif stat == GameStats.wood:
            data = self.wood
        elif stat == GameStats.population:
            data = self.population

        return utils.display_number(data, precision)

    def event_wood_plus_production(self, seconds = 0, tick = 1):
        if self.event_list.event_exist("WoodPlus"):
            mult = seconds * self.fps + tick
            self.event_list.select_event("WoodPlus").counter += mult * (1 + round(0.8 * self.production(GameStats.lumber), 3))

    def manage_event(self):
        if len(self.event_list.event_list) > 0:
            if len(self.event_list.check_expired()) > 0:
                for event in self.event_list.check_expired():
                    if event.name == "WoodPlus":
                        self.wood += event.counter
                        self.event_list.push(events.Event("WoodPlusDebuff", "Debuff", seconds = 3))
                    if event.name == "BuyHouse":
                        self.house += event.counter
                self.event_list.remove_expired()

            if self.event_list.event_exist("WoodPlus"):
                self.event_wood_plus_production()

    def init_event(self):
        if self.event_list.event_exist("WoodPlus"):
            if self.event_list.select_event("WoodPlus").is_event_passed():
                time_elapsed = self.event_list.select_event("WoodPlus").ending_time() - events.get_time(self.time)
            else:
                time_elapsed = events.now() - events.get_time(self.time)
            self.event_wood_plus_production(seconds = time_elapsed.seconds)