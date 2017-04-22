import numpy as np
from Common import config
from matplotlib import ticker

window_size = 60
view_size = 70


class ReturnChart:
    def __init__(self, ax):
        self._ax = ax
        self._engine = None
        self._view_size = view_size
        self._window_size = window_size
        self._baseline_return = list(np.ones(self._window_size + 1) * 0.0)
        self._strategies_return = list(np.ones(self._window_size + 1) * 0.0)
        return

    def draw(self, engine):
        self._ax.clear()
        self._engine = engine

        account = engine.get_account()
        i = engine.get_day_count()

        self._ax.set_title('Return on Investment', fontsize=config.LARGE_FONT_SIZE, loc='left', color='black')

        # 更新数据
        self._baseline_return.append(account.baseline_return())
        self._strategies_return.append(account.strategies_return())

        # 收益率零轴
        self._ax.plot([i - 1, i + self._view_size + 1], [0, 0], color='black', linewidth=1.5, alpha=0.8)

        y_min_limit, y_max_limit = self._get_ylim()

        self._ax.grid(True)
        self._ax.set_xlim(i - 1, i + view_size + 1)
        self._ax.set_ylim(y_min_limit, y_max_limit)
        self._set_labels()
        self._draw_legends()
        self._draw_future_splitter()
        return

    def _draw_future_splitter(self):
        # 绘制未来分割线
        engine = self._engine
        i = engine.get_day_count()
        y_min_limit, y_max_limit = self._get_ylim()
        future_splitter = i + self._view_size - (self._view_size - self._window_size)
        self._ax.plot([future_splitter, future_splitter],
                      [y_min_limit, y_max_limit],
                      color='red', alpha=0.5)
        return

    def _draw_legends(self):
        engine = self._engine
        account = engine.get_account()
        i = engine.get_day_count()

        # 标记基线收益
        x = range(i - 1, len(self._baseline_return) - 1)
        baseline_y = np.array(self._baseline_return[i:])
        baseline_max = np.max(self._baseline_return)
        baseline_min = np.min(self._baseline_return)

        self._ax.plot(x, baseline_y, color='black', marker='.')
        self._ax.fill_between(x, 0, baseline_y, facecolor='gray', alpha=0.3)
        self._ax.set_xlim(i - 1, i + self._view_size + 1)
        self._ax.annotate('Baseline: {:.2f}%'.format(account.baseline_return()), xy=(0.02, 0.95),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='black', fontsize=config.SMALL_FONT_SIZE)

        self._ax.annotate('Max: {:.2f}%'.format(baseline_max), xy=(0.18, 0.95),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='black', fontsize=config.SMALL_FONT_SIZE)

        self._ax.annotate('Min: {:.2f}%'.format(baseline_min), xy=(0.3, 0.95),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='black', fontsize=config.SMALL_FONT_SIZE)

        if baseline_max != 0:
            baseline_max_pos = self._baseline_return.index(baseline_max) - 1
            self._ax.annotate('Max: {:.2f}%'.format(baseline_max),
                              xy=(baseline_max_pos, baseline_max), xycoords='data',
                              xytext=(-20, -5), textcoords='offset points',
                              arrowprops=dict(arrowstyle="->", color='black', alpha=0.8),
                              color="black", weight='bold', alpha=0.8,
                              ha='right', va='top',
                              fontsize=config.SMALL_FONT_SIZE)

        if baseline_min != 0:
            baseline_min_pos = self._baseline_return.index(baseline_min) - 1
            self._ax.annotate('Min: {:.2f}%'.format(baseline_min),
                              xy=(baseline_min_pos, baseline_min), xycoords='data',
                              xytext=(-20, +5), textcoords='offset points',
                              arrowprops=dict(arrowstyle="->", color='black', alpha=0.8),
                              color="black", weight='bold', alpha=0.8,
                              ha='right', va='bottom',
                              fontsize=config.SMALL_FONT_SIZE)

        # 标记策略收益
        strategy_y = np.array(self._strategies_return[i:])
        strategy_max = np.max(self._strategies_return)
        strategy_min = np.min(self._strategies_return)

        self._ax.plot(x, strategy_y, color='blue', marker='.')
        self._ax.fill_between(x, 0, strategy_y, facecolor='deepskyblue', alpha=0.3)
        self._ax.annotate('Strategy: {:.2f}%'.format(account.current_return()), xy=(0.02, 0.87),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='blue', fontsize=config.SMALL_FONT_SIZE)

        self._ax.annotate('Max: {:.2f}%'.format(strategy_max), xy=(0.18, 0.87),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='blue', fontsize=config.SMALL_FONT_SIZE)

        self._ax.annotate('Min: {:.2f}%'.format(strategy_min), xy=(0.3, 0.87),
                          xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='blue', fontsize=config.SMALL_FONT_SIZE)

        if strategy_max != 0:
            strategy_max_pos = self._strategies_return.index(strategy_max) - 1
            self._ax.annotate('Max: {:.2f}%'.format(strategy_max),
                              xy=(strategy_max_pos, strategy_max), xycoords='data',
                              xytext=(10, -5), textcoords='offset points',
                              arrowprops=dict(arrowstyle="->", color='blue', alpha=0.8),
                              color="blue", weight='bold', alpha=0.8,
                              ha='right', va='top',
                              fontsize=config.SMALL_FONT_SIZE)

        if strategy_min != 0:
            strategy_min_pos = self._strategies_return.index(strategy_min) - 1
            self._ax.annotate('Min: {:.2f}%'.format(strategy_min),
                              xy=(strategy_min_pos, strategy_min), xycoords='data',
                              xytext=(10, +5), textcoords='offset points',
                              arrowprops=dict(arrowstyle="->", color='blue', alpha=0.8),
                              color="blue", weight='bold', alpha=0.8,
                              ha='right', va='bottom',
                              fontsize=config.SMALL_FONT_SIZE)

        # 标记统计信息
        self._ax.annotate('Durtion: {}d'.format(i + 1), xy=(0.99, 0.94),
                          xycoords="axes fraction",
                          va='top', ha='right', weight='bold',
                          color='red', fontsize=config.SMALL_FONT_SIZE)
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
            x -= window_size
            if x >= 0:
                label = "{:g}d".format(x)
            else:
                label = '-'
            return label

        self._ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(_x_formatter))
        self._ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))
        return
