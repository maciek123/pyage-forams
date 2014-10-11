from pyage_forams.solutions.distributed.request import Request


class MigrateRequest(Request):
    def __init__(self, agent_address, cell_address, foram):
        super(MigrateRequest, self).__init__(agent_address)
        self.cell_address = cell_address
        self.foram = foram

    def execute(self, agent):
        agent.import_foram(self.cell_address, self.foram)

    def __repr__(self):
        return "MigrateRequest[%s, %s, %s]" % (self.agent_address, self.cell_address, self.foram)