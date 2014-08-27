import logging
from random import choice

import Pyro4

from pyage.core.agent.agent import AGENT
from pyage.core.inject import InjectOptional, Inject
from pyage_forams.solutions.distributed.request import MigrateRequest


logger = logging.getLogger(__name__)


class ShadowCell(object):

    @Inject("request_dispatcher")
    def __init__(self, address, available_food, algae, agent_address):
        self.food = available_food
        self.algae = algae
        self.address = address
        self.agent_address = agent_address
        self.empty = True
        self.neighbours = []  # TODO get rid of this property

    def remove_foram(self):
        self.empty = True

    def insert_foram(self, foram):
        if hasattr(foram, "parent"):
            foram.parent.remove_foram(foram.get_address())
        self.empty = False
        self.export_foram(foram)

    def take_algae(self, demand):
        to_let = min(demand, self.algae)
        self.algae -= to_let
        return to_let

    def is_empty(self):
        return self.empty

    def get_address(self):
        return self.address

    def available_food(self):
        return self.food

    def get_neighbours(self):
        return self.neighbours

    def export_foram(self, foram):
        logger.info("exporting %s to %s" % (foram, self.address))
        self.request_dispatcher.submit_request(
            MigrateRequest(AGENT + "." + self.agent_address, self.address, foram))

    def __repr__(self):
        return "(%d, ShadowCell, %d)" % (self.algae, self.available_food())


