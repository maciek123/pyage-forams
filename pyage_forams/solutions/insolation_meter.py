class InsolationMeter(object):
    def __init__(self):
        super(InsolationMeter, self).__init__()

    def get_insolation(self, cell):
        depth = getattr(cell, "depth", 0)
        return 0.4 / (1.0 + depth)