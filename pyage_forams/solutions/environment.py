import logging
from random import randint, choice, random

from pyage.core.inject import Inject
from pyage_forams.solutions.cell import Cell


logger = logging.getLogger(__name__)


class AbstractEnvironment(object):
    @Inject("insolation_meter", "initial_algae_probability", "size", "algae_growth_probability")
    def __init__(self, regeneration_factor):
        super(AbstractEnvironment, self).__init__()
        self.regeneration_factor = regeneration_factor
        self._fix_size()

    def _fix_size(self):
        """
        To assure backward compatibility, converts single-value size parameter to tuple
        """
        try:
            self.size[0]
        except:
            logger.warning("Using single value as size parameter in config file is deprecated, use tuple instead")
            self.size = (self.size, self.size, self.size)  # will work for both 2D and 3D case

    def add_foram(self, foram):
        choice(filter(lambda c: not c.is_full(), self.get_all_cells())).insert_foram(foram)

    def tick(self, step):
        for cell in self.get_all_cells():
            if 0 < cell.get_algae():
                cell.add_algae(self.regeneration_factor + self.insolation_meter.get_insolation(cell, step))
        while random() < self.algae_growth_probability:
            try:
                choice(filter(lambda c: c.is_empty(), self.get_all_cells())).add_algae(random() * 2)
            except:
                pass

    def get_cell(self, address):
        for cell in self.get_all_cells():
            if cell.get_address() == address:
                return cell

    def add_neighbour(self, cell_address, neighbour):
        self.get_cell(cell_address).add_neighbour(neighbour)


class Environment2d(AbstractEnvironment):
    def __init__(self, regeneration_factor):
        super(Environment2d, self).__init__(regeneration_factor)
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[Cell(randint(0, 4) if random() < self.initial_algae_probability else 0) for _ in range(self.size[1])]
                for _ in range(self.size[0])]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                grid[i][j]._neighbours.extend(
                    [grid[x][y] for x in range(max(0, i - 1), min(self.size[0], i + 2)) for y in
                     range(max(0, j - 1), min(self.size[1], j + 2)) if x != i or y != j])
        return grid

    def get_all_cells(self):
        for row in self.grid:
            for cell in row:
                yield cell

    def get_border_cells(self, side):
        if side == "right":
            return self._get_right_cells()
        elif side == "left":
            return self._get_left_cells()
        elif side == "upper":
            return self._get_upper_cells()
        elif side == "lower":
            return self._get_lower_cells()
        else:
            raise KeyError("unknown side: %s" % side)

    def get_shadows(self, side):
        return [cell.to_shadow() for cell in self.get_border_cells(side)]

    def _get_left_cells(self):
        return [row[0] for row in self.grid]

    def _get_right_cells(self):
        return [row[-1] for row in self.grid]

    def _get_upper_cells(self):
        return [c for c in self.grid[0]]

    def _get_lower_cells(self):
        return [c for c in self.grid[-1]]

    def join_cells(self, cells, side):
        _join_rows(cells, self.get_border_cells(side))
        return {cell.get_address(): cell for cell in cells}


class Environment3d(AbstractEnvironment):
    def __init__(self, regeneration_factor):
        super(Environment3d, self).__init__(regeneration_factor)
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        grid = [[[Cell(randint(1, 4) if random() < self.initial_algae_probability else 0)
                  for _ in range(self.size[2])] for _ in range(self.size[1])] for _ in range(self.size[0])]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                for k in range(self.size[2]):
                    grid[i][j][k].depth = self.size[0] - k - 1
                    grid[i][j][k]._neighbours.extend(
                        [grid[x][y][z] for x in range(max(0, i - 1), min(self.size[0], i + 2)) for y in
                         range(max(0, j - 1), min(self.size[1], j + 2)) for z in
                         range(max(0, k - 1), min(self.size[2], k + 2)) if x != i or y != j or z != k])

        return grid

    def get_all_cells(self):
        for plane in self.grid:
            for row in plane:
                for cell in row:
                    yield cell

    def get_border_cells(self, side):
        if side == "right":
            return self._get_right_cells()
        elif side == "left":
            return self._get_left_cells()
        elif side == "upper":
            return self._get_upper_cells()
        elif side == "lower":
            return self._get_lower_cells()
        elif side == "front":
            return self._get_front_cells()
        elif side == "back":
            return self._get_back_cells()
        else:
            raise KeyError("unknown side: %s" % side)

    def get_shadows(self, side):
        return [[cell.to_shadow() for cell in row] for row in self.get_border_cells(side)]

    def _get_left_cells(self):
        return [row[0] for row in self.grid]

    def _get_right_cells(self):
        return [row[-1] for row in self.grid]

    def _get_upper_cells(self):
        return [c for c in self.grid[0]]

    def _get_lower_cells(self):
        return [c for c in self.grid[-1]]

    def _get_front_cells(self):
        return [[row[0] for row in plane] for plane in self.grid]

    def _get_back_cells(self):
        return [[row[-1] for row in plane] for plane in self.grid]

    def join_cells(self, cells, side):
        for (r1, r2) in zip(cells, self.get_border_cells(side)):
            _join_rows(r1, r2)
        for (r1, r2) in zip(cells[1:], self.get_border_cells(side)[:-1]):
            _join_rows(r1, r2)
        for (r1, r2) in zip(cells[:-1], self.get_border_cells(side)[1:]):
            _join_rows(r1, r2)

        return {cell.get_address(): cell for row in cells for cell in row}


def _join_rows(r1, r2):
    for (c1, c2) in zip(r1, r2):
        c1.add_neighbour(c2)
        c2.add_neighbour(c1)
    for (c1, c2) in zip(r1[1:], r2[:-1]):
        c1.add_neighbour(c2)
        c2.add_neighbour(c1)
    for (c1, c2) in zip(r1[:-1], r2[1:]):
        c1.add_neighbour(c2)
        c2.add_neighbour(c1)


def environment_factory(regeneration_factor=0.1, clazz=Environment2d):
    e = [None]

    def environ():
        if e[0] is None:
            e[0] = clazz(regeneration_factor)
        return e[0]

    return environ