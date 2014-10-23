from collections import defaultdict
import logging

import Pyro4

from pyage.core.agent.agent import AGENT
from pyage.core.inject import Inject
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.request import Request


logger = logging.getLogger(__name__)


class NeighbourMatcher(object):
    @Inject("request_dispatcher", "size", "neighbours", 'ns_hostname')
    def __init__(self):
        super(NeighbourMatcher, self).__init__()
        self._located_agents = defaultdict(self._locate_agent)

    def match_neighbours(self, agent):
        for (side, address) in self.neighbours.iteritems():
            neighbour = self._locate_neighbour(address)
            if neighbour:
                self._join(neighbour, agent, side)

    def _locate_neighbour(self, address):
        try:
            ns = Pyro4.locateNS(self.ns_hostname)
            agents = ns.list(AGENT + "." + address)
            return Pyro4.Proxy(agents.values().pop())
        except:
            logging.warning("could not locate %s" % address)

    def _join(self, neighbour, agent, side):
        raise NotImplementedError()

    def _locate_agent(self, remote_address):
        ns = Pyro4.locateNS(self.ns_hostname)
        agent = Pyro4.Proxy(ns.lookup(remote_address))
        return agent


class Neighbour2dMatcher(NeighbourMatcher):
    def _join(self, remote_agent, agent, side):
        try:
            remote_address = AGENT + "." + remote_agent.get_address()
            logger.info("%s matching with: %s" % (side, remote_address))
            shadows = remote_agent.get_shadows(opposite(side))
            logger.debug("received shadows: %s" % shadows)
            shadow_cells = self.create_shadow_cells(remote_address, shadows)
            agent.join(remote_address, shadow_cells, side, remote_agent.get_steps())
            self.request_dispatcher.submit_request(
                Match2dRequest(remote_address, agent.get_shadows(side),
                               AGENT + "." + agent.get_address(), opposite(side), agent.get_steps()))
        except Exception, e:
            logger.exception("could not join: %s", e.message)

    @staticmethod
    def create_shadow_cells(remote_address, shadows):
        shadow_cells = {address: ShadowCell(address, available_food, algae, empty, remote_address) for
                        (address, available_food, algae, empty, _) in shadows}
        for (address, _, _, _, neighbours) in shadows:
            for neighbour in neighbours:
                try:
                    shadow_cells[address].add_neighbour(shadow_cells[neighbour])
                except KeyError:
                    pass
        return shadow_cells.values()

    def update(self, remote_address, side, mapping):
        logger.info("updating shadow cels from: %s" % remote_address)
        agent = self._locate_agent(remote_address)
        shadows = agent.get_shadows(opposite(side))
        for shadow in shadows:
            if shadow[0] in mapping:
                mapping[shadow[0]].update(shadow)
            else:
                logger.info("unsuccessful attempt to update cell with address %s", shadow.get_address())
        return agent.get_steps()


class Neighbour3dMatcher(NeighbourMatcher):
    def _join(self, remote_agent, agent, side):
        try:
            remote_address = AGENT + "." + remote_agent.get_address()
            logger.info("%s matching with: %s" % (side, remote_address))
            shadows = remote_agent.get_shadows(opposite(side))
            logger.debug("received shadows: %s" % shadows)
            shadow_cells = self.create_shadow_cells(remote_address, shadows)
            agent.join(remote_address, shadow_cells, side, remote_agent.get_steps())
            self.request_dispatcher.submit_request(
                Match3dRequest(remote_address, agent.environment.get_shadows(side),
                               AGENT + "." + agent.get_address(), opposite(side), agent.get_steps()))
        except Exception, e:
            logger.exception("could not join: %s", e.message)


    @staticmethod
    def create_shadow_cells(remote_address, shadows):
        shadow_cells = [[ShadowCell(address, available_food, algae, empty, remote_address) for
                         (address, available_food, algae, empty, _) in row] for row in shadows]
        mapping = {shadow_cell.get_address(): shadow_cell for row in shadow_cells for shadow_cell in row}
        for row in shadows:
            for (address, _, _, _, neighbours) in row:
                for neighbour in neighbours:
                    try:
                        mapping[address].add_neighbour(mapping[neighbour])
                    except KeyError:
                        pass
        return shadow_cells

    def update(self, remote_address, side, mapping):
        logger.info("updating shadow cels from: %s" % remote_address)
        agent = self._locate_agent(remote_address)
        shadows = agent.get_shadows(opposite(side))
        for row in shadows:
            for shadow in row:
                if shadow[0] in mapping:
                    mapping[shadow[0]].update(shadow)
                else:
                    logger.info("unsuccessful attempt to update cell with address %s", shadow.get_address())
        return agent.get_steps()


class Match2dRequest(Request):
    def __init__(self, agent_address, cells, remote_address, side, steps):
        super(Match2dRequest, self).__init__(agent_address)
        self.side = side
        self.shadows = cells
        self.remote_address = remote_address
        self.steps = steps

    def execute(self, agent):
        logger.info("2d-matching with %s" % self.remote_address)
        shadow_cells = Neighbour2dMatcher.create_shadow_cells(self.remote_address, self.shadows)
        agent.join(self.remote_address, shadow_cells, self.side, self.steps)


class Match3dRequest(Request):
    def __init__(self, agent_address, shadows, remote_address, side, steps):
        super(Match3dRequest, self).__init__(agent_address)
        self.side = side
        self.shadows = shadows
        self.remote_address = remote_address
        self.steps = steps

    def execute(self, agent):
        logger.info("3d-matching with %s" % self.remote_address)
        shadow_cells = Neighbour3dMatcher.create_shadow_cells(self.remote_address, self.shadows)
        agent.join(self.remote_address, shadow_cells, self.side, self.steps)


def opposite(side):
    if side == "left":
        return "right"
    elif side == "right":
        return "left"
    elif side == "upper":
        return "lower"
    elif side == "lower":
        return "upper"
    elif side == "front":
        return "back"
    elif side == "back":
        return "front"
    else:
        raise ValueError("unrecognized side: " + side)
