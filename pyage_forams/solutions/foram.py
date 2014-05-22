import logging
from random import random

from pyage.core.address import Addressable
from pyage.core.inject import Inject
from pyage_forams.solutions.genom import Genom
from pyage_forams.utils import counted


logger = logging.getLogger(__name__)


class ForamAggregateAgent(Addressable):
    @Inject("forams", "environment")
    def __init__(self):
        super(ForamAggregateAgent, self).__init__()
        for foram in self.forams.values():
            foram.parent = self
            self.environment.add_foram(foram)

    def step(self):
        for foram in self.forams.values():
            foram.step()
        self.environment.tick()

    def remove_foram(self, address):
        foram = self.forams[address]
        del self.forams[address]
        foram.parent = None
        return foram

    def add_foram(self, foram):
        foram.parent = self
        self.forams[foram.get_address()] = foram


class Foram(Addressable):
    @Inject("genom_factory", "thermometer")
    def __init__(self, energy, genom=None):
        super(Foram, self).__init__()
        self.energy = energy
        if genom is None:
            self.genom = self.genom_factory()
        else:
            self.genom = genom
        self.steps = 0
        self.chambers = 0
        self.alive = True
        self.cell = None

    def step(self):
        if not self.alive:
            logger.warn("called step on dead foram")
            return
        logger.debug("foram! %s" % self.steps)
        self.steps += 1
        if self._should_die():
            self._die()
            return
        if self._eat() <= 0:
            self._move()
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
        capacity = self.chambers + 1
        return capacity

    def _energy_demand(self):
        return 0.2 * (self.chambers + 1)

    def _take_algae(self, capacity):
        taken = 0
        cells = iter([self.cell] + self.cell.neighbours)
        while capacity > taken:
            try:
                cell = cells.next()
                taken += cell.take_algae(capacity - taken)
            except StopIteration:
                break
        return taken

    def _can_reproduce(self):
        return self.energy > 10 and self.genom.chambers_limit <= self.chambers

    @counted
    def _reproduce(self):
        logger.debug("%s is reproducing" % self)
        empty_neighbours = filter(lambda c: c.is_empty(), self.cell.neighbours)
        if not empty_neighbours:
            return
        energy = self.energy / (len(empty_neighbours) * 2.0)
        for cell in empty_neighbours:
            self.energy -= energy
            foram = Foram(energy, Genom(self.genom.chambers_limit))
            cell.insert_foram(foram)
            self.parent.add_foram(foram)

    def _move(self):
        try:
            empty_neighbours = filter(lambda c: c.is_empty(), self.cell.neighbours)
            logger.debug(self.cell.neighbours)
            logger.debug(empty_neighbours)
            cell = max(empty_neighbours,
                       key=lambda c: random() + c.available_food() + sum(s.available_food() for s in c.neighbours))
            if cell:
                cell.insert_foram(self.cell.remove_foram())
                self.energy -= 0.25
                logger.debug("%s moved" % self)
        except:
            logging.exception("could not move")

    def _should_die(self):
        return self.energy <= 0

    def _die(self):
        logger.debug("%s died" % self)
        self.alive = False
        self.parent.remove_foram(self.get_address())
        self.cell.remove_foram()

    def _can_create_chamber(self):
        # TODO hardcoded energy levels
        return self.energy > 10 and self.genom.chambers_limit > self.chambers

    def _create_chamber(self):
        self.energy -= 5
        self.chambers += 1
        logger.debug("Foram %s has a new chamber, so %d altogether" % (self, self.chambers))

    def __repr__(self):
        return "Foram[%.2f, %d]" % (self.energy, self.chambers)


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