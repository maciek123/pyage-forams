from __future__ import print_function
from compiler.ast import flatten
from datetime import datetime
import itertools
import logging
from subprocess import Popen

import matplotlib.pyplot as plt

from pyage.core.inject import Inject
from pyage.core.statistics import Statistics
from pyage_forams.solutions.foram import Foram


logger = logging.getLogger(__name__)


class PlottingStatistics(Statistics):
    @Inject("environment")
    def __init__(self):
        super(PlottingStatistics, self).__init__()
        self.prefix = datetime.now().strftime("%Y%m%d_%H%M%S")

    def update(self, step_count, agents):
        self.plot(self.environment.grid, step_count, agents)

    def summarize(self, agents):
        pass
        # cmd = "convert -loop 0 -delay 50 /tmp/pyage-step-*-%s.png animation.gif && rm /tmp/pyage-step-*-%s.png" % (
        # self.prefix, self.prefix)
        # Popen(cmd, shell=True)

    def plot(self, grid, step, agents):
        plt.title("step %d %s" % (step, agents[0].get_address()))

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

        plt.savefig("/tmp/pyage-step-%07d-%s.png" % (step, self.prefix))
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
                    s=[1000.0 / x * grid[i][j].get_algae() for i in range(x) for j in range(y)], color='blue',
                    alpha=0.5)

    @staticmethod
    def _draw_chambers(grid, i, j):
        plt.annotate(
            grid[i][j].foram.chambers,
            xy=(i, j), xytext=(-5, 5),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))


class CsvStatistics(Statistics):
    @Inject("environment")
    def __init__(self, interval=1, filename=None):
        super(CsvStatistics, self).__init__()
        self.interval = interval
        self.filename = "forams-%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S") if filename is None else filename
        self.died_so_far = 0
        self.born_so_far = 0

    def update(self, step_count, agents):
        if step_count % self.interval == 0:
            with open(self.filename, 'ab') as f:
                entry = self._get_entry(agents, step_count)
                print((",".join(map(str, entry))), file=f)
        self.died_so_far = Foram._die.called
        self.born_so_far = Foram._create_child.called

    def summarize(self, agents):
        pass

    def _get_entry(self, agents, step_count):
        forams_count = len(agents[0].forams)
        entry = [step_count, forams_count,
                 sum(f.chambers for f in agents[0].forams.values()),
                 Foram._die.called - self.died_so_far,
                 Foram._create_child.called - self.born_so_far]
        return entry


class PsiStatistics(Statistics):
    @Inject("environment", "insolation_meter", "stop_condition")
    def __init__(self, interval=1, filename=None):
        super(PsiStatistics, self).__init__()
        self.interval = interval
        self._column_names = ['"x"', '"y"', '"z"', '"Foram"', '"Energy"', '"Algae"', '"Insolation"']
        self._column_symbols = ['"F"', '"E"', '"A"', '"I"']
        self._column_types = ['float', 'float', 'float', 'float']
        self.filename = "forams-%s" % datetime.now().strftime("%Y%m%d_%H%M%S") if filename is None else filename
        self.counter = 0

    def update(self, step_count, agents):
        if step_count % self.interval == 0:
            self.counter += 1
            new_filename = '%s%s.psi' % (self.filename, '%06d' % self.counter)
            with open(new_filename, 'w') as f:
                cells = self._get_nonempty_cells(step_count)
                self._add_header(f, len(cells))
                self._add_data(f, cells)

    def summarize(self, agents):
        pass

    def _get_nonempty_cells(self, step):
        nonempty_cells = []

        for x in range(len(self.environment.grid)):
            for y in range(len(self.environment.grid[x])):
                for z in range(len(self.environment.grid[x][y])):
                    entry = self._get_entry(x, y, z, step)
                    if entry:
                        nonempty_cells.append(self._get_entry(x, y, z, step))

        return nonempty_cells

    def _get_entry(self, x, y, z, step):
        cell = self.environment.grid[x][y][z]
        if cell.is_empty() and cell.algae == 0:
            return None
        return map(float, [x, y, z] + [0 if cell.is_empty() else cell.foram.chambers,
                                       0 if cell.is_empty() else cell.foram.energy,
                                       cell.algae,
                                       self.insolation_meter.get_insolation(cell, step)])

    def _add_header(self, f, cells_count):
        f.write('# PSI Format 1.0\n#\n')
        self._add_column_names(f)
        self._add_column_symbols(f)
        self._add_column_types(f)
        f.write('%d 2694 115001\n'
                '1.00 0.00 0.00\n'
                '0.00 1.00 0.00\n'
                '0.00 0.00 1.00\n\n'
                % cells_count)

    def _add_data(self, f, cells):
        for c in cells:
            f.write(' '.join(map(str, c)) + '\n')

    def _add_column_names(self, f):
        names = (['# column[%d] = %s' % (i, n) for i, n in enumerate(self._column_names)])
        f.write('\n'.join(names) + '\n')

    def _add_column_symbols(self, f):
        symbols = ['# symbol[%d] = %s' % (i + 3, s) for i, s in enumerate(self._column_symbols)]
        f.write('\n'.join(symbols) + '\n')

    def _add_column_types(self, f):
        types = ['# type[%d] = %s' % (i + 3, t) for i, t in enumerate(self._column_types)]
        f.write('\n'.join(types) + '\n')


class SimpleStatistics(Statistics):
    @Inject("environment", "insolation_meter")
    def __init__(self):
        super(SimpleStatistics, self).__init__()

    def update(self, step_count, agents):
        if step_count % 150 == 0:
            logger.info(self.environment.grid)

    def summarize(self, agents):
        logger.debug("done")


class MultipleStatistics(Statistics):
    def __init__(self, stats):
        super(MultipleStatistics, self).__init__()
        self.stats = stats

    def update(self, step_count, agents):
        for s in self.stats:
            s.update(step_count, agents)

    def summarize(self, agents):
        for s in self.stats:
            s.summarize(agents)
