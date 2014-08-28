import logging

from pyage.core.address import Addressable


logger = logging.getLogger(__name__)


class Cell(Addressable):
    def __init__(self, algae=0):
        super(Cell, self).__init__()
        self._algae = algae
        self.foram = None
        self._neighbours = []

    def insert_foram(self, foram):
        logger.info("inserting %s into %s" % (foram, self))
        if not self.is_empty():
            raise ValueError("cannot insert foram to already occupied cell")
        self.foram = foram
        foram.cell = self

    def remove_foram(self):
        foram = self.foram
        foram.cell = None
        self.foram = None
        return foram

    def is_empty(self):
        return self.foram is None

    def take_algae(self, demand):
        to_let = min(demand, self._algae)
        self._algae -= to_let
        return to_let

    def get_algae(self):
        return self._algae

    def add_algae(self, algae):
        self._algae += algae

    def available_food(self):
        return self._algae + sum(map(lambda c: c.get_algae(), self._neighbours))

    def add_neighbour(self, cell):
        self._neighbours.append(cell)

    def get_neighbours(self):
        return self._neighbours

    def __repr__(self):
        return "(%d, %s, %d)" % (self._algae, self.foram, self.available_food())