import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import os
from Visualizers.CandleChart import plot_kchart, plot_realtime_chart
from Common import config


class account:
    cash = 0
    init_fund = 0
    history_data = None
    previous_date = None
    current_date = None
    current_time = None
    current_return = 100
    security_price = None
    security_amount = 0  # 当前舱内有多少股票

    baseline_cash = 0
    baseline_return = 100
    baseline_security_amount = 0

    today_SPO = False

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
        # 一天只允许交易一次
        if len(account.transcations) > 0:
            last_trans_date = account.transcations.ix[-1].name
            if last_trans_date == account.current_date and account.today_SPO == False:
                # if account.transcations.iloc[-1]['action'] == 'buy':
                return

        # print(account.current_date, account.current_time)
        if vol > 0 and account.cash >= vol * account.security_price:  # buy
            account.cash -= vol * account.security_price
            account.security_amount += vol
            account.transcations = account.transcations.append(
                pd.Series({
                    'time': account.current_time,
                    'action': 'buy',
                    'price': account.security_price,
                    'amount': vol,
                    'return': 0,
                }, name=account.current_date))
        elif vol < 0 and account.security_amount <= np.abs(vol):  # sell
            account.cash += np.abs(vol) * account.security_price
            print('cash: {}'.format(round(account.cash)))
            account.security_amount -= np.abs(vol)
            session_return = 0
            if account.transcations.iloc[-1]['action'] == 'buy':
                bought_price = account.transcations.iloc[-1]['price']
                session_return = (account.security_price - bought_price) / bought_price * 100
            account.transcations = account.transcations.append(
                pd.Series({
                    'time': account.current_time,
                    'action': 'sell',
                    'price': account.security_price,
                    'amount': vol,
                    'return': session_return
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
    back_test_finished = False
    tail_mode = False
    tail_len = 0
    view_size = 70
    baseline = list(np.ones(window_size + 1) * 0)
    strategy = list(np.ones(window_size + 1) * 0)
    plt.ion()
    account.init(daily_data['open'][window_size])
    account.history_data = daily_data

    # 清空输出目录
    for cur, _dirs, files in os.walk(config.OUTPUT_DIR):
        for f in files:
            os.remove(os.path.join(cur, f))

    for i in range(0, len(daily_data)):
        if i + view_size <= len(daily_data):
            data_slice = daily_data[i:i + view_size + 1]
            # print(tail_mode, len(data_slice), len(daily_data))
            pos = window_size
        else:
            tail_mode = True
            tail_len = np.abs(len(daily_data) - view_size + 1 - i)
            start_pos = len(daily_data) - view_size + tail_len + 1
            data_slice = daily_data[start_pos:]
            pos = window_size
            # print(tail_mode, i, pos, start_pos, len(data_slice), tail_len)

            if tail_len == (view_size - window_size - 2):
                back_test_finished = True

        account.current_date = data_slice.ix[pos].name
        account.previous_date = data_slice.ix[pos - 1].name

        # 输出K线图 并且计算收益率
        ax1, ax2, ax3, today_realtime_ax, last_action_ax = plot_kchart(secId, data_slice)

        # 设置标题
        ax1.set_title('{} to {}'.format(daily_data.ix[window_size].name,
                                        daily_data.ix[-1].name))

        # 绘制分割线
        price_columns = ['ma5', 'ma10', 'ma30', 'ma60', 'high', 'low', 'open', 'close']
        min_price = np.min(data_slice[price_columns].dropna().values) * 0.9
        max_price = np.max(data_slice[price_columns].dropna().values) * 1.1
        if window_size - i >= 0:
            ax1.plot([window_size - i, window_size - i],
                     [min_price, max_price],
                     color='black', alpha=0.5)

        if tail_mode:
            ax1.set_xlim(-1, len(data_slice) + tail_len)
            ax2.set_xlim(-1, len(data_slice) + tail_len)
        ax1.plot([pos, pos],
                 [min_price, max_price],
                 color='red', alpha=0.5)

        # 当天的分钟数据
        m_data = minute_data.loc[account.current_date][:240]

        # 处理如果股票增发 价格跳水的计算逻辑
        # SPO - Secondary Public Offering
        open_price = m_data.iloc[0]['open']
        prev_close = daily_data.loc[account.previous_date]['close']
        current_price = account.security_price
        if (open_price - prev_close) / prev_close < -0.12:
            # 处理基线收益算法，按昨天收盘价卖出，今天开盘价继续买入
            # baseline - sell all
            account.baseline_cash += account.baseline_security_amount * prev_close
            account.baseline_security_amount = 0
            # baseline - buy all
            account.baseline_security_amount = int(account.baseline_cash / open_price)
            account.baseline_cash = account.baseline_cash % open_price

            # sell all
            if account.security_amount > 0:
                print('-- SPO - Reset account --')
                prev_date = account.previous_date
                current_date = account.current_date
                account.security_price = prev_close
                account.current_date = prev_date
                account.today_SPO = True
                account.order(-account.security_amount)
                # 还原
                account.security_price = current_price
                account.current_date = current_date
                account.today_SPO = False

        # 调用策略
        for m in range(len(m_data)):
            account.current_time = m_data.iloc[m]['time']
            account.current_time = "{:02d}:{:02d}".format(int(account.current_time.seconds / 3600),
                                                          (account.current_time.seconds % 3600) // 60)
            account.security_price = m_data.iloc[m]['close']
            handle_data(account, m_data[:(m + 1)])

        ax1.set_ylim(min_price, max_price)

        # 绘制分时图
        params = {
            "prev_close": prev_close,
            "current_date": account.current_date,
            "title": "Date: {}".format(account.current_date)
        }
        plot_realtime_chart(today_realtime_ax, m_data, params)
        plot_realtime_chart(last_action_ax, m_data, params)

        # 计算基线收益率
        account.update_baseline_return()
        baseline.append(account.baseline_return)

        ax3.plot(range(i - 1, len(baseline) - 1), baseline[i:], color='black', marker='.')
        ax3.set_xlim(i - 1, i + view_size + 1)
        ax3.annotate('Baseline: {}%'.format(account.baseline_return), xy=(0.02, 0.95),
                     xycoords="axes fraction",
                     va='top', ha='left', weight='extra bold',
                     color='black', fontsize=10)

        # 计算策略收益率
        account.update_current_return()
        strategy.append(account.current_return)
        min_return = np.min(list(strategy[-60:]) + list(baseline[-60:]))
        max_return = np.max(list(strategy[-60:]) + list(baseline[-60:]))
        if min_return > 0:
            min_return *= 0.9
        else:
            min_return *= 1.1
        if max_return > 0:
            max_return *= 1.1
        else:
            max_return *= 0.9

        ax3.set_ylim(min_return, max_return)

        ax3.plot(range(i - 1, len(strategy) - 1), strategy[i:], color='blue', marker='.')
        ax3.annotate('Strategy: {}%'.format(account.current_return), xy=(0.02, 0.85),
                     xycoords="axes fraction",
                     va='top', ha='left', weight='extra bold',
                     color='blue', fontsize=10)

        return_pos = i + view_size - (view_size - window_size)
        ax3.plot([return_pos, return_pos],
                 [min_return, max_return],
                 color='red', alpha=0.5)
        # 收益率零轴
        ax3.plot([i - 1, i + view_size], [0, 0], color='black', linewidth=1.5, alpha=0.8)
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
            price = account.transcations['price'].iloc[b_i]
            action = account.transcations['action'].iloc[b_i]
            pos = daily_data.index.get_loc(d)
            pos = pos - i
            if pos >= 0:

                if action == 'buy':
                    ax1.annotate('b',
                                 xy=(pos, price), xycoords='data',
                                 xytext=(-1, -30), textcoords='offset points',
                                 arrowprops=dict(arrowstyle="->", color='black'),
                                 color="darkred", weight='bold')
                else:
                    ax1.annotate('s',
                                 xy=(pos, price), xycoords='data',
                                 xytext=(-1, +20), textcoords='offset points',
                                 arrowprops=dict(arrowstyle="->", color='black'),
                                 color="blue", weight='bold')
                    return_rate = round(account.transcations.iloc[b_i]['return'], 2)
                    if return_rate >= 0:
                        ax1.annotate('+ {}%'.format(return_rate),
                                     xy=(pos, price), xycoords='data', rotation=0,
                                     xytext=(-1, +40), textcoords='offset points', fontsize=8,
                                     arrowprops=dict(arrowstyle="->", color='black'),
                                     color="red", weight='bold')
                    else:
                        ax1.annotate('- {}%'.format(np.abs(return_rate)),
                                     xy=(pos, price), xycoords='data', rotation=0,
                                     xytext=(-1, +40), textcoords='offset points', fontsize=8,
                                     arrowprops=dict(arrowstyle="->", color='black'),
                                     color="green", weight='bold')
            pass

        # 标记当日买卖点
        if len(account.transcations):
            last_trans_date = account.transcations.ix[-1].name
            pos = daily_data.index.get_loc(last_trans_date) - 1
            last_prev_close = daily_data.iloc[pos]['close']
            last_action = account.transcations.loc[last_trans_date]['action']
            if last_trans_date == account.current_date:
                last_action_time = account.transcations.loc[last_trans_date]['time']
                last_action_price = account.transcations.loc[last_trans_date]['price']
                last_action_timedelta = np.timedelta64(
                    (int(last_action_time[0:2]) * 3600 + int(last_action_time[3:]) * 60) * 1000 * 1000 * 1000, 'ns')
                last_action_pos = list(m_data['time'].values).index(last_action_timedelta)
                last_action_change = (last_action_price - last_prev_close) / last_prev_close * 100

                if int(last_action_time[0:2]) < 12:
                    last_action_time += ' AM'
                else:
                    last_action_time += ' PM'

                if last_action == 'buy':
                    color = 'darkred'
                    last_action_name = 'B'
                    action_offset = 20
                    action_va = 'bottom'
                else:
                    color = 'blue'
                    last_action_name = 'S'
                    action_offset = -30
                    action_va = 'top'

                today_realtime_ax.scatter(last_action_pos, last_action_price,
                                          color='red', marker='o', alpha=0.6)
                today_realtime_ax.annotate(
                    '{}: {:.2f} ({:.2f}%)\n'
                    'T: {}'.format(last_action_name, last_action_price,
                                   last_action_change, last_action_time),
                    xy=(last_action_pos, last_action_price),
                    xycoords="data",
                    xytext=(10, action_offset),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", color='black'),
                    va=action_va, ha='center', weight='bold',
                    color=color, fontsize=8)

                today_realtime_ax.plot([last_action_pos, last_action_pos],
                                       [last_prev_close * 0.89, last_prev_close * 1.11],
                                       color='red', alpha=0.6)

            last_action = account.transcations.iloc[-1]['action']
            last_action_price = account.transcations.iloc[-1]['price']
            if account.previous_date in account.transcations.index:
                prev_action = account.transcations.loc[account.previous_date]['action']
                if prev_action == 'buy':
                    last_action = 'buy'
                    last_action_price = account.transcations.loc[account.previous_date]['price']
            if last_action == 'buy':
                # 标记买入价格
                today_realtime_ax.plot([0, 240], [last_action_price, last_action_price],
                                       color='red', alpha=0.8, linestyle='--', linewidth=1)

            bought_price = 0

            for i_ in range(0, len(account.transcations)):
                pos_ = np.abs(i_ - len(account.transcations)) - 1
                if account.transcations.iloc[pos_]['action'] == 'buy' and bought_price == 0:
                    bought_price = account.transcations.iloc[pos_]['price']

            # 如果今天没有卖出，那么就用收盘价来比较
            # 如果今天做了卖出操作那么就用卖出价来比较
            if account.transcations.iloc[-1]['action'] == 'sell' \
                    and account.current_date == account.transcations.ix[-1].name:
                the_price = account.transcations.iloc[-1]['price']
            else:
                the_price = m_data.iloc[-1]['close']

            if the_price > bought_price:
                color = 'red'
                start_ = bought_price
                height = the_price - bought_price
            else:
                color = 'green'
                start_ = the_price
                height = bought_price - the_price

            if bought_price > 0 and account.transcations.iloc[-1]['action'] != 'sell' \
                    or (account.transcations.iloc[-1]['action'] == 'sell'
                        and account.current_date == account.transcations.ix[-1].name):
                today_realtime_ax.add_patch(patches.Rectangle((0, start_), width=240, height=height,
                                                              color=color, alpha=0.15))
                pass

            today_realtime_ax.plot([0, 240], [bought_price, bought_price],
                                   color='red', alpha=0.6, linestyle='--', linewidth=0.5)

            # 如果今日卖出，标记本次交易是否获利
            if account.transcations.iloc[-1]['action'] == 'sell' \
                    and account.current_date == account.transcations.ix[-1].name:
                sell_price = account.transcations.iloc[-1]['price']
                session_return = account.transcations.iloc[-1]['return']
                session_return_sign = ""
                if account.transcations.iloc[-1]['return'] > 0:
                    color = 'red'
                    return_offset = 20
                    return_va = 'bottom'
                    session_return_sign = "+"
                else:
                    color = 'green'
                    return_offset = -20
                    return_va = 'top'
                today_realtime_ax.plot([0, 240], [sell_price, sell_price], color=color, linewidth=0.5)
                today_realtime_ax.annotate('Return: {}{:.2f}%'.format(session_return_sign,session_return),
                            xy=(120, sell_price),
                            xycoords="data",
                            xytext=(0, return_offset),
                            textcoords='offset points',
                            arrowprops=dict(arrowstyle="->", color=color),
                            va=return_va, ha='center', weight='bold',
                            color=color, fontsize=9)

        fig_name = "{}-{}-{}.png".format(secId, str(i), str(account.current_date))
        plt.savefig(os.path.join(config.OUTPUT_DIR, fig_name), format='png')

        if back_test_finished:
            ax3.set_title('-- BACK TEST FINISHED --', color="red", weight='bold')
            plt.ioff()
            plt.show()
            break
        plt.pause(0.01)


plt.ioff()
plt.show()
pass
