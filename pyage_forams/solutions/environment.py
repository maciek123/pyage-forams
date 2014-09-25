from random import randint, choice, random

from pyage.core.inject import Inject


class AbstractEnvironment(object):
    @Inject("insolation_meter", "algae_limit", "initial_algae_probability")
    def __init__(self, regeneration_factor):
        super(AbstractEnvironment, self).__init__()
        self.regeneration_factor = regeneration_factor

    def add_foram(self, foram):
        choice(filter(lambda c: c.is_empty(), self.get_all_cells())).insert_foram(foram)

    def tick(self, step):
        for cell in self.get_all_cells():
            if 0 < cell.algae < self.algae_limit:
                cell.algae += self.regeneration_factor + self.insolation_meter.get_insolation(cell, step)
        while random() > 0.4:
            try:
                choice(filter(lambda c: c.is_empty(), self.get_all_cells())).algae += 1 + random() * 2
            except:
                pass


class Environment2d(AbstractEnvironment):
    @Inject("size")
    def __init__(self, regeneration_factor):
        super(Environment2d, self).__init__(regeneration_factor)
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[Cell(randint(0, 4) if random() < self.initial_algae_probability else 0) for _ in range(self.size)] for
                _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                grid[i][j].neighbours.extend([grid[x][y] for x in range(max(0, i - 1), min(self.size, i + 2)) for y in
                                              range(max(0, j - 1), min(self.size, j + 2)) if x != i or y != j])

        return grid

    def get_all_cells(self):
        for row in self.grid:
            for cell in row:
                yield cell


class Environment3d(AbstractEnvironment):
    @Inject("size")
    def __init__(self, regeneration_factor):
        super(Environment3d, self).__init__(regeneration_factor)
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[[Cell(randint(1, 4) if random() < self.initial_algae_probability else 0)
                  for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    grid[i][j][k].depth = self.size - k - 1
                    grid[i][j][k].neighbours.extend(
                        [grid[x][y][z] for x in range(max(0, i - 1), min(self.size, i + 2)) for y in
                         range(max(0, j - 1), min(self.size, j + 2)) for z in
                         range(max(0, k - 1), min(self.size, k + 2)) if x != i or y != j or z != k])

        return grid

    def get_all_cells(self):
        for plane in self.grid:
            for row in plane:
                for cell in row:
                    yield cell


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


def environment_factory(regeneration_factor=0.1, clazz=Environment2d):
    e = [None]

    def environ():
        if e[0] is None:
            e[0] = clazz(regeneration_factor)
        return e[0]

    return environ