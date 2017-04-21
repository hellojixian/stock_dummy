import numpy as np
from Common import config
from matplotlib import ticker

window_size = 60
view_size = 70


class ReturnChart:
    def __init__(self, ax):
        self._ax = ax
        self._view_size = view_size
        self._window_size = window_size
        self._baseline_return = list(np.ones(self._window_size + 1) * 0)
        self._strategies_return = list(np.ones(self._window_size + 1) * 0)
        pass

    def draw(self, engine):
        account = engine.get_account()
        i = engine.get_day_count()
        print('i:', i)
        self._ax.clear()

        self._ax.set_title('Return', fontsize=config.LARGE_FONT_SIZE, loc='left', color='black')

        # 更新数据
        self._baseline_return.append(account.baseline_return())
        self._strategies_return.append(account.strategies_return())

        # 绘制基线收益
        x = range(i - 1, len(self._baseline_return) - 1)
        baseline_y = np.array(self._baseline_return[i:])
        self._ax.plot(x, baseline_y, color='black', marker='.')
        self._ax.fill_between(x, 0, baseline_y, facecolor='gray', alpha=0.3)
        self._ax.set_xlim(i - 1, i + self._view_size + 1)
        self._ax.annotate('Baseline: {}%'.format(account.baseline_return()), xy=(0.02, 0.95),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='black', fontsize=config.MIDDLE_FONT_SIZE)

        # 绘制策略收益
        strategy_y = np.array(self._strategies_return[i:])
        self._ax.plot(x, strategy_y, color='blue', marker='.')
        self._ax.fill_between(x, 0, strategy_y, facecolor='deepskyblue', alpha=0.3)
        self._ax.annotate('Strategy: {}%'.format(account.current_return()), xy=(0.02, 0.87),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='blue', fontsize=config.MIDDLE_FONT_SIZE)

        # 绘制未来分割线
        y_min_limit, y_max_limit = self._get_ylim()
        future_splitter = i + self._view_size - (self._view_size - self._window_size) - 1
        self._ax.plot([future_splitter, future_splitter],
                      [y_min_limit, y_max_limit],
                      color='red', alpha=0.5)

        # 收益率零轴
        self._ax.plot([i - 1, i + self._view_size + 1], [0, 0], color='black', linewidth=1.5, alpha=0.8)

        # 标记统计信息
        self._ax.annotate('Durtion: {}d'.format(i + 1), xy=(0.99, 0.94),
                          xycoords="axes fraction",
                          va='top', ha='right', weight='bold',
                          color='red', fontsize=config.MIDDLE_FONT_SIZE)

        self._ax.grid(True)
        self._ax.set_xlim(i - 1, i + view_size + 1)
        self._ax.set_ylim(y_min_limit, y_max_limit)
        self._set_labels()

        return

    def _get_ylim(self):
        min_return = np.min(list(self._strategies_return[-60:]) + list(self._baseline_return[-60:]))
        max_return = np.max(list(self._strategies_return[-60:]) + list(self._baseline_return[-60:]))

        min_return *= 1.1
        max_return *= 1.1

        if min_return == 0:
            min_return = -1

        if max_return == 0:
            max_return = 1

        return [min_return, max_return]

    def _set_labels(self):
        def _y_formatter(y, p):
            return "{:g}%".format(y)

        def _x_formatter(x, p):
            return "{:g}d".format(x)

        self._ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(_x_formatter))
        self._ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))
        return
