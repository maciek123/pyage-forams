from random import random


class InsolationMeter(object):
    def __init__(self, surface_insolation=10, insolation_factor=0.2):
        super(InsolationMeter, self).__init__()
        self.surface_insolation = surface_insolation
        self.insolation_factor = insolation_factor

    def get_insolation(self, cell, step):
        depth = getattr(cell, "depth", 0)
        if random() > 0.999:
            print step, depth, max(0, self.surface_insolation - depth * self.insolation_factor)
        return max(0, self.surface_insolation - depth * self.insolation_factor)