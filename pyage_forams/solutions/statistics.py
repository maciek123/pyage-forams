from datetime import datetime
import itertools
from subprocess import Popen

import matplotlib.pyplot as plt

from pyage.core.inject import Inject
from pyage.core.statistics import Statistics


class PlottingStatistics(Statistics):
    @Inject("environment")
    def __init__(self):
        super(PlottingStatistics, self).__init__()
        self.prefix = datetime.now().strftime("%Y%m%d_%H%M%S")

    def update(self, step_count, agents):
        self.plot(self.environment.grid, step_count)

    def summarize(self, agents):
        cmd = "convert -loop 0 -delay 50 /tmp/pyage-%s-step-*.png animation.gif && rm /tmp/pyage-%s-step-*.png" % (
            self.prefix, self.prefix)
        Popen(cmd, shell=True)

    def plot(self, grid, step):
        plt.title("step %d" % step)

        forams = []
        for (i, row) in enumerate(grid):
            for (j, cell) in enumerate(row):
                if not cell.is_empty():
                    forams.append((i, j))
                    self._draw_chambers(grid, i, j)

        x = len(grid)
        y = len(grid[0])

        self._draw_forams(forams, grid)
        self._draw_algae(grid, x, y)
        self._draw_grid(x, y)

        plt.savefig("/tmp/pyage-%s-step-%07d.png" % (self.prefix, step))
        plt.close()

    @staticmethod
    def _draw_forams(forams, grid):
        plt.scatter([c[0] for c in forams],
                    [c[1] for c in forams],
                    marker='o',
                    s=[200.0 / len(grid) * grid[i][j].foram.energy for (i, j) in forams],
                    c=['red' for _ in forams])

    @staticmethod
    def _draw_grid(x, y):
        plt.xticks([i - 0.5 for i in range(x + 1)], [])
        plt.yticks([i - 0.5 for i in range(y + 1)], [])
        plt.ticklabel_format()
        plt.xlim([-0.5, x - 0.5])
        plt.ylim([-0.5, y - 0.5])
        plt.grid()

    @staticmethod
    def _draw_algae(grid, x, y):
        pts = itertools.product(range(x), range(y))
        plt.scatter(*zip(*pts), marker='*',
                    s=[1000.0 / x * grid[i][j].algae for i in range(x) for j in range(y)], color='blue',
                    alpha=0.5)

    @staticmethod
    def _draw_chambers(grid, i, j):
        plt.annotate(
            grid[i][j].foram.chambers,
            xy=(i, j), xytext=(-5, 5),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

