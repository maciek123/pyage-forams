import logging

from pyage_forams.solutions.distributed.request import TakeAlgaeRequest
from pyage.core.inject import Inject
from pyage_forams.solutions.distributed.requests.migrate import MigrateRequest


logger = logging.getLogger(__name__)


class ShadowCell(object):
    @Inject("request_dispatcher")
    def __init__(self, address, available_food, algae, full, agent_address):
        self.food = available_food
        self._algae = algae
        self.address = address
        self.agent_address = agent_address
        self.full = full
        self._neighbours = []  # TODO get rid of this property

    def remove_foram(self):
        pass

    def insert_foram(self, foram):
        if hasattr(foram, "parent"):
            foram.parent.remove_foram(foram.get_address())
        else:
            logger.info("%s has no parent", foram)
        self.export_foram(foram)

    def take_algae(self, demand):
        to_let = min(demand, self._algae)
        self._algae -= to_let
        if not to_let == 0:
            self.request_dispatcher.submit_request(TakeAlgaeRequest(self.agent_address, self.address, to_let))
        return to_let

    def get_algae(self):
        return self._algae

    def add_algae(self, algae):
        self._algae += algae

    def is_full(self):
        return self.full

    def get_address(self):
        return self.address

    def available_food(self):
        return self.food

    def get_neighbours(self):
        return self._neighbours

    def add_neighbour(self, neighbour):
        self._neighbours.append(neighbour)

    def export_foram(self, foram):
        logger.info("exporting %s to %s" % (foram, self.address))
        self.request_dispatcher.submit_request(
            MigrateRequest(self.agent_address, self.address, foram))

    def update(self, (address, available_food, algae, full, _)):
        logger.debug("%s  updating! %s", self, (address, available_food, algae, _))
        self._algae = algae
        self.food = available_food
        self.full = full

    def __repr__(self):
        return "(%d, ShadowCell, %d)" % (self._algae, self.available_food())


