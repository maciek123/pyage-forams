class Thermometer(object):
    def __init__(self, initial_temperature=0):
        super(Thermometer, self).__init__()
        self.temperature = initial_temperature

    def get_temperature(self):
        return self.temperature