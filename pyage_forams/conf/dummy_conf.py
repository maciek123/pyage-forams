# for testing purposes
from pyage.core import address
from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.thermometer import Thermometer

factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate

thermometer = Thermometer
address_provider = address.SequenceAddressProvider
size = lambda: 3


