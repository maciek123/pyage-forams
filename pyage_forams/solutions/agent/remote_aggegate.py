import logging
from time import sleep
import Pyro4

from pyage.core.address import Addressable
from pyage.core.inject import Inject
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.neighbour_matcher import opposite


logger = logging.getLogger(__name__)


class RemoteForamAggregateAgent(Addressable):
    @Inject("forams", "environment", "neighbour_matcher", "request_dispatcher", "ns_hostname")
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        super(RemoteForamAggregateAgent, self).__init__()
        self.updates = []
        self.requests = []
        for foram in self.forams.values():
            foram.parent = self
            self.environment.add_foram(foram)
        self.neighbour_matcher.match_neighbours(self)

    def step(self):
        for foram in self.forams.values():
            if foram.cell is None or foram.cell.foram is None:
                logger.warning("something went wrong %s" % foram)
            foram.step()
        self.environment.tick()
        sleep(1)
        self.request_dispatcher.send_requests()
        while self.requests:
            self.requests.pop().execute(self)
        for update in self.updates:
            update()

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

    def get_cells(self, side):
        return self.environment.get_border_cells(side)

    def join(self, remote_address, shadow_cells, side):
        mapping = {cell.get_address(): cell for cell in shadow_cells}

        def update():
            try:
                logger.info("updating %s" % remote_address)
                ns = Pyro4.locateNS(self.ns_hostname)
                agent = Pyro4.Proxy(ns.lookup(remote_address))
                cells = agent.get_cells(opposite(side))
                for cell in cells:
                    if cell.get_address() in mapping:
                        mapping[cell.get_address()].update(cell)
            except:
                logging.exception("could not update")

        self.updates.append(update)
        self.environment.join_cells(shadow_cells, side)

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


def create_remote_agent(name):
    agent = RemoteForamAggregateAgent(name)
    return {agent.get_address(): agent}