# for testing purposes
from pyage.core import address

from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.insolation_meter import InsolationMeter


factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate

insolation_meter = InsolationMeter
address_provider = address.SequenceAddressProvider
size = lambda: 3


