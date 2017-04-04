import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import numpy as np

fig = None
ax1, ax2, ax3 = None, None, None
vol_scale_rate = 0.0001


def plot_kchart(secId, quotes):
    global fig, ax1, ax2, ax3
    vol30 = quotes['vol_ma30'].values * vol_scale_rate
    vol60 = quotes['vol_ma60'].values * vol_scale_rate

    if fig is None:
        fig = plt.figure(figsize=(12, 8))
        fig.set_tight_layout(True)
        gs = mpl.gridspec.GridSpec(10, 1)

        ax1 = fig.add_subplot(gs[:5, 0])
        ax2 = fig.add_subplot(gs[5:7, 0])
        ax3 = fig.add_subplot(gs[7:10, 0])

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax1.set_title('{} to {}'.format(quotes.ix[0].name,
                                    quotes.ix[-1].name))
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)
    ax1.grid(True)
    ax1.grid(which='minor', alpha=0.2)
    ax1.grid(which='major', alpha=0.5)
    ax2.grid(True)
    ax3.grid(True)
    ax1.set_xlim(-1, len(quotes))
    ax2.set_xlim(-1, len(quotes))

    ax1.set_title(str(secId).upper(), fontsize=15, loc='left', color='r')
    ax2.set_title('Volume', fontsize=15, loc='left', color='r')
    ax3.set_title('Returns', fontsize=15, loc='left', color='r')

    ax1.set_yticks(np.arange(np.min(quotes['low']) - 1, np.max(quotes['high']) + 1, 1))
    ax1.set_yticks(np.arange(np.min(quotes['low']) - 1, np.max(quotes['high']) + 1, 0.2), minor=True)
    ax1.set_xticks(range(0, len(quotes), int(len(quotes) * 1 / 8)))
    ax2.set_xticks(range(0, len(quotes), int(len(quotes) * 1 / 8)))
    ax1.set_xticklabels([quotes.ix[index].name for index in ax1.get_xticks()])
    ax2.set_xticklabels([quotes.ix[index].name for index in ax2.get_xticks()])
    ax2.set_ylim(0, np.max(quotes['vol']) * vol_scale_rate * 1.2)

    ax1.plot(quotes['close'].values, color='black', linewidth=1,alpha=0.3)
    ax1.plot(quotes['ma5'].values, color='b', linewidth=1)
    ax1.plot(quotes['ma10'].values, color='firebrick', linewidth=1)
    ax1.plot(quotes['ma30'].values, color='forestgreen', linewidth=1)
    ax1.plot(quotes['ma60'].values, color='darkmagenta', linewidth=1)
    ax1.annotate('Close-', xy=(0.02, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold', color='black',
                 fontsize=10)
    ax1.annotate('MA5-', xy=(0.075, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold', color='b',
                 fontsize=10)
    ax1.annotate('MA10-', xy=(0.12, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='firebrick', fontsize=10)
    ax1.annotate('MA30-', xy=(0.17, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='forestgreen', fontsize=10)
    ax1.annotate('MA60-', xy=(0.22, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='darkmagenta', fontsize=10)

    ax2.plot(vol30, color='b', linewidth=1)
    ax2.plot(vol60, color='firebrick', linewidth=1)
    ax2.annotate('VMA30-', xy=(0.02, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='b', fontsize=10)
    ax2.annotate('VMA60-', xy=(0.1, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='firebrick', fontsize=10)

    if 'sar' in quotes.columns:
        for i in range(len(quotes)):
            if quotes['sar'].values[i] > 0:
                ax1.scatter(i, quotes['sar'].values[i], color='red', marker='o', alpha=0.6)
            else:
                ax1.scatter(i, np.abs(quotes['sar'].values[i]), color='green', marker='o', alpha=0.6)

    for i in range(len(quotes)):
        close_price = quotes.loc[:, 'close'].iloc[i]
        open_price = quotes.loc[:, 'open'].iloc[i]
        high_price = quotes.loc[:, 'high'].iloc[i]
        low_price = quotes.loc[:, 'low'].iloc[i]
        vol = quotes.loc[:, 'vol'].iloc[i] * vol_scale_rate
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

    return [ax1, ax2, ax3]


def animate_data(secId, data):
    window_size = 0
    view_size = 80
    baseline = list(np.ones(view_size) * 100)
    plt.ion()
    for i in range(window_size, len(data) - view_size):
        data_slice = data[i:i + view_size]
        last_percent = float(baseline[-1])
        last_pchange = float(data_slice.iloc[-1]['change']) + 1
        baseline_return = round(last_percent * last_pchange, 2)
        baseline.append(baseline_return)

        print(i, baseline[-1])
        ax1, ax2, ax3 = plot_kchart(secId, data_slice)
        ax3.plot(range(i, i + view_size + 1), baseline[i:], color='black')
        ax3.set_xlim(i-1, i + view_size + 1)
        ax3.annotate('Baseline: {}%'.format(baseline_return), xy=(0.02, 0.95),
                     xycoords="axes fraction",
                     va='top', ha='left', weight='extra bold',
                     color='black', fontsize=10)
        plt.pause(0.2)
    plt.ioff()
    plt.show()