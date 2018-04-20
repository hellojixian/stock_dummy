from Common import config
from matplotlib import ticker
import matplotlib.patches as patches
import numpy as np

class EnvironmentAnalysis:
    def __init__(self, ax):
        self._ax = ax
        self._account = None
        self._engine = None
        self._data = None
        self._labels = ['close', 'bar', 'vol', '',
                        'open', 'high', 'low', 'close', 'up', 'down', 'bar', 'vol', '',
                        'open_3', 'high_3', 'low_3', 'close_3',
                        'open_2', 'high_2', 'low_2', 'close_2',
                        'open', 'high', 'low', 'close',
                        'up', 'down', 'bar', 'vol', '',
                        'open']
        return

    def draw(self, engine):
        self._ax.clear()
        self._data = engine.get_static_env()
        self._ax.set_title('Environment Analysis', fontsize=config.LARGE_FONT_SIZE, loc='left', color='black')

        for tick in self._ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(config.SMALL_FONT_SIZE)
        for tick in self._ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(config.MIDDLE_FONT_SIZE)

        data = self._data
        y_max = 10
        y_min = -10

        self._draw_bar(0, 'stock', data['prev3']['stock']['change'])
        self._draw_bar(1, 'stock', data['prev3']['stock']['bar'])
        self._draw_bar(2, 'stock', data['prev3']['stock']['vol60'])
        self._draw_bar(0, 'index', data['prev3']['index']['change'])
        self._draw_bar(1, 'index', data['prev3']['index']['bar'])
        self._draw_bar(2, 'index', data['prev3']['index']['vol60'])
        self._annotate_bar(0, data['prev3']['stock']['change'])
        self._annotate_bar(1, data['prev3']['stock']['bar'])
        self._annotate_bar(2, data['prev3']['stock']['vol60'])
        self._ax.plot([3, 3], [y_min, y_max], linewidth=1, color='black', alpha=0.5)

        self._ax.add_patch(patches.Rectangle((3.5, y_max), 4, y_min, fill=True, color='black', alpha=0.1))
        self._ax.add_patch(patches.Rectangle((3.5, y_min), 4, y_max, fill=True, color='black', alpha=0.1))
        self._draw_bar(4, 'stock', data['prev2']['stock']['open'])
        self._draw_bar(5, 'stock', data['prev2']['stock']['high'])
        self._draw_bar(6, 'stock', data['prev2']['stock']['low'])
        self._draw_bar(7, 'stock', data['prev2']['stock']['close'])
        self._draw_bar(8, 'stock', data['prev2']['stock']['upline'])
        self._draw_bar(9, 'stock', data['prev2']['stock']['downline'])
        self._draw_bar(10, 'stock', data['prev2']['stock']['bar'])
        self._draw_bar(11, 'stock', data['prev2']['stock']['vol60'])
        self._draw_bar(4, 'index', data['prev2']['index']['open'])
        self._draw_bar(5, 'index', data['prev2']['index']['high'])
        self._draw_bar(6, 'index', data['prev2']['index']['low'])
        self._draw_bar(7, 'index', data['prev2']['index']['close'])
        self._draw_bar(8, 'index', data['prev2']['index']['upline'])
        self._draw_bar(9, 'index', data['prev2']['index']['downline'])
        self._draw_bar(10, 'index', data['prev2']['index']['bar'])
        self._draw_bar(11, 'index', data['prev2']['index']['vol60'])
        self._annotate_bar(4, data['prev2']['stock']['open'])
        self._annotate_bar(5, data['prev2']['stock']['high'])
        self._annotate_bar(6, data['prev2']['stock']['low'])
        self._annotate_bar(7, data['prev2']['stock']['close'])
        self._annotate_bar(8, data['prev2']['stock']['upline'])
        self._annotate_bar(9, data['prev2']['stock']['downline'])
        self._annotate_bar(10, data['prev2']['stock']['bar'])
        self._annotate_bar(11, data['prev2']['stock']['vol60'])
        self._ax.plot([12, 12], [y_min, y_max], linewidth=1, color='black', alpha=0.5)

        self._ax.add_patch(patches.Rectangle((12.5, y_max), 4, y_min, fill=True, color='black', alpha=0.1))
        self._ax.add_patch(patches.Rectangle((12.5, y_min), 4, y_max, fill=True, color='black', alpha=0.1))
        self._ax.add_patch(patches.Rectangle((20.5, y_max), 4, y_min, fill=True, color='black', alpha=0.1))
        self._ax.add_patch(patches.Rectangle((20.5, y_min), 4, y_max, fill=True, color='black', alpha=0.1))
        self._draw_bar(13, 'stock', data['prev']['stock']['open_3'])
        self._draw_bar(14, 'stock', data['prev']['stock']['high_3'])
        self._draw_bar(15, 'stock', data['prev']['stock']['low_3'])
        self._draw_bar(16, 'stock', data['prev']['stock']['close_3'])
        self._draw_bar(17, 'stock', data['prev']['stock']['open_2'])
        self._draw_bar(18, 'stock', data['prev']['stock']['high_2'])
        self._draw_bar(19, 'stock', data['prev']['stock']['low_2'])
        self._draw_bar(20, 'stock', data['prev']['stock']['close_2'])
        self._draw_bar(21, 'stock', data['prev']['stock']['open'])
        self._draw_bar(22, 'stock', data['prev']['stock']['high'])
        self._draw_bar(23, 'stock', data['prev']['stock']['low'])
        self._draw_bar(24, 'stock', data['prev']['stock']['close'])
        self._draw_bar(25, 'stock', data['prev']['stock']['upline'])
        self._draw_bar(26, 'stock', data['prev']['stock']['downline'])
        self._draw_bar(27, 'stock', data['prev']['stock']['bar'])
        self._draw_bar(28, 'stock', data['prev']['stock']['vol60'])
        self._draw_bar(13, 'index', data['prev']['index']['open'])
        self._draw_bar(14, 'index', data['prev']['index']['high_3'])
        self._draw_bar(15, 'index', data['prev']['index']['low_3'])
        self._draw_bar(16, 'index', data['prev']['index']['close_3'])
        self._draw_bar(17, 'index', data['prev']['index']['open_2'])
        self._draw_bar(18, 'index', data['prev']['index']['high_2'])
        self._draw_bar(19, 'index', data['prev']['index']['low_2'])
        self._draw_bar(20, 'index', data['prev']['index']['close_2'])
        self._draw_bar(21, 'index', data['prev']['index']['open'])
        self._draw_bar(22, 'index', data['prev']['index']['high'])
        self._draw_bar(23, 'index', data['prev']['index']['low'])
        self._draw_bar(24, 'index', data['prev']['index']['close'])
        self._draw_bar(25, 'index', data['prev']['index']['upline'])
        self._draw_bar(26, 'index', data['prev']['index']['downline'])
        self._draw_bar(27, 'index', data['prev']['index']['bar'])
        self._draw_bar(28, 'index', data['prev']['index']['vol60'])
        self._annotate_bar(13, data['prev']['stock']['open_3'])
        self._annotate_bar(14, data['prev']['stock']['high_3'])
        self._annotate_bar(15, data['prev']['stock']['low_3'])
        self._annotate_bar(16, data['prev']['stock']['close_3'])
        self._annotate_bar(17, data['prev']['stock']['open_2'])
        self._annotate_bar(18, data['prev']['stock']['high_2'])
        self._annotate_bar(19, data['prev']['stock']['low_2'])
        self._annotate_bar(20, data['prev']['stock']['close_2'])
        self._annotate_bar(21, data['prev']['stock']['open'])
        self._annotate_bar(22, data['prev']['stock']['high'])
        self._annotate_bar(23, data['prev']['stock']['low'])
        self._annotate_bar(24, data['prev']['stock']['close'])
        self._annotate_bar(25, data['prev']['stock']['upline'])
        self._annotate_bar(26, data['prev']['stock']['downline'])
        self._annotate_bar(27, data['prev']['stock']['bar'])
        self._annotate_bar(28, data['prev']['stock']['vol60'])
        self._ax.plot([29, 29], [y_min, y_max], linewidth=1, color='black', alpha=0.5)

        self._draw_bar(30, 'stock', data['current']['stock']['open'])
        self._draw_bar(30, 'index', data['current']['index']['open'])
        self._annotate_bar(30, data['current']['stock']['open'])

        self._ax.set_xticks(range(0, 31))
        self._ax.set_xticklabels(self._labels, rotation=90,
                                 rotation_mode="anchor", ha='right', va='center')
        self._ax.set_yticklabels(range(-10, 11))
        self._ax.set_ylim(y_min, y_max)
        self._ax.set_xlim(-0.5, 30.5)

        self._ax.set_yticks(np.linspace(y_min, y_max, 11), minor=False)
        self._ax.set_yticks(np.linspace(y_min, y_max, 21), minor=True)
        self._ax.grid(True)
        self._ax.grid(which='major', alpha=0.6)
        self._ax.grid(which='minor', alpha=0.3)

        self._draw_legend()
        return

    def _draw_legend(self):
        y_pos = 9.8
        self._ax.annotate('Prev 3',
                          xy=(-0.5, y_pos), xycoords='data',
                          color='black', weight='bold',
                          ha='left', va='top', rotation=0,
                          fontsize=7)
        self._ax.annotate('Previous 2',
                          xy=(3.1, y_pos), xycoords='data',
                          color='black', weight='bold',
                          ha='left', va='top', rotation=0,
                          fontsize=7)
        self._ax.annotate('Previous',
                          xy=(12.1, y_pos), xycoords='data',
                          color='black', weight='bold',
                          ha='left', va='top', rotation=0,
                          fontsize=7)
        self._ax.annotate('Cur',
                          xy=(29.1, y_pos), xycoords='data',
                          color='black', weight='bold',
                          ha='left', va='top', rotation=0,
                          fontsize=7)

        def _y_formatter(y, p):
            return "{:g}%".format(y)

        self._ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))
        return

    def _annotate_bar(self, pos, value):
        if value > 0:
            sign = '+'
            color = 'red'
        else:
            sign = ''
            color = 'green'
        self._ax.annotate('{}{:.2f}%'.format(sign, value),
                          xy=(pos, -9.6), xycoords='data',
                          color=color, weight='bold',
                          ha='center', va='bottom', rotation=90,
                          fontsize=7)
        return

    def _draw_bar(self, pos, type, value):
        if value > 0:
            color = 'red'
        else:
            color = 'green'

        if type == 'index':
            offset = 0.15
            if color == 'red':
                color = 'firebrick'
            elif color == 'green':
                color = 'darkgreen'
        else:
            offset = - 0.15

        self._ax.bar(pos + offset, value, 0.3, color=color)
        return
