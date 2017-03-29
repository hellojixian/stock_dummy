import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import gridspec
import numpy as np
import talib as ta
import pandas as pd
import numpy as np


def plot_kchart(secId, quotes):
    fig = plt.figure(figsize=(12, 8))
    fig.set_tight_layout(True)
    gs = gridspec.GridSpec(10, 1)

    ax1 = fig.add_subplot(gs[:7, 0])
    ax1.set_title('{} to {}'.format(quotes.ix[0, 'date'], quotes.ix[len(quotes)-1, 'date']))
    ax1.set_axisbelow(True)
    ax2 = fig.add_subplot(gs[7:, 0])
    ax2.set_axisbelow(True)
    ax1.grid(True)
    ax1.grid(which='minor', alpha=0.2)
    ax1.grid(which='major', alpha=0.5)
    ax2.grid(True)
    ax1.set_xlim(-1, len(quotes))
    ax2.set_xlim(-1, len(quotes))

    for i in range(len(quotes)):
        close_price = quotes.ix[i, 'close']
        open_price = quotes.ix[i, 'open']
        high_price = quotes.ix[i, 'high']
        low_price = quotes.ix[i, 'low']
        vol = quotes.ix[i, 'vol'] / 10000
        if close_price > open_price:
            color = 'red'
            ax1.add_patch(
                patches.Rectangle((i - 0.4, open_price), 0.8, close_price - open_price, fill=True, color=color))
            ax1.plot([i, i], [low_price, open_price], color)
            ax1.plot([i, i], [close_price, high_price], color)
            ax2.add_patch(patches.Rectangle((i - 0.4, 0), 0.8, vol, fill=True, color=color, alpha=1))
        else:
            color = 'darkcyan'
            ax1.add_patch(
                patches.Rectangle((i - 0.4, open_price), 0.8, close_price - open_price, fill=True, color=color))
            ax1.plot([i, i], [low_price, high_price], color=color)
            ax2.add_patch(patches.Rectangle((i - 0.4, 0), 0.8, vol, fill=True, color=color, alpha=1))
    ax1.set_title(str(secId).upper(), fontsize=15, loc='left', color='r')
    ax2.set_title('Volume', fontsize=15, loc='left', color='r')

    ax1.set_yticks(np.arange(np.min(quotes['low']), np.max(quotes['high']), 1))
    ax1.set_yticks(np.arange(np.min(quotes['low']), np.max(quotes['high']), 0.2), minor=True)
    ax1.set_xticks(range(0, len(quotes), int(len(quotes) * 1 / 8)))
    ax2.set_xticks(range(0, len(quotes), int(len(quotes) * 1 / 8)))
    ax1.set_xticklabels([quotes.ix[index, 'date'] for index in ax1.get_xticks()])
    ax2.set_xticklabels([quotes.ix[index, 'date'] for index in ax2.get_xticks()])

    ma5 = ta.MA(quotes['close'].values, timeperiod=5, matype=0)
    ma10 = ta.MA(quotes['close'].values, timeperiod=10, matype=0)
    ma30 = ta.MA(quotes['close'].values, timeperiod=30, matype=0)
    ma60 = ta.MA(quotes['close'].values, timeperiod=60, matype=0)
    ax1.plot(ma5, color='b', linewidth=1)
    ax1.plot(ma10, color='firebrick', linewidth=1)
    ax1.plot(ma30, color='forestgreen', linewidth=1)
    ax1.plot(ma60, color='darkmagenta', linewidth=1)
    ax1.annotate('MA5-', xy=(0.02, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold', color='b',
                 fontsize=10)
    ax1.annotate('MA10-', xy=(0.07, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='firebrick', fontsize=10)
    ax1.annotate('MA30-', xy=(0.12, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='forestgreen', fontsize=10)
    ax1.annotate('MA60-', xy=(0.17, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='darkmagenta', fontsize=10)

    vol30 = ta.MA(quotes['vol'].values, timeperiod=30, matype=0)
    vol60 = ta.MA(quotes['vol'].values, timeperiod=60, matype=0)
    vol30 /= 10000
    vol60 /= 10000
    ax2.plot(vol30, color='b', linewidth=1)
    ax2.plot(vol60, color='firebrick', linewidth=1)
    ax2.annotate('VMA30-', xy=(0.02, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='b', fontsize=10)
    ax2.annotate('VMA60-', xy=(0.1, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='firebrick', fontsize=10)

    return plt
