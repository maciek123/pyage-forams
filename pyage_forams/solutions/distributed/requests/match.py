import logging
from pyage_forams.solutions.agent.shadow_cell import ShadowCell
from pyage_forams.solutions.distributed.request import Request

logger = logging.getLogger(__name__)


class MatchRequest(Request):
    def __init__(self, agent_address, cells, remote_address, how):
        super(MatchRequest, self).__init__(agent_address)
        self.how = how
        self.cells = cells
        self.remote_address = remote_address

    def execute(self, agent):
        logger.info("matching with %s" % self.remote_address)
        shadow_cells = [ShadowCell(cell.get_address(), cell.available_food(), cell.get_algae(), self.remote_address) for
                        cell in self.cells]
        # TODO get rid of magic strings
        if self.how == "right":
            agent.join_right(self.remote_address, shadow_cells)
        elif self.how == "left":
            agent.join_left(self.remote_address, shadow_cells)
        elif self.how == "upper":
            agent.join_upper(self.remote_address, shadow_cells)
        elif self.how == "lower":
            agent.join_lower(self.remote_address, shadow_cells)