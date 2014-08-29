import logging
from random import choice

import Pyro4

from pyage.core.agent.agent import AGENT
from pyage.core.inject import InjectOptional, Inject
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.requests.match import MatchRequest


logger = logging.getLogger(__name__)


class NeighbourMatcher(object):
    def match_neighbours(self, agent):
        raise NotImplementedError()


class Neighbour2dMatcher(NeighbourMatcher):
    @Inject("request_dispatcher", "size")
    def __init__(self):
        super(Neighbour2dMatcher, self).__init__()

    def match_neighbours(self, agent):
        remote_agent = self.get_random_aggregate(agent.get_address())
        if remote_agent:
            self._join_left(remote_agent, agent)

    def _join_left(self, remote_agent, agent):
        remote_address = AGENT + "." + remote_agent.get_address()
        logger.info("left matching with: %s" % remote_address)
        cells = remote_agent.get_right_cells()
        shadow_cells = [ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), remote_address) for cell
                        in cells]
        agent.join_left(remote_address, shadow_cells)
        self.request_dispatcher.submit_request(
            MatchRequest(remote_address, agent.environment.get_left_cells(), AGENT + "." + agent.get_address(),
                         "right"))

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
