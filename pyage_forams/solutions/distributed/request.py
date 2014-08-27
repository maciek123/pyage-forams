class Request(object):
    def execute(self, agent):
        raise NotImplementedError()


class MigrateRequest(Request):
    def __init__(self, cell_address, foram):
        super(MigrateRequest, self).__init__()
        self.cell_address = cell_address
        self.foram = foram

    def execute(self, agent):
        agent.import_foram(self.cell_address, self.foram)


class TakeAlgaeRequest(Request):
    def __init__(self, cell_address, algae):
        super(TakeAlgaeRequest, self).__init__()
        self.algae = algae
        self.cell_address = cell_address

    def execute(self, agent):
        agent.take_algae(self.cell_address, self.algae)


