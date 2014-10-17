import logging
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.request import Request

logger = logging.getLogger(__name__)


class Match2dRequest(Request):
    def __init__(self, agent_address, cells, remote_address, side, steps):
        super(Match2dRequest, self).__init__(agent_address)
        self.side = side
        self.cells = cells
        self.remote_address = remote_address
        self.steps = steps

    def execute(self, agent):
        logger.info("2d-matching with %s" % self.remote_address)
        shadow_cells = [ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), self.remote_address) for
                        cell in self.cells]
        agent.join(self.remote_address, shadow_cells, self.side, self.steps)


class Match3dRequest(Request):
    def __init__(self, agent_address, cells, remote_address, side, steps):
        super(Match3dRequest, self).__init__(agent_address)
        self.side = side
        self.cells = cells
        self.remote_address = remote_address
        self.steps = steps

    def execute(self, agent):
        logger.info("3d-matching with %s" % self.remote_address)
        shadow_cells = [
            [ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), self.remote_address) for cell in
             row] for row in self.cells]
        agent.join(self.remote_address, shadow_cells, self.side, self.steps)