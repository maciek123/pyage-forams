import logging
from random import choice
from time import sleep
import Pyro4
from pyage.core.address import Addressable
from pyage.core.agent.agent import AGENT
from pyage.core.inject import Inject, InjectOptional
from pyage_forams.solutions.foram import logger

__author__ = 'makz'


class ForamAggregateAgent(Addressable):
    @Inject("forams", "environment")
    def __init__(self):
        super(ForamAggregateAgent, self).__init__()
        for foram in self.forams.values():
            foram.parent = self
            self.environment.add_foram(foram)

    def step(self):
        for foram in self.forams.values():
            if foram.cell is None or foram.cell.foram is None:
                logger.warning("something went wrong %s" % foram)
            foram.step()
        self.environment.tick()
        sleep(1)
        try:
            agent = self.get_random_aggregate()
            if not agent: return
            foram = choice(list(self.environment.get_all_cells())).remove_foram()
            logger.info("f: %s" % foram)
            if foram is not None:
                logger.warning("exporting %s to %s" % (foram, agent.get_address()))
                cells = agent.get_all_cells()
                logger.warning(cells)
                agent.import_foram(choice(cells), foram)
                self.remove_foram(foram.get_address())
                logger.warning("export sucessful")
        except Exception, e:
            logging.exception("could not export")

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
        for cell in self.environment.get_all_cells():
            if cell.get_address() == cell_address:
                cell.take_algae(algae)
                logger.info(cell)

    def get_all_cells(self):
        return [cell.get_address() for cell in self.environment.get_all_cells()]

    def import_foram(self, cell_address, foram):
        try:
            logger.warning("importing %s into %s" % (foram, cell_address))
            self.environment.get_cell(cell_address).insert_foram(foram)
            self.add_foram(foram)
            logger.warning("cell imported")
        except:
            logging.exception("Could not import cell")

    @InjectOptional('ns_hostname')
    def get_random_aggregate(self):
        try:
            ns = Pyro4.locateNS(self.ns_hostname)
            agents = ns.list(AGENT)
            logger.warning(agents)
            del agents[AGENT + "." + self.get_address()]
            return Pyro4.Proxy(choice(agents.values()))
        except:
            logger.info("could not locate")