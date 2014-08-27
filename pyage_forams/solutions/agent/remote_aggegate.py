import logging
from time import sleep

from pyage.core.address import Addressable
from pyage.core.inject import Inject
from pyage_forams.solutions.agent.shadow_cell import ShadowCell


logger = logging.getLogger(__name__)


class RemoteForamAggregateAgent(Addressable):
    @Inject("forams", "environment", "neighbour_matcher", "request_dispatcher")
    def __init__(self):
        super(RemoteForamAggregateAgent, self).__init__()
        self.matched = False
        self.requests = []
        for foram in self.forams.values():
            foram.parent = self
            self.environment.add_foram(foram)

    def step(self):
        if not self.matched:
            # TODO refactor
            self.neighbour_matcher.match_neighbours(self.environment, self.get_address())
            self.matched = True
        for foram in self.forams.values():
            if foram.cell is None or foram.cell.foram is None:
                logger.warning("something went wrong %s" % foram)
            foram.step()
        self.environment.tick()
        sleep(1)
        self.request_dispatcher.send_requests()
        while self.requests:
            self.requests.pop().execute(self)

    def remove_foram(self, address):
        foram = self.forams[address]
        del self.forams[address]
        foram.parent = None
        return foram

    def add_foram(self, foram):
        foram.parent = self
        self.forams[foram.get_address()] = foram

    def take_algae(self, cell_address, algae):
        logger.warn("taking %f algae from %s" % (algae, cell_address))
        self.environment.get_cell(cell_address).take_algae(algae)

    def get_all_cells(self):
        return [cell.get_address() for cell in self.environment.get_all_cells()]

    def import_foram(self, cell_address, foram):
        try:
            logger.warning("importing %s into %s" % (foram, cell_address))
            self.environment.get_cell(cell_address).insert_foram(foram)
            self.add_foram(foram)
            logger.warning("foram imported")
        except:
            logging.exception("Could not import cell")

    def submit_requests(self, requests):
        self.requests.extend(requests)

    def join_shadow_cells(self, agent_address):
        logger.info("joining %s" % agent_address)
        self.neighbour_matcher.match_neighbours(self.environment, self.get_address(), agent_address)


def create_remote_agent():
    agent = RemoteForamAggregateAgent()
    return {agent.get_address(): agent}