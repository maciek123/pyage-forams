class Genom(object):
    def __init__(self, chambers_limit):
        super(Genom, self).__init__()
        self.chambers_limit = chambers_limit


class GenomFactory(object):
    def __init__(self, chambers_limit):
        super(GenomFactory, self).__init__()
        self.life_length = chambers_limit

    def generate(self):
        return Genom(self.life_length)