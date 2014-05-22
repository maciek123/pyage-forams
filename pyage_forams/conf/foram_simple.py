# coding=utf-8

from pyage.core import address

from pyage.core.stop_condition import StepLimitStopCondition
from pyage_forams.solutions.environment import environment_factory
from pyage_forams.solutions.foram import create_forams, create_agent
from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.statistics import PlottingStatistics, CsvStatistics
from pyage_forams.solutions.thermometer import Thermometer

factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate
forams = create_forams(8, initial_energy=5)
agents = create_agent
thermometer = Thermometer
size = lambda: 20

environment = environment_factory()

stop_condition = lambda: StepLimitStopCondition(90)

address_provider = address.SequenceAddressProvider
stats = CsvStatistics