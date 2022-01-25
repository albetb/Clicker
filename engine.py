from enum import Enum, unique
import utils

@unique
class GameStats(str, Enum):
    food = "food"
    wood = "wood"
    harvester = "harvester"
    lumber = "lumber"
    population = "population"

class Game:
    def __init__(self, population: int, food: float, wood: float, harvester: int, lumber: int) -> None:
        self.population = population
        self.food = food
        self.wood = wood
        self.harvester = harvester
        self.lumber = lumber

    def production(self, stat: GameStats) -> int:
        if stat == GameStats.harvester:
            data = self.harvester
        elif stat == GameStats.lumber:
            data = self.lumber
        else:
            raise RuntimeError("cannot call production on food and wood")

        return 0.05 * (data ** 1.05) * (1 + (data // 10) * 0.5)

    def harvester_production_per_second(self, clocks_per_second: int):
        value = (self.production(GameStats.harvester) - 0.005 * self.population) * clocks_per_second
        return utils.display_number(value, "high") + "/s"

    def lumber_production_per_second(self, clocks_per_second: int):
        value = self.production(GameStats.lumber) * clocks_per_second * 0.8
        return utils.display_number(value, "high") + "/s"

    def population_cost(self) -> float:
        return round(((self.population + 1) * 50) ** 1.1)

    def increment_food(self, dry_run = False) -> float:
        value = 10 + self.harvester ** 1.5
        if not dry_run:
            self.food += value
        return value

    def format_harvester(self):
        return utils.display_number(self.harvester)

    def format_lumber(self):
        return utils.display_number(self.lumber)

    def get_earn_per_click(self) -> str:
        value = self.increment_food(dry_run=True)
        return utils.display_number(value, "high")

    def autominer(self):
        self.food = round(self.food + self.production(GameStats.harvester) - self.population * 0.005, 3)
        self.wood = round(self.wood + 0.8 * self.production(GameStats.lumber), 3)

    def serialize(self) -> str:
        return f"{self.population}$${self.food}$${self.harvester}$${self.wood}$${self.lumber}"

    def increment_population(self):
        if self.food >= self.population_cost():
            self.food -= self.population_cost()
            self.population += 1

    def increment_harvester(self):
        if self.population > self.harvester + self.lumber:
            self.harvester += 1

    def decrement_harvester(self):
        if self.harvester > 0:
            self.harvester -= 1

    def increment_lumber(self):
        if self.population > self.harvester + self.lumber:
            self.lumber += 1

    def decrement_lumber(self):
        if self.lumber > 0:
            self.lumber -= 1

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