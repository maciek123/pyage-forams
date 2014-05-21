from random import randint, choice, random

from pyage.core.inject import Inject


class Environment(object):
    @Inject("thermometer", "size")
    def __init__(self):
        super(Environment, self).__init__()
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[Cell(randint(0, 4) if random() > 0.7 else 0) for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                grid[i][j].neighbours.extend([grid[x][y] for x in range(max(0, i - 1), min(self.size, i + 2)) for y in
                                              range(max(0, j - 1), min(self.size, j + 2)) if x != i or j != j])

        return grid

    def add_foram(self, foram):
        choice(filter(lambda c: c.is_empty(), [cell for sublist in self.grid for cell in sublist])).insert_foram(foram)

    def tick(self):
        for row in self.grid:
            for cell in row:
                if cell.algae > 0:
                    cell.algae += 0.1
        while random() > 0.4:
            try:
                choice(filter(lambda c: c.is_empty(), choice(self.grid))).algae += 1 + random() * 2
            except:
                pass


class Cell(object):
    def __init__(self, algae=0):
        super(Cell, self).__init__()
        self.algae = algae
        self.foram = None
        self.neighbours = []

    def insert_foram(self, foram):
        if not self.is_empty():
            raise ValueError("cannot insert foram to already occupied cell")
        self.foram = foram
        foram.cell = self

    def remove_foram(self):
        foram = self.foram
        self.foram = None
        return foram

    def is_empty(self):
        return self.foram is None

    def take_algae(self, demand):
        to_let = min(demand, self.algae)
        self.algae -= to_let
        return to_let

    def available_food(self):
        return self.algae + sum(map(lambda c: c.algae, self.neighbours))

    def __repr__(self):
        return "%d, %s" % (self.algae, self.foram)

