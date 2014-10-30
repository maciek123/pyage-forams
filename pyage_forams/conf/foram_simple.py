# coding=utf-8

from pyage.core import address
import Pyro4
from pyage.core.migration import Pyro4Migration
from pyage.core.stop_condition import StepLimitStopCondition
from pyage_forams.solutions.environment import environment_factory, Environment3d
from pyage_forams.solutions.foram import create_forams, create_agent
from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.insolation_meter import StaticInsolation, DynamicInsolation
from pyage_forams.solutions.statistics import SimpleStatistics, PsiStatistics, CsvStatistics, MultipleStatistics


factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate
forams = create_forams(8, initial_energy=5)
agents = create_agent
insolation_meter = lambda: DynamicInsolation([(20, 10, 0.2), (10, 20, 0.4)])
size = lambda: 50

reproduction_minimum = lambda: 50
movement_energy = lambda: 0.5
growth_minimum = lambda: 30
energy_need = lambda: 0.2
algae_limit = lambda: 20
newborn_limit = lambda:6
reproduction_probability = lambda: 0.5
growth_probability = lambda: 0.5
growth_cost_factor = lambda: 0.8
capacity_factor = lambda: 1.1
initial_algae_probability = lambda: 0.2
environment = environment_factory(regeneration_factor=0.1, clazz=Environment3d)
stop_condition = lambda: StepLimitStopCondition(500)
stats = lambda: MultipleStatistics([CsvStatistics(), PsiStatistics()])


address_provider = address.SequenceAddressProvider
migration = Pyro4Migration
ns_hostname = lambda: os.environ['NS_HOSTNAME']
pyro_daemon = Pyro4.Daemon()
daemon = lambda: pyro_daemon