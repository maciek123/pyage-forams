import logging
from random import random, sample

from pyage.core.address import Addressable
from pyage.core.inject import Inject
from pyage_forams.solutions.agent.aggregate import ForamAggregateAgent
from pyage_forams.solutions.genom import Genom
from pyage_forams.utils import counted


logger = logging.getLogger(__name__)


class Foram(Addressable):
    @Inject("genom_factory", "reproduction_minimum", "movement_energy", "growth_minimum", "energy_need",
            "newborn_limit", "reproduction_probability", "growth_probability", "growth_cost_factor", "capacity_factor")
    def __init__(self, energy, genom=None):
        super(Foram, self).__init__()
        self.energy = energy
        if genom is None:
            self.genom = self.genom_factory()
        else:
            self.genom = genom
        self.chambers = 1
        self.alive = True
        self.cell = None

    def step(self):
        logger.debug("step %s", self)
        if not self.alive:
            logger.warn("called step on dead foram")
            return
        if self._eat() <= 0:
            self._move()
        if self._should_die():
            self._die()
            return
        if self._can_reproduce():
            self._reproduce()
        if self._can_create_chamber():
            self._create_chamber()

    def _eat(self):
        e = self.energy
        capacity = self._energy_capacity()
        self.energy += self._take_algae(capacity) - self._energy_demand()
        return self.energy - e

    def _energy_capacity(self):
        capacity = self.chambers * self.capacity_factor
        return capacity

    def _energy_demand(self):
        return self.energy_need * (self.chambers + 1)

    def _take_algae(self, capacity):
        taken = 0
        cells = iter([self.cell] + self.cell.get_neighbours())
        while capacity > taken:
            try:
                cell = cells.next()
                taken += cell.take_algae(capacity - taken)
            except StopIteration:
                break
        return taken

    def _can_reproduce(self):
        return self.energy > self.reproduction_minimum and self.genom.chambers_limit <= self.chambers \
               and random() < self.reproduction_probability

    @counted
    def _reproduce(self):
        logger.debug("%s is reproducing" % self)
        empty_neighbours = filter(lambda c: not c.is_full(), self.cell.get_neighbours())
        if not empty_neighbours:
            logger.debug("%s has no space to reproduce" % self)
            return
        logger.debug("%s is reproducing" % self)
        if len(empty_neighbours) > self.newborn_limit:
            empty_neighbours = sample(empty_neighbours, self.newborn_limit)
        energy = self.energy / (len(empty_neighbours) * 2.0)
        for cell in empty_neighbours:
            self.energy = 0
            self._create_child(cell, energy)
        logger.debug("%s has reproduced into %d cells and will now die" % (self, len(empty_neighbours)))
        self._die()

    @counted
    def _create_child(self, cell, energy):
        foram = Foram(energy, Genom(self.genom.chambers_limit))
        self.parent.add_foram(foram)
        cell.insert_foram(foram)

    def _move(self):
        try:
            if self.energy < self.movement_energy:
                logger.warning("%s has no energy to move" % self)
                return
            empty_neighbours = filter(lambda c: not c.is_full(), self.cell.get_neighbours())
            if not empty_neighbours:
                logger.warning("%s has nowhere to move" % self)
                return
            logger.debug(empty_neighbours)
            cell = max(empty_neighbours,
                       key=lambda c: random() + c.available_food() + sum(
                           s.available_food() for s in c.get_neighbours()))
            if cell:
                cell.insert_foram(self.cell.remove_foram(self))
                self.energy -= self.movement_energy
                logger.debug("%s moved" % self)
        except:
            logging.exception("could not move")

    def _should_die(self):
        return self.energy <= 0

    @counted
    def _die(self):
        logger.debug("%s died" % self)
        self.alive = False
        self.parent.remove_foram(self.get_address())
        self.cell.remove_foram(self)

    def _can_create_chamber(self):
        return self.energy > self.growth_minimum and self.genom.chambers_limit > self.chambers \
               and random() > self.growth_probability

    def _create_chamber(self):
        self.energy -= self.growth_cost_factor * self.energy
        self.chambers += 1
        logger.debug("Foram %s has a new chamber, so %d altogether" % (self, self.chambers))

    def __repr__(self):
        return "%s[%.2f, %d]" % (self.get_address(), self.energy, self.chambers)


def create_forams(count, initial_energy):
    def factory():
        forams = {}
        for i in range(count):
            foram = Foram(initial_energy)
            forams[foram.get_address()] = foram
        return forams

    return factory


def create_agent():
    agent = ForamAggregateAgent()
    return {agent.get_address(): agent}