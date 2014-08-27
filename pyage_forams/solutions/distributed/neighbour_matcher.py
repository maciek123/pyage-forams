class NeighbourMatcher(object):
    def match_neighbours(self, environment):
        raise NotImplementedError()


class Neighbour2dMatcher(NeighbourMatcher):
    def __init__(self):
        super(Neighbour2dMatcher, self).__init__()

    def match_neighbours(self, environment):
        pass

