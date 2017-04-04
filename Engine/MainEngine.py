import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Visualizers.CandleChart import plot_kchart


class account:
    cash = 0
    init_fund = 0
    history_data = None
    current_date = None
    current_time = None
    current_return = 100
    security_price = None
    security_amount = 0  # 当前舱内有多少股票

    baseline_cash = 0
    baseline_return = 100
    baseline_security_amount = 0

    transcations = pd.DataFrame(columns=['time', 'action', 'amount'])

    # 剩余资金 + 舱内股票当时价值 / 初始资金
    @staticmethod
    def update_current_return():
        account.current_return = (account.cash +
                                  account.security_amount * account.security_price) \
                                 / account.init_fund * 100 - 100
        account.current_return = round(account.current_return, 2)
        pass

    @staticmethod
    def update_baseline_return():
        account.baseline_return = (account.baseline_cash +
                                   account.baseline_security_amount * account.security_price) \
                                  / account.init_fund * 100 - 100
        account.baseline_return = round(account.baseline_return, 2)
        pass

    # 如果这一天有买入或者卖出需要标记出来 用于画图输出用
    @staticmethod
    def order(vol):
        # print(account.current_date, account.current_time)
        if vol > 0 and account.cash >= vol * account.security_price:  # buy
            account.cash -= vol * account.security_price
            account.security_amount += vol
            account.transcations = account.transcations.append(
                pd.Series({
                    'time': account.current_time,
                    'action': 'buy',
                    'price': account.security_price,
                    'amount': vol
                }, name=account.current_date))
        elif vol < 0 and account.security_amount <= np.abs(vol):  # sell
            account.cash += np.abs(vol) * account.security_price
            account.security_amount -= np.abs(vol)
            account.transcations = account.transcations.append(
                pd.Series({
                    'time': account.current_time,
                    'action': 'sell',
                    'price': account.security_price,
                    'amount': vol
                }, name=account.current_date))
        account.update_current_return()
        pass

    @staticmethod
    def init(init_price):
        account.init_fund = account.cash
        vol = int(account.cash / init_price)
        account.baseline_cash = account.cash % init_price
        account.baseline_security_amount = vol
        pass


def back_test(secId, daily_data, window_size, minute_data, handle_data):
    global account
    view_size = 70
    baseline = list(np.ones(window_size + 1) * 0)
    strategy = list(np.ones(window_size + 1) * 0)
    plt.ion()
    account.init(daily_data['open'][window_size])
    account.history_data = daily_data
    for i in range(0, len(daily_data) - view_size - window_size):
        data_slice = daily_data[i:i + view_size + 1]
        pos = window_size
        account.current_date = data_slice.ix[pos].name

        # 调用策略
        m_data = minute_data.loc[account.current_date][:240]
        for m in range(len(m_data)):
            account.current_time = m_data.iloc[m]['time']
            account.current_time = "{:02d}:{:02d}".format(int(account.current_time.seconds / 3600),
                                                          (account.current_time.seconds % 3600) // 60)
            account.security_price = m_data.iloc[m]['close']
            handle_data(account, m_data)

        # 输出K线图 并且计算收益率
        ax1, ax2, ax3 = plot_kchart(secId, data_slice)

        # 绘制分割线
        price_columns = ['ma5', 'ma10', 'ma30', 'ma60', 'high', 'low', 'open', 'close']
        min_price = np.min(data_slice[price_columns].dropna().values) * 0.9
        max_price = np.max(data_slice[price_columns].dropna().values) * 1.1
        if window_size - i >= 0:
            ax1.plot([window_size - i, window_size - i],
                     [min_price, max_price],
                     color='black', alpha=0.5)
        ax1.plot([pos + 1, pos + 1],
                 [min_price, max_price],
                 color='red', alpha=0.5)
        ax1.set_ylim(min_price, max_price)

        # 计算基线收益率
        account.update_baseline_return()
        baseline.append(account.baseline_return)

        ax3.plot(range(i, len(baseline)), baseline[i:], color='black', marker='.')
        ax3.set_xlim(i - 1, i + view_size + 1)
        ax3.annotate('Baseline: {}%'.format(account.baseline_return), xy=(0.02, 0.95),
                     xycoords="axes fraction",
                     va='top', ha='left', weight='extra bold',
                     color='black', fontsize=10)

        # 计算策略收益率
        account.update_current_return()
        strategy.append(account.current_return)
        ax3.plot(range(i, len(strategy)), strategy[i:], color='blue', marker='.')
        ax3.annotate('Strategy: {}%'.format(account.current_return), xy=(0.02, 0.85),
                     xycoords="axes fraction",
                     va='top', ha='left', weight='extra bold',
                     color='blue', fontsize=10)

        min_return = np.min(strategy + baseline) * 0.95
        max_return = np.max(strategy + baseline) * 1.05
        ax3.set_ylim(min_return, max_return)
        return_pos = i + view_size - (view_size - window_size) + 1
        ax3.plot([return_pos, return_pos],
                 [min_return, max_return],
                 color='red', alpha=0.5)
        ax3.plot([i - 1, i + view_size + 1], [0, 0], color='black', linewidth=1.5, alpha=0.8)
        ax3.annotate('Durtion: {}d'.format(i + 1), xy=(0.99, 0.95),
                     xycoords="axes fraction",
                     va='top', ha='right', weight='bold',
                     color='red', fontsize=10)
        ax1.annotate('Date: {}'.format(account.current_date), xy=(0.99, 0.95),
                     xycoords="axes fraction",
                     va='top', ha='right', weight='bold',
                     color='red', fontsize=10)

        # 标记买卖点
        for b_i in range(len(account.transcations)):
            d = account.transcations.ix[b_i].name
            price = account.transcations['price'][b_i]
            action = account.transcations['action'][b_i]
            pos = daily_data.index.get_loc(d)
            pos = pos - i
            print(pos)
            if pos > 0:
                if action=='buy':
                    ax1.annotate('b',
                                 xy=(pos, price), xycoords='data',
                                 xytext=(-1, -20), textcoords='offset points',
                                 arrowprops=dict(arrowstyle="->", color='red'),
                                 color="red")
                else:
                    ax1.annotate('s',
                                 xy=(pos, price), xycoords='data',
                                 xytext=(-1, +20), textcoords='offset points',
                                 arrowprops=dict(arrowstyle="->", color='blue'),
                                 color="blue")
            # print(account.transcations.ix[i].name)
            pass

        print('-----')

        plt.pause(0.2)
    plt.ioff()
    plt.show()
    pass
