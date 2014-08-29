import logging
from random import randint, choice, random

from pyage.core.inject import Inject
from pyage_forams.solutions.cell import Cell


logger = logging.getLogger(__name__)


class AbstractEnvironment(object):
    @Inject("insolation_meter")
    def __init__(self, regeneration_factor):
        super(AbstractEnvironment, self).__init__()
        self.regeneration_factor = regeneration_factor

    def add_foram(self, foram):
        choice(filter(lambda c: c.is_empty(), self.get_all_cells())).insert_foram(foram)

    def tick(self):
        for cell in self.get_all_cells():
            if cell.get_algae() > 0:
                cell.add_algae(self.regeneration_factor + self.insolation_meter.get_insolation(cell))
        while random() > 0.4:
            try:
                choice(filter(lambda c: c.is_empty(), self.get_all_cells())).add_algae(1 + random() * 2)
            except:
                pass

    def get_cell(self, address):
        for cell in self.get_all_cells():
            if cell.get_address() == address:
                return cell

    def add_neighbour(self, cell_address, neighbour):
        self.get_cell(cell_address).add_neighbour(neighbour)


class Environment2d(AbstractEnvironment):
    @Inject("size")
    def __init__(self, regeneration_factor):
        super(Environment2d, self).__init__(regeneration_factor)
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[Cell(randint(0, 4) if random() > 0.7 else 0) for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                grid[i][j]._neighbours.extend([grid[x][y] for x in range(max(0, i - 1), min(self.size, i + 2)) for y in
                                               range(max(0, j - 1), min(self.size, j + 2)) if x != i or y != j])
        return grid

    def get_all_cells(self):
        for row in self.grid:
            for cell in row:
                yield cell

    # TODO some refactoring
    def get_left_cells(self):
        return [row[0] for row in self.grid]

    def get_right_cells(self):
        return [row[-1] for row in self.grid]

    def get_upper_cells(self):
        return self.grid[0]

    def get_lower_cells(self):
        return self.grid[-1]

    def join_left(self, cells):
        for (c1, c2) in zip(cells, self.get_left_cells()):
            c1.add_neighbour(c2)
            c2.add_neighbour(c1)

    def join_right(self, cells):
        for (c1, c2) in zip(cells, self.get_right_cells()):
            c1.add_neighbour(c2)
            c2.add_neighbour(c1)

    def join_upper(self, cells):
        for (c1, c2) in zip(cells, self.get_upper_cells()):
            c1.add_neighbour(c2)
            c2.add_neighbour(c1)

    def join_lower(self, cells):
        for (c1, c2) in zip(cells, self.get_lower_cells()):
            c1.add_neighbour(c2)
            c2.add_neighbour(c1)


class Environment3d(AbstractEnvironment):
    @Inject("size")
    def __init__(self, regeneration_factor):
        super(Environment3d, self).__init__(regeneration_factor)
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[[Cell(randint(1, 4) if random() > 0.7 else 0)
                  for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    grid[i][j][k].depth = i
                    grid[i][j][k]._neighbours.extend(
                        [grid[x][y][z] for x in range(max(0, i - 1), min(self.size, i + 2)) for y in
                         range(max(0, j - 1), min(self.size, j + 2)) for z in
                         range(max(0, k - 1), min(self.size, k + 2)) if x != i or y != j or z != k])

        return grid

    def get_all_cells(self):
        for plane in self.grid:
            for row in plane:
                for cell in row:
                    yield cell


def environment_factory(regeneration_factor=0.1, clazz=Environment2d):
    e = [None]

    def environ():
        if e[0] is None:
            e[0] = clazz(regeneration_factor)
        return e[0]

    return environ