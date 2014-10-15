import logging
from random import random
from time import sleep

import Pyro4

from pyage.core.address import Addressable
from pyage.core.agent.agent import AGENT
from pyage.core.inject import Inject
from pyage_forams.solutions.distributed.neighbour_matcher import opposite


logger = logging.getLogger(__name__)


class RemoteForamAggregateAgent(Addressable):
    @Inject("forams", "environment", "neighbour_matcher", "request_dispatcher", "ns_hostname", "neighbours")
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        super(RemoteForamAggregateAgent, self).__init__()
        self.updates = []
        self.requests = []
        self.joined = {}
        self._step = 0
        for foram in self.forams.values():
            foram.parent = self
            self.environment.add_foram(foram)
        self.neighbour_matcher.match_neighbours(self)

    def step(self):
        self._step += 1
        self._wait_for_neighbours()
        for foram in self.forams.values():
            if foram.cell is None or foram.cell.foram is None:
                logger.warning("something went wrong %s" % foram)
            foram.step()
        self.environment.tick(self._step)
        self._notify_neighbours()
        self.request_dispatcher.send_requests()
        self._process_requests()
        for update in self.updates:
            update()

    def get_steps(self):
        return self._step

    def _wait_for_neighbours(self):
        while not self._all_neighbours_ready():
            logger.info("waiting for neighbours %d %s" % (self._step, self.joined))
            self._process_requests()
            sleep(random())  # TODO improve

    def _process_requests(self):
        while self.requests:
            self.requests.pop().execute(self)

    def _all_neighbours_ready(self):
        if len(self.joined) < len(self.neighbours):
            return False
        for (neighbour, step) in self.joined.iteritems():
            if step < self._step - 1:  # TODO make configurable
                return False
        return True

    def _notify_neighbours(self):
        try:
            for (neighbour, step) in self.joined.iteritems():
                self._notify_neighbour(neighbour)
        except:
            logger.exception("could not notify neighbours")

    def remove_foram(self, address):
        logger.info("removing foram %s", address)
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

    def join(self, remote_address, shadow_cells, side, step):  # TODO 3d join
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
                    else:
                        logger.info("unsuccessful attempt to update cell with address %s", cell.get_address())
                self.joined[remote_address] = agent.get_steps()
            except:
                logging.exception("could not update")

        self.updates.append(update)
        self.environment.join_cells(shadow_cells, side)
        self.joined[remote_address] = step
        logger.info("%s is now %s-joined with: %s" % (self.address, side, remote_address))

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

    def notify(self, neighbour_address, steps):
        logger.info("received notification %s %s", steps, neighbour_address)
        self.joined[neighbour_address] = steps

    def _notify_neighbour(self, neighbour):
        try:
            ns = Pyro4.locateNS(self.ns_hostname)
            agent = Pyro4.Proxy(ns.lookup(neighbour))
            agent.notify(AGENT + "." + self.get_address(), self.get_steps())
            logger.info("notified %s", neighbour)
        except:
            logger.exception("could not notify neighbour")


def create_remote_agent(name):
    agent = RemoteForamAggregateAgent(name)
    return {agent.get_address(): agent}