from unittest import TestCase
from pyage.core import inject
from pyage_forams.solutions.environment import Cell
from pyage_forams.solutions.insolation_meter import StaticInsolation, DynamicInsolation


class TestInsolation(TestCase):
    def test_insolation(self):
        inject.config = "pyage_forams.conf.dummy_conf"
        insolation_meter = StaticInsolation(surface_insolation=5, insolation_factor=0.1)
        self.assertEqual(insolation_meter.get_insolation(create_cell(), 10), 5)
        self.assertEqual(insolation_meter.get_insolation(create_cell(10), 10), 4)
        self.assertEqual(insolation_meter.get_insolation(create_cell(100), 10), 0)


class TestDynamicInsolation(TestCase):
    def test_insolation(self):
        inject.config = "pyage_forams.conf.dummy_conf"
        insolation_meter = DynamicInsolation([(10, 10, 0.1), (20, 5, 0.5), (1, 1, 1)])
        self.assertEqual(insolation_meter.get_insolation(create_cell(0), 1), 10)
        self.assertEqual(insolation_meter.get_insolation(create_cell(0), 20), 5)
        self.assertEqual(insolation_meter.get_insolation(create_cell(0), 31), 1)


def create_cell(depth=0):
    cell = Cell()
    cell.depth = depth
    return cell

