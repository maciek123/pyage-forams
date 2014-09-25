# for testing purposes
from pyage.core import address

from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.insolation_meter import StaticInsolation


factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate

insolation_meter = StaticInsolation
address_provider = address.SequenceAddressProvider
size = lambda: 3


reproduction_minimum = lambda: 10
movement_energy = lambda: 0.25
growth_minimum = lambda: 10
energy_need = lambda: 0.2
