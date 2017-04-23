import numpy as np
import pandas as pd
from Common import config
from matplotlib import ticker
import matplotlib.patches as patches


class RealtimeChart:
    def __init__(self, ax):
        self._ax = ax
        self._vol_ax = self._ax.twinx()
        self._account = None
        self._engine = None
        self._quotes = pd.DataFrame()
        self._min_labels = [
            '09:30', '10:00', '10:30', '11:00', '|', '13:30', '14:00', '14:30',
            '|', '10:00', '10:30', '11:00', '|', '13:30', '14:00', '14:30', '15:00'
        ]
        return

    def draw(self, engine):
        self._ax.clear()

        account = engine.get_account()

        quotes = engine.get_minute_data()
        self._quotes = quotes

        self._account = account
        self._engine = engine

        self._ax.set_title('Realtime - {}'.format(account.current_date),
                           fontsize=config.LARGE_FONT_SIZE, loc='left', color='black')
        self._ax.set_xlim(-1, len(quotes) + 1)

        # draw prev date
        self._ax.plot(range(0, 240), quotes['close'].values[0:240], color='blue', linewidth=1)
        # draw today line
        self._ax.plot(range(240, 480), quotes['close'].values[240:480], color='blue', linewidth=1)

        self._draw_vol()
        self._draw_frame()
        self._draw_changes()
        self._draw_zero_axis()
        self._annotate_price()
        return

    def _draw_frame(self):
        for tick in self._ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(config.SMALL_FONT_SIZE)
        for tick in self._ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(config.MIDDLE_FONT_SIZE)

        y_min_limit, y_max_limit = self._get_ylim()
        # 中午分割线
        self._ax.plot([120, 120],
                      [y_min_limit * 0.99, y_max_limit * 1.01],
                      color='black', alpha=1,
                      linestyle='--', linewidth=0.5)

        self._ax.plot([360, 360],
                      [y_min_limit * 0.99, y_max_limit * 1.01],
                      color='black', alpha=1,
                      linestyle='--', linewidth=0.5)
        # 两日分割线
        self._ax.plot([240, 240],
                      [y_min_limit * 0.99, y_max_limit * 1.01],
                      color='black', alpha=1,
                      linestyle='--', linewidth=0.5)

        self._ax.set_xticks(range(0, len(self._quotes) + 1, 30))
        self._ax.set_xticklabels(self._min_labels)
        self._ax.set_yticks(np.linspace(y_min_limit, y_max_limit, 11), minor=False)
        self._ax.set_yticks(np.linspace(y_min_limit, y_max_limit, 21), minor=True)
        self._ax.grid(True)
        self._ax.grid(which='major', alpha=0.6)
        self._ax.grid(which='minor', alpha=0.3)

        price = self._get_zero_axis_price()
        self._ax.set_ylim(y_min_limit * 0.99, y_max_limit * 1.01)

        def _y_formatter(y, p):
            percent = round(((y - price) / price) * 100, 2)
            return "{:g}%".format(percent)

        self._ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))
        return

    def _get_prev_zero_axis_price(self):
        prev_2_date = self._engine.get_prev_date(offest=2)
        return self._engine.get_daily_data().loc[prev_2_date]['close']

    def _get_zero_axis_price(self):
        return self._quotes.iloc[239]['close']

    def _draw_zero_axis(self):
        # 绘制零轴
        quotes = self._quotes
        price = self._get_prev_zero_axis_price()
        self._ax.plot([0, 240],
                      [price, price],
                      color='black', alpha=1,
                      linestyle='--', linewidth=0.5)
        self._ax.annotate('pc: {:.2f}'.format(price),
                          xy=(10, price), xycoords='data',
                          xytext=(0, +15), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color='black', alpha=0.5),
                          color="black", weight='bold', alpha=0.5,
                          ha='center', va='bottom',
                          fontsize=config.SMALL_FONT_SIZE)

        price = self._get_zero_axis_price()
        self._ax.plot([240, len(quotes)],
                      [price, price],
                      color='black', alpha=1,
                      linestyle='--', linewidth=0.5)
        return

    def _draw_changes(self):
        prev_date = self._engine.get_prev_date(offest=1)
        prev_open = self._engine.get_daily_data().loc[prev_date]['open']
        prev_close = self._engine.get_daily_data().loc[prev_date]['close']
        if prev_close > prev_open:
            color = 'red'
            self._ax.add_patch(patches.Rectangle((0, prev_open),
                                                 width=240,
                                                 height=(prev_close - prev_open),
                                                 color=color, alpha=0.15))
        else:
            color = 'green'
            self._ax.add_patch(patches.Rectangle((0, prev_close),
                                                 width=240,
                                                 height=(prev_open - prev_close),
                                                 color=color, alpha=0.15))

        current_date = self._account.get_current_date()
        current_open = self._engine.get_daily_data().loc[current_date]['open']
        current_close = self._engine.get_daily_data().loc[current_date]['close']
        if current_close > current_open:
            color = 'red'
            self._ax.add_patch(patches.Rectangle((240, current_open),
                                                 width=240,
                                                 height=(current_close - current_open),
                                                 color=color, alpha=0.15))
        else:
            color = 'green'
            self._ax.add_patch(patches.Rectangle((240, current_close),
                                                 width=240,
                                                 height=(current_open - current_close),
                                                 color=color, alpha=0.15))

        return

    def _annotate_price(self):
        prev_2_date = self._engine.get_prev_date(offest=2)
        prev_2_close = self._engine.get_daily_data().loc[prev_2_date]['close']

        prev_date = self._engine.get_prev_date(offest=1)
        prev_open = self._engine.get_daily_data().loc[prev_date]['open']
        prev_close = self._engine.get_daily_data().loc[prev_date]['close']
        prev_open_change = (prev_open - prev_2_close) / prev_2_close * 100
        prev_close_change = (prev_close - prev_2_close) / prev_2_close * 100
        prev_high = self._engine.get_daily_data().loc[prev_date]['high']
        prev_low = self._engine.get_daily_data().loc[prev_date]['low']

        if prev_open > prev_2_close:
            color = 'red'
        else:
            color = 'green'

        if prev_open_change >= 0:
            prev_open_sign = '+'
        else:
            prev_open_sign = ''

        self._ax.annotate('o: {:.2f} ({}{:.2f}%)'.format(prev_open, prev_open_sign, prev_open_change),
                          xy=(0, prev_open), xycoords='data',
                          xytext=(10, -20), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color=color, alpha=0.6),
                          color=color, weight='bold', alpha=0.6,
                          backgroundcolor='white',
                          ha='center', va='top',
                          fontsize=config.SMALL_FONT_SIZE)
        if prev_close > prev_2_close:
            color = 'red'
            pos = 25
            va = 'bottom'
        else:
            color = 'green'
            pos = 25
            va = 'top'

        if prev_close_change >= 0:
            prev_close_sign = '+'
        else:
            prev_close_sign = ''

        self._ax.annotate('pc: {:.2f} ({}{:.2f}%)'.format(prev_close, prev_close_sign, prev_close_change),
                          xy=(239, prev_close), xycoords='data',
                          xytext=(-10, pos), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color=color, alpha=1),
                          color=color, weight='bold', alpha=1,
                          ha='center', va=va,
                          fontsize=config.SMALL_FONT_SIZE)

        current_date = self._account.get_current_date()
        current_open = self._engine.get_daily_data().loc[current_date]['open']
        current_close = self._engine.get_daily_data().loc[current_date]['close']
        current_open_change = (current_open - prev_close) / prev_close * 100
        current_close_change = (current_close - prev_close) / prev_close * 100
        current_high = self._engine.get_daily_data().loc[current_date]['high']
        current_low = self._engine.get_daily_data().loc[current_date]['low']
        if current_open > prev_close:
            color = 'red'
        else:
            color = 'green'

        if current_open_change >= 0:
            current_open_sign = '+'
        else:
            current_open_sign = ''
        self._ax.annotate('o: {:.2f} ({}{:.2f}%)'.format(current_open, current_open_sign, current_open_change),
                          xy=(240, current_open), xycoords='data',
                          xytext=(10, -20), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color=color, alpha=1),
                          color=color, weight='bold', alpha=1,
                          ha='center', va='top',
                          fontsize=config.SMALL_FONT_SIZE)
        if current_close > prev_close:
            color = 'red'
            pos = 25
            va = 'bottom'
        else:
            color = 'green'
            pos = -25
            va = 'top'

        if current_close_change >= 0:
            current_close_sign = '+'
        else:
            current_close_sign = ''

        self._ax.annotate('c: {:.2f} ({}{:.2f}%)'.format(current_close, current_close_sign, current_close_change),
                          xy=(480, current_close), xycoords='data',
                          xytext=(-10, pos), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color=color, alpha=1),
                          color=color, weight='bold', alpha=1,
                          backgroundcolor='white',
                          ha='center', va=va,
                          fontsize=config.SMALL_FONT_SIZE)
        return

    def _get_ylim(self):
        margin = 0.1
        price = self._get_zero_axis_price()
        y_min_limit = price * (1 - margin)
        y_max_limit = price * (1 + margin)
        return [y_min_limit, y_max_limit]

    def _draw_vol(self):
        self._vol_ax.clear()

        quotes = self._quotes

        for i in range(len(quotes)):
            close_price = quotes.loc[:, 'close'].iloc[i]
            open_price = quotes.loc[:, 'open'].iloc[i]
            vol = quotes.loc[:, 'vol'].iloc[i]
            if close_price > open_price:
                color = 'gray'
                self._vol_ax.add_patch(patches.Rectangle((i - 0.1, 0), 0.1, vol,
                                                         fill=True, color=color, alpha=0.5))
            else:
                color = 'silver'
                self._vol_ax.add_patch(patches.Rectangle((i - 0.1, 0), 0.1, vol,
                                                         fill=True, color=color, alpha=0.5))

        y_max = np.max(quotes['vol'].values)
        y_max_limit = y_max * 5
        self._vol_ax.set_xlim(-1, len(quotes))
        self._vol_ax.set_ylim(0, y_max_limit)

        def _y_formatter(y, p):
            return ""

        self._vol_ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))
        return
