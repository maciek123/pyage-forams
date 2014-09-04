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
    @Inject("request_dispatcher", "size", "neighbours")
    def __init__(self):
        super(Neighbour2dMatcher, self).__init__()

    def match_neighbours(self, agent):
        for (side, address ) in self.neighbours.iteritems():
            neighbour = self._locate_neighbour(address)
            if neighbour:
                self._join(neighbour, agent, side)

    def _join(self, remote_agent, agent, side):
        remote_address = AGENT + "." + remote_agent.get_address()
        logger.info("%s matching with: %s" % (side, remote_address))
        cells = remote_agent.get_cells(side)
        shadow_cells = [ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), remote_address) for cell
                        in cells]
        agent.join(remote_address, shadow_cells, opposite(side))
        self.request_dispatcher.submit_request(
            MatchRequest(remote_address, agent.environment.get_border_cells(opposite(side)),
                         AGENT + "." + agent.get_address(),
                         side))

    @InjectOptional('ns_hostname')
    def _locate_neighbour(self, address):
        try:
            ns = Pyro4.locateNS(self.ns_hostname)
            agents = ns.list(AGENT + "." + address)
            logger.warning(agents)
            return Pyro4.Proxy(choice(agents.values()))
        except:
            logging.exception("could not locate %s" % address)


def opposite(side):
    if side == "left":
        return "right"
    elif side == "right":
        return "left"
    elif side == "upper":
        return "lower"
    elif side == "lower":
        return "upper"