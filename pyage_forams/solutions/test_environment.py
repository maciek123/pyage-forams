from unittest import TestCase
from pyage.core import inject
from pyage_forams.solutions.environment import Environment2d, Environment3d


class TestEnvironment(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestEnvironment, cls).setUpClass()
        inject.config = "pyage_forams.conf.dummy_conf"

    def test_environment(self):
        self._get_environments()

    def test_neighborhood(self):
        for environment in self._get_environments():
            environment.get_all_cells()

    def test_neighborhood_symmetry(self):
        for environment in self._get_environments():
            for cell in environment.get_all_cells():
                for neighbour in cell._neighbours:
                    self.assertTrue(cell in neighbour._neighbours)

    def test_self_neighbourhood(self):
        for environment in self._get_environments():
            for cell in environment.get_all_cells():
                self.assertFalse(cell in cell._neighbours)

    def test_neighbourhood_repetitions(self):
        for environment in self._get_environments():
            for cell in environment.get_all_cells():
                self.assertEqual(len(cell._neighbours), len(set(cell._neighbours)))

    def test_2d_neighbourhood(self):
        grid = (self._get_environments()[0]).grid
        self.assertEqual(len(grid[1][1]._neighbours), 8)

        self.assertTrue(grid[0][0] in grid[1][1]._neighbours)
        self.assertTrue(grid[0][1] in grid[1][1]._neighbours)
        self.assertTrue(grid[0][2] in grid[1][1]._neighbours)
        self.assertTrue(grid[1][0] in grid[1][1]._neighbours)
        self.assertTrue(grid[1][2] in grid[1][1]._neighbours)
        self.assertTrue(grid[2][0] in grid[1][1]._neighbours)
        self.assertTrue(grid[2][1] in grid[1][1]._neighbours)
        self.assertTrue(grid[2][2] in grid[1][1]._neighbours)

    def test_3d_neighbourhood(self):
        grid = (self._get_environments()[1]).grid
        self.assertEqual(len(grid[1][1][1]._neighbours), 26)

        self.assertTrue(grid[0][0][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][0][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][0][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][0][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][1][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][1][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][1][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][2][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][2][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[0][2][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][0][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][0][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][0][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][1][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][1][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][2][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][2][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[1][2][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][0][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][0][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][0][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][0][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][0][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][0][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][1][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][1][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][1][2] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][2][0] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][2][1] in grid[1][1][1]._neighbours)
        self.assertTrue(grid[2][2][2] in grid[1][1][1]._neighbours)

    def _get_environments(self):
        return [Environment2d(0.2), Environment3d(0.2)]