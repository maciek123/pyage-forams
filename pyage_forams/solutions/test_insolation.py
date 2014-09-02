from unittest import TestCase
from pyage.core import inject
from pyage_forams.solutions.environment import Cell
from pyage_forams.solutions.insolation_meter import InsolationMeter


class TestInsolation(TestCase):
    def test_insolation(self):
        inject.config = "pyage_forams.conf.dummy_conf"
        insolation_meter = InsolationMeter(surface_insolation=5, insolation_factor=0.1)
        cell = Cell()
        self.assertEqual(insolation_meter.get_insolation(cell, 10), 5)
        cell.depth = 10
        self.assertEqual(insolation_meter.get_insolation(cell, 10), 4)
        cell.depth = 100
        self.assertEqual(insolation_meter.get_insolation(cell, 10), 0)

