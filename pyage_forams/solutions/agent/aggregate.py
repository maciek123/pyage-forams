import logging

from pyage.core.address import Addressable
from pyage.core.inject import Inject


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
        self.environment.tick(self.parent.steps)

    def remove_foram(self, address):
        foram = self.forams[address]
        del self.forams[address]
        foram.parent = None
        return foram

    def add_foram(self, foram):
        foram.parent = self
        self.forams[foram.get_address()] = foram