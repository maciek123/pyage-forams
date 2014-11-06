from unittest import TestCase

from pyage.core import inject
import pyage_forams.conf.dummy_conf
from pyage_forams.solutions.cell import Cell

from pyage_forams.solutions.environment import Environment2d, Environment3d


class TestSimpleDistributed(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSimpleDistributed, cls).setUpClass()
        inject.config = "pyage_forams.conf.dummy_conf"

    def test_2d_joining(self):
        environment = Environment2d(0.2)
        cells = [Cell() for _ in range(3)]
        environment.join_cells(cells, "right")

        self.assertTrue(cells[0] in environment.grid[0][2].get_neighbours())
        self.assertTrue(cells[1] in environment.grid[0][2].get_neighbours())

        self.assertTrue(cells[0] in environment.grid[1][2].get_neighbours())
        self.assertTrue(cells[1] in environment.grid[1][2].get_neighbours())
        self.assertTrue(cells[2] in environment.grid[1][2].get_neighbours())

        self.assertTrue(cells[1] in environment.grid[2][2].get_neighbours())
        self.assertTrue(cells[2] in environment.grid[2][2].get_neighbours())

    def test_3d_joining(self):
        environment = Environment3d(0.2)
        cells = [[Cell() for _ in range(3)] for _ in range(3)]
        environment.join_cells(cells, "right")

        self.assertTrue(cells[0][0] in environment.grid[0][2][0].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[0][2][0].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[0][2][0].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[0][2][0].get_neighbours())

        self.assertTrue(cells[0][0] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[0][2][1].get_neighbours())

        self.assertTrue(cells[0][1] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[0][2][2].get_neighbours())

        self.assertTrue(cells[0][0] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[2][0] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[2][1] in environment.grid[1][2][0].get_neighbours())

        self.assertTrue(cells[0][0] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[2][0] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[2][1] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[2][2] in environment.grid[1][2][1].get_neighbours())

        self.assertTrue(cells[0][2] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[2][2] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[2][1] in environment.grid[1][2][2].get_neighbours())

        self.assertTrue(cells[2][0] in environment.grid[2][2][0].get_neighbours())
        self.assertTrue(cells[2][1] in environment.grid[2][2][0].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[2][2][0].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[2][2][0].get_neighbours())

        self.assertTrue(cells[2][0] in environment.grid[2][2][1].get_neighbours())
        self.assertTrue(cells[2][1] in environment.grid[2][2][1].get_neighbours())
        self.assertTrue(cells[2][2] in environment.grid[2][2][1].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[2][2][1].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[2][2][1].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[2][2][1].get_neighbours())

        self.assertTrue(cells[2][2] in environment.grid[2][2][2].get_neighbours())
        self.assertTrue(cells[2][1] in environment.grid[2][2][2].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[2][2][2].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[2][2][2].get_neighbours())


class TestDistributed(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestDistributed, cls).setUpClass()
        inject.config = "pyage_forams.conf.test.test_conf"
        # pyage_forams.conf.dummy_conf.size = lambda: (2, 3, 4)

    def test_2d_joining(self):
        environment = Environment2d(0.2)
        cells = [Cell() for _ in range(2)]
        environment.join_cells(cells, "right")

        self.assertTrue(cells[0] in environment.grid[0][2].get_neighbours())
        self.assertTrue(cells[1] in environment.grid[0][2].get_neighbours())

        self.assertTrue(cells[0] in environment.grid[1][2].get_neighbours())
        self.assertTrue(cells[1] in environment.grid[1][2].get_neighbours())

    def test_3d_joining(self):
        environment = Environment3d(0.2)
        cells = [[Cell() for _ in range(4)] for _ in range(2)]
        environment.join_cells(cells, "right")

        self.assertTrue(cells[0][0] in environment.grid[0][2][0].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[0][2][0].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[0][2][0].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[0][2][0].get_neighbours())

        self.assertTrue(cells[0][0] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[0][2][1].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[0][2][1].get_neighbours())

        self.assertTrue(cells[0][1] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[0][3] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[0][2][2].get_neighbours())
        self.assertTrue(cells[1][3] in environment.grid[0][2][2].get_neighbours())

        self.assertTrue(cells[0][0] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[1][2][0].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[1][2][0].get_neighbours())

        self.assertTrue(cells[0][0] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[0][1] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[1][0] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[1][2][1].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[1][2][1].get_neighbours())

        self.assertTrue(cells[0][1] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[0][3] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[1][1] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[1][2][2].get_neighbours())
        self.assertTrue(cells[1][3] in environment.grid[1][2][2].get_neighbours())

        self.assertTrue(cells[0][3] in environment.grid[0][2][3].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[0][2][3].get_neighbours())
        self.assertTrue(cells[1][3] in environment.grid[0][2][3].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[0][2][3].get_neighbours())

        self.assertTrue(cells[0][3] in environment.grid[1][2][3].get_neighbours())
        self.assertTrue(cells[0][2] in environment.grid[1][2][3].get_neighbours())
        self.assertTrue(cells[1][3] in environment.grid[1][2][3].get_neighbours())
        self.assertTrue(cells[1][2] in environment.grid[1][2][3].get_neighbours())

    def test_2d_multiple_joining(self):
        environment = Environment2d(0.2)
        right_cells = [Cell() for _ in range(2)]
        environment.join_cells(right_cells, "right")
        upper_cells = [Cell() for _ in range(3)]
        environment.join_cells(upper_cells, "upper")

        self.assertTrue(right_cells[0] in environment.grid[0][2].get_neighbours())
        self.assertTrue(right_cells[1] in environment.grid[0][2].get_neighbours())

        self.assertTrue(right_cells[0] in environment.grid[1][2].get_neighbours())
        self.assertTrue(right_cells[1] in environment.grid[1][2].get_neighbours())

        self.assertTrue(upper_cells[0] in environment.grid[0][0].get_neighbours())
        self.assertTrue(upper_cells[0] in environment.grid[0][1].get_neighbours())

        self.assertTrue(upper_cells[1] in environment.grid[0][0].get_neighbours())
        self.assertTrue(upper_cells[1] in environment.grid[0][1].get_neighbours())
        self.assertTrue(upper_cells[1] in environment.grid[0][2].get_neighbours())

        self.assertTrue(upper_cells[2] in environment.grid[0][1].get_neighbours())
        self.assertTrue(upper_cells[2] in environment.grid[0][2].get_neighbours())