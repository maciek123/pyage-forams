from __future__ import print_function
from datetime import datetime
import logging
import os

from pyage.core.inject import Inject
from pyage.core.statistics import Statistics
from pyage_forams.solutions.foram import Foram


logger = logging.getLogger(__name__)


class CsvStatistics(Statistics):
    @Inject("environment")
    def __init__(self, interval=1, filename=None):
        super(CsvStatistics, self).__init__()
        self.interval = interval
        self.filename = "forams-%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S") if filename is None else filename
        self.died_so_far = 0
        self.born_so_far = 0

    def update(self, step_count, agents):
        if step_count == 1:
            with open(self.filename, 'ab') as f:
                print(("No, Forams, ChambersAvg, AlgaeSum, Die, New"), file=f)
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
        if forams_count > 0:
            entry = [step_count, forams_count,
                     sum(f.chambers for f in agents[0].forams.values()) / forams_count,
                     self._get_algae_sum(),
                     Foram._die.called - self.died_so_far,
                     Foram._create_child.called - self.born_so_far]
        if forams_count < 1:
            entry = [step_count, 0, self._get_algae_sum(), 0, 0, 0]
        return entry

    def _get_algae_sum(self):
        return sum(c.get_algae() for c in self.environment.get_all_cells())


class PsiStatistics(Statistics):
    @Inject("environment", "insolation_meter", "stop_condition")
    def __init__(self, interval=1, filename=None):
        super(PsiStatistics, self).__init__()
        self.interval = interval
        self._column_names = ['"x"', '"y"', '"z"', '"Forams"', '"Algae"', '"Insolation"', '"Energy"', '"Chambers"']
        self._column_symbols = ['"F"', '"A"', '"I"', '"E"', '"C"']
        self._column_types = ['float', 'float', 'float', 'float', 'float']
        self._shifts = [(-0.25, -0.25, -0.25), (-0.25, 0.25, -0.25), (0.25, -0.25, -0.25), (0.25, 0.25, -0.25),
                        (-0.25, -0.25, 0.25), (-0.25, 0.25, 0.25), (0.25, -0.25, 0.25), (0.25, 0.25, 0.25)]
        self.filename = "forams-%s" % datetime.now().strftime("%Y%m%d_%H%M%S") if filename is None else filename
        os.mkdir(self.filename)
        self.filename = os.path.join(self.filename, self.filename)
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
                        nonempty_cells.extend(entry)

        return nonempty_cells

    def _get_entry(self, x, y, z, step):
        cell = self.environment.grid[x][y][z]
        if cell.is_empty() and cell.get_algae() == 0:
            return None
        if cell.is_empty() and cell.get_algae() > 0:
            return [map(float, [x, y, z] + [0,
                                            cell.get_algae(),
                                            self.insolation_meter.get_insolation(cell, step),
                                            0,
                                            0])]
        if len(cell.forams) == 1:
            foram = next(iter(cell.forams))
            return [map(float, [x, y, z] + [1,
                                            cell.get_algae(),
                                            self.insolation_meter.get_insolation(cell, step),
                                            foram.energy,
                                            foram.chambers])]
        if len(cell.forams) <= 8:
            entries = []
            for i, f in enumerate(cell.forams):
                shift = self._shifts[i]
                entries.append(map(float, [x + shift[0], y + shift[1], z + shift[2]] +
                                   [1,
                                    cell.get_algae(),
                                    self.insolation_meter.get_insolation(cell, step),
                                    f.energy,
                                    f.chambers]))
            return entries
        return [map(float, [x, y, z] + [len(cell.forams),
                                        cell.get_algae(),
                                        self.insolation_meter.get_insolation(cell, step)])]

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
