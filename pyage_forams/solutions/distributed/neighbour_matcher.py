import logging
from random import choice

import Pyro4

from pyage.core.agent.agent import AGENT
from pyage.core.inject import InjectOptional, Inject
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.requests.match import MatchRequest


logger = logging.getLogger(__name__)


class NeighbourMatcher(object):
    def match_neighbours(self, environment, parent_address):
        raise NotImplementedError()


class Neighbour2dMatcher(NeighbourMatcher):
    @Inject("request_dispatcher", "size")
    def __init__(self):
        super(Neighbour2dMatcher, self).__init__()

    def match_neighbours(self, environment, parent_address):
        agent = self.get_random_aggregate(parent_address)
        if agent:
            agent_address = agent.get_address()
            logger.info("matching with: %s" % agent_address)
            cells = agent.get_left_cells()
            shadow_cells = [
                ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), AGENT + "." + agent_address) for
                cell in cells]
            environment.join(shadow_cells)
            self.request_dispatcher.submit_request(
                MatchRequest(AGENT + '.' + agent.get_address(), environment.get_left_cells(),
                             AGENT + '.' + parent_address))


    @InjectOptional('ns_hostname')
    def get_random_aggregate(self, parent_address):
        try:
            ns = Pyro4.locateNS(self.ns_hostname)
            agents = ns.list(AGENT)
            logger.warning(agents)
            address = AGENT + "." + parent_address
            if address in agents:
                del agents[address]
            return Pyro4.Proxy(choice(agents.values()))
        except:
            logging.exception("could not locate")
