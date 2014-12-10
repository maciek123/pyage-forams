from unittest import TestCase
from pyage.core import inject
from pyage_forams.solutions.cell import Cell


class TestCell(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCell, cls).setUpClass()
        inject.config = "pyage_forams.conf.dummy_conf"

    def test_add_algae(self):
        cell = Cell()
        cell.add_algae(1000000)
        food = cell.available_food()

        cell.add_algae(1000000)
        self.assertEqual(food, cell.available_food())