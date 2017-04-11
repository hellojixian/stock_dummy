import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import numpy as np

fig = None
ax1, ax2, ax3, ax4, ax5 = None, None, None, None, None
vol_scale_rate = 0.0001


def plot_kchart(secId, quotes):
    global fig, ax1, ax2, ax3, ax4, ax5
    vol30 = quotes['vol_ma30'].values * vol_scale_rate
    vol60 = quotes['vol_ma60'].values * vol_scale_rate

    if fig is None:
        fig = plt.figure(figsize=(16, 8))
        fig.set_tight_layout(True)
        gs = mpl.gridspec.GridSpec(10, 9)

        ax1 = fig.add_subplot(gs[:5, 0:6])
        ax2 = fig.add_subplot(gs[5:7, 0:6])
        ax3 = fig.add_subplot(gs[7:10, 0:6])
        ax4 = fig.add_subplot(gs[0:5, 6:])
        ax5 = fig.add_subplot(gs[5:10, 6:])

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

    ax1.plot(quotes['close'].values, color='black', linewidth=1, alpha=0.3)
    ax1.plot(quotes['ma5'].values, color='b', linewidth=1)
    ax1.plot(quotes['ma10'].values, color='firebrick', linewidth=1)
    ax1.plot(quotes['ma30'].values, color='forestgreen', linewidth=1)
    ax1.plot(quotes['ma60'].values, color='darkmagenta', linewidth=1)
    ax1.annotate('Close-', xy=(0.02, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold', color='black',
                 fontsize=10)
    ax1.annotate('MA5-', xy=(0.085, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold', color='b',
                 fontsize=10)
    ax1.annotate('MA10-', xy=(0.13, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='firebrick', fontsize=10)
    ax1.annotate('MA30-', xy=(0.20, 0.95), xycoords="axes fraction",
                 va='top', ha='left', weight='extra bold',
                 color='forestgreen', fontsize=10)
    ax1.annotate('MA60-', xy=(0.27, 0.95), xycoords="axes fraction",
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
                ax1.scatter(i, quotes['sar'].values[i], color='red', marker='o', alpha=0.4)
            else:
                ax1.scatter(i, np.abs(quotes['sar'].values[i]), color='green', marker='o', alpha=0.4)

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

    return [ax1, ax2, ax3, ax4, ax5]


def plot_realtime_chart(ax, m_data, params):
    ax.clear()
    trading_mins = 240
    font_size = 8
    prev_close = params['prev_close']

    close_price = m_data.iloc[-1]['close']
    open_price = m_data.iloc[0]['open']
    lowest_price = np.min(m_data['low'].values)
    lowest_change = (lowest_price - prev_close) / prev_close * 100
    lowest_pos = list(m_data['low'].values).index(lowest_price)
    lowest_time = m_data['time'].iloc[lowest_pos]
    lowest_time = "{:02d}:{:02d}".format(int(lowest_time.seconds / 3600),
                                         (lowest_time.seconds % 3600) // 60)

    highest_price = np.max(m_data['high'].values)
    highest_change = (highest_price - prev_close) / prev_close * 100
    highest_pos = list(m_data['high'].values).index(highest_price)
    highest_time = m_data['time'].iloc[highest_pos]
    highest_time = "{:02d}:{:02d}".format(int(highest_time.seconds / 3600),
                                          (highest_time.seconds % 3600) // 60)

    # 绘制中午分割线
    min_labels = ['09:30', '10:00', '10:30', '11:00', '11|13',
                  '13:30', '14:00', '14:30', '15:00']
    ax.set_xticks(range(0, trading_mins + 1, 30))
    ax.set_xticklabels(min_labels)

    # 昨日收盘价 - 零轴
    ax.plot([0, 241], [prev_close, prev_close], color='blue', alpha=0.8, linewidth=1, linestyle='--')

    price_limit_max = prev_close * 1.11
    price_limit_min = prev_close * 0.89
    ax.plot([trading_mins / 2, trading_mins / 2], [price_limit_min, price_limit_max],
            color='black', alpha=0.5, linewidth=0.5)
    ax.set_ylim(price_limit_min, price_limit_max)
    ax.set_xlim(0, trading_mins)
    ax.annotate(params['title'], xy=(0.99, 0.95),
                xycoords="axes fraction",
                va='top', ha='right', weight='bold',
                color='red', fontsize=10)

    y_labels = ["", "", "- 9%", "", "- 7%", "", "- 5%", "", "- 3%", "", "- 1%", "------",
                "1%", "", "3%", "", "5%", "", "7%", "", "9%", "", ""]
    ax.set_yticks(np.linspace(price_limit_min, price_limit_max, 23), minor=False)
    ax.set_yticklabels(y_labels, minor=False)
    ax.grid(True)
    ax.grid(which='major', alpha=0.5)

    # 绘制当日分时图
    line_data = [open_price] + list(m_data['close'].values.tolist())
    ax.plot(range(0, len(line_data)), line_data, color='blue',
            alpha=0.5, linewidth=1.5, linestyle='-')

    # 标记关键价格 - prev_close / open
    if open_price > prev_close:
        color = 'red'
        open_anno_offset = 20
        open_va = "bottom"
        prev_close_offset = -open_anno_offset
        prev_close_va = "top"
    else:
        color = 'green'
        open_va = "top"
        open_anno_offset = -20
        prev_close_offset = -open_anno_offset
        prev_close_va = "bottom"
    open_change = (open_price - prev_close) / prev_close * 100
    ax.annotate('{0:.2f}'.format(prev_close),
                xy=(0, prev_close),
                xycoords="data",
                xytext=(-30, prev_close_offset),
                backgroundcolor='white',
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='black', alpha=0.7),
                va=prev_close_va, ha='right', weight='normal',
                color='black', fontsize=font_size, alpha=0.7)
    ax.annotate('O: {:.2f} ({:.2f}%)'.format(open_price, open_change),
                xy=(0, open_price),
                xycoords="data",
                backgroundcolor='white',
                xytext=(0, open_anno_offset),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='black'),
                va=open_va, ha='right', weight='bold',
                color=color, fontsize=font_size)
    # 标记关键价格 -  close
    if close_price > prev_close:
        color = 'red'
        close_va = 'top'
        close_anno_offset = -20
    else:
        color = 'green'
        close_va = 'bottom'
        close_anno_offset = 20
    close_change = (close_price - prev_close) / prev_close * 100
    open_close_change = (close_price - open_price) / open_price * 100
    ax.annotate('C: {:.2f} ({:.2f}%)'.format(close_price, close_change, open_close_change),
                xy=(240, close_price),
                xycoords="data",
                xytext=(0, close_anno_offset),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='black'),
                va=close_va, ha='right', weight='bold',
                color=color, fontsize=font_size)

    # 标记关键价格 - high(red)
    if int(highest_time[0:2]) < 12:
        highest_time += ' AM'
    else:
        highest_time += ' PM'
    ax.annotate('H: {:.2f} ({:.2f}%)\n'
                'T: {}'.format(highest_price, highest_change, highest_time),
                xy=(highest_pos + 1, highest_price),
                xycoords="data",
                xytext=(0, 15),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='red'),
                va='bottom', ha='center', weight='normal', alpha=1,
                color='red', fontsize=font_size)

    # 标记关键价格 - low(green)
    if int(highest_time[0:2]) < 12:
        lowest_time += ' AM'
    else:
        lowest_time += ' PM'
    ax.annotate('L: {:.2f} ({:.2f}%)\n'
                'T: {}'.format(lowest_price, lowest_change, lowest_time),
                xy=(lowest_pos + 1, lowest_price),
                xycoords="data",
                xytext=(0, -15),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='green'),
                va='top', ha='center', weight='normal', alpha=1,
                color='green', fontsize=font_size)
    pass


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

        ax1, ax2, ax3 = plot_kchart(secId, data_slice)
        ax3.plot(range(i, i + view_size + 1), baseline[i:], color='black')
        ax3.set_xlim(i - 1, i + view_size + 1)
        ax3.annotate('Baseline: {}%'.format(baseline_return), xy=(0.02, 0.95),
                     xycoords="axes fraction",
                     va='top', ha='left', weight='extra bold',
                     color='black', fontsize=10)
        plt.pause(0.2)
    plt.ioff()
    plt.show()
