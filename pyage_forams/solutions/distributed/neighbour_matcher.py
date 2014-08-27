import logging
from random import choice
import Pyro4
from pyage.core.agent.agent import AGENT
from pyage.core.inject import InjectOptional, Inject
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.request import MigrateRequest, MatchRequest

logger = logging.getLogger(__name__)


class NeighbourMatcher(object):
    def match_neighbours(self, environment, parent_address, remote_address=None):
        raise NotImplementedError()


class Neighbour2dMatcher(NeighbourMatcher):
    @Inject("request_dispatcher")
    def __init__(self):
        super(Neighbour2dMatcher, self).__init__()

    def match_neighbours(self, environment, parent_address, remote_address=None):
        if remote_address is None:
            agent = self.get_random_aggregate(parent_address)
        else:
            ns = Pyro4.locateNS(self.ns_hostname)
            agent = Pyro4.Proxy(ns.lookup(remote_address))
        if agent:
            if remote_address is None:  # TODO refactor
                self.request_dispatcher.submit_request(
                    MatchRequest(AGENT + '.' + agent.get_address(), AGENT + '.' + parent_address))
            agent_address = agent.get_address()
            logger.info("matching with: %s" % agent_address)
            cell_address = choice(agent.get_all_cells())
            shadow_cells = [ShadowCell(cell_address, 10, 1, agent_address)]
            environment.join(shadow_cells)


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
