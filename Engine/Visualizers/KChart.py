import numpy as np
import pandas as pd
from Common import config
from matplotlib import ticker
import matplotlib.patches as patches

window_size = 60
view_size = 70


class KChart:
    def __init__(self, ax):
        self._ax = ax
        self._view_size = view_size
        self._window_size = window_size
        self._account = None
        self._engine = None
        self._quotes = pd.DataFrame()
        return

    def draw(self, engine):
        self._ax.clear()

        account = engine.get_account()
        i = engine.get_day_count()

        quotes = engine.get_daily_data()
        quotes = quotes[i + 1:i + view_size + 1]

        self._account = account
        self._engine = engine
        self._quotes = quotes
        y_min_limit, y_max_limit = self._get_ylim()
        self._ax.set_title('Candlestick Chart {}: {} to {}'
                           .format(str(engine.get_sec_id()).upper(), quotes.ix[0].name, quotes.ix[-1].name),
                           fontsize=config.LARGE_FONT_SIZE, loc='left', color='black')

        self._ax.set_axisbelow(True)

        self._ax.grid(True)
        self._ax.grid(which='minor', alpha=0.2)
        self._ax.grid(which='major', alpha=0.5)

        self._ax.set_yticks(np.linspace(y_min_limit, y_max_limit, 11))
        self._ax.set_yticks(np.linspace(y_min_limit, y_max_limit, 21), minor=True)
        self._ax.set_xticks(range(0, len(quotes), int(len(quotes) * 1 / 6)))
        self._ax.set_xticklabels([quotes.ix[index].name for index in self._ax.get_xticks()])

        self._ax.plot(quotes['close'].values, color='black', linewidth=1, alpha=0.3)
        self._ax.plot(quotes['ma5'].values, color='b', linewidth=1)
        self._ax.plot(quotes['ma10'].values, color='firebrick', linewidth=1)
        self._ax.plot(quotes['ma30'].values, color='forestgreen', linewidth=1)
        self._ax.plot(quotes['ma60'].values, color='darkmagenta', linewidth=1)

        for i in range(len(quotes)):
            close_price = quotes.loc[:, 'close'].iloc[i]
            open_price = quotes.loc[:, 'open'].iloc[i]
            high_price = quotes.loc[:, 'high'].iloc[i]
            low_price = quotes.loc[:, 'low'].iloc[i]
            if close_price > open_price:
                color = 'red'
                self._ax.add_patch(
                    patches.Rectangle((i - 0.4, open_price), 0.8, close_price - open_price, fill=True, color=color))
                self._ax.plot([i, i], [low_price, open_price], linewidth=0.9, color=color)
                self._ax.plot([i, i], [close_price, high_price], linewidth=0.9, color=color)

            else:
                color = 'darkcyan'
                self._ax.add_patch(
                    patches.Rectangle((i - 0.4, open_price), 0.8, close_price - open_price, fill=True, color=color))
                self._ax.plot([i, i], [low_price, high_price], linewidth=0.9, color=color)

        self._draw_legends(account)
        self._draw_sar()
        self._draw_future_splitter()
        self._draw_zero_axis()
        self._draw_annotations()
        self._set_labels()
        self._ax.set_xlim(-1, len(quotes))
        self._ax.set_ylim(y_min_limit, y_max_limit)
        return

    def _get_zero_axis_price(self):
        if len(self._quotes) > 2:
            return self._quotes.iloc[self._window_size - 2]['close']
        elif len(self._quotes) == 2:
            self._quotes.iloc[self._window_size - 1]['close']
        else:
            return 1

    def _get_latest_price(self):
        return self._account.get_security_price(self._engine.get_sec_id())

    def _draw_future_splitter(self):
        # 绘制未来分割线
        y_min_limit, y_max_limit = self._get_ylim()
        future_splitter = self._view_size - (self._view_size - self._window_size) - 1
        self._ax.plot([future_splitter, future_splitter],
                      [y_min_limit * 0.8, y_max_limit * 1.2],
                      color='red', alpha=0.5)
        return

    def _draw_zero_axis(self):
        # 绘制零轴
        quotes = self._quotes
        price = self._get_zero_axis_price()
        self._ax.plot([-1, len(quotes)],
                      [price, price],
                      color='black', alpha=1,
                      linestyle='--', linewidth=0.5)
        return

    def _draw_sar(self):
        quotes = self._quotes
        if 'sar' in quotes.columns:
            for i in range(len(quotes)):
                if quotes['sar'].values[i] > 0:
                    self._ax.scatter(i, quotes['sar'].values[i], color='red', marker='o', alpha=0.4)
                else:
                    self._ax.scatter(i, np.abs(quotes['sar'].values[i]), color='green', marker='o', alpha=0.4)

        return

    def _draw_legends(self, account):
        self._ax.annotate('Close-', xy=(0.02, 0.95), xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold', color='black',
                          fontsize=config.SMALL_FONT_SIZE)
        self._ax.annotate('MA5-', xy=(0.085, 0.95), xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold', color='b',
                          fontsize=config.SMALL_FONT_SIZE)
        self._ax.annotate('MA10-', xy=(0.13, 0.95), xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='firebrick', fontsize=config.SMALL_FONT_SIZE)
        self._ax.annotate('MA30-', xy=(0.20, 0.95), xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='forestgreen', fontsize=config.SMALL_FONT_SIZE)
        self._ax.annotate('MA60-', xy=(0.27, 0.95), xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='darkmagenta', fontsize=config.SMALL_FONT_SIZE)
        self._ax.annotate('Date: {}'.format(account.current_date), xy=(0.85, 0.95), xycoords="axes fraction",
                          va='top', ha='left', weight='extra bold',
                          color='red', fontsize=config.SMALL_FONT_SIZE)
        return

    def _draw_annotations(self):
        # 标记零轴的价格
        prev_close_price = self._get_zero_axis_price()
        close_price = self._get_latest_price()
        price_change = round(((close_price - prev_close_price) / prev_close_price) * 100, 2)
        self._ax.annotate('pc: {:.2f}'.format(prev_close_price),
                          xy=(self._window_size - 2, prev_close_price), xycoords='data',
                          xytext=(-15, +15), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color='black', alpha=0.8),
                          color="black", weight='bold', alpha=0.8,
                          ha='center', va='bottom',
                          fontsize=config.SMALL_FONT_SIZE)

        #  标记最后一日的收盘价(涨幅)
        if price_change >= 0:
            va = 'bottom'
            color = 'darkred'
            sign = '+'
            y_pos = 30
        else:
            va = 'top'
            color = 'darkgreen'
            sign = ''
            y_pos = -30

        self._ax.annotate('c: {:.2f} ({}{}%)'.format(close_price, sign, price_change),
                          xy=(self._window_size - 1, close_price), xycoords='data',
                          xytext=(-10, y_pos), textcoords='offset points',
                          arrowprops=dict(arrowstyle="->", color=color, alpha=1),
                          color=color, weight='bold', alpha=1,
                          backgroundcolor='white',
                          ha='center', va=va,
                          fontsize=config.SMALL_FONT_SIZE)
        return

    def _get_ylim(self):
        margin = 0.2
        price = self._get_zero_axis_price()
        y_min_limit = price * (1 - margin)
        y_max_limit = price * (1 + margin)
        return [y_min_limit, y_max_limit]

    def _set_labels(self):
        price = self._get_zero_axis_price()

        def _y_formatter(y, p):
            percent = round(((y - price) / price) * 100, 2)
            return "{:g}%".format(percent)

        self._ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))
        return
