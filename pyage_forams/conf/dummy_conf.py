# for testing purposes
from pyage.core import address

from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.insolation_meter import StaticInsolation


factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate

insolation_meter = StaticInsolation
address_provider = address.SequenceAddressProvider
size = lambda: 3
cell_capacity = lambda: 1
algae_growth_probability = lambda: 0.3

reproduction_minimum = lambda: 10
movement_energy = lambda: 0.25
growth_minimum = lambda: 10
energy_need = lambda: 0.2
algae_limit = lambda: 20
newborn_limit = lambda: 9
reproduction_probability = lambda: 0.8
growth_probability = lambda: 0.8
growth_cost_factor = lambda: 0.5
capacity_factor = lambda: 1.1
initial_algae_probability = lambda: 0.3
