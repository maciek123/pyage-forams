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
            self._join(remote_agent, agent, "right")

    def _join(self, remote_agent, agent, side):
        remote_address = AGENT + "." + remote_agent.get_address()
        logger.info("left matching with: %s" % remote_address)
        cells = remote_agent.get_cells(side)
        shadow_cells = [ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), remote_address) for cell
                        in cells]
        agent.join(remote_address, shadow_cells, opposite(side))
        self.request_dispatcher.submit_request(
            MatchRequest(remote_address, agent.environment.get_border_cells(opposite(side)),
                         AGENT + "." + agent.get_address(),
                         side))

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


def opposite(side):
    if side == "left":
        return "right"
    elif side == "right":
        return "left"
    elif side == "upper":
        return "lower"
    elif side == "lower":
        return "upper"