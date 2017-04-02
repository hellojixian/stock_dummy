import matplotlib.pyplot as plt
import numpy as np
from Visualizers.CandleChart import plot_kchart


class account:
    cash: 0
    current_date: None
    current_time: None
    current_price: None

    def order(vol):
        pass

def back_test(secId, daily_data, minute_data, handle_data):
    global account
    window_size = 0
    view_size = 80
    baseline = list(np.ones(view_size) * 100)
    plt.ion()
    account.init_fund = account.cash
    for i in range(window_size, len(daily_data) - view_size):
        data_slice = daily_data[i:i + view_size]
        account.current_date = data_slice.ix[-1].name

        # 计算基线收益率
        last_percent = float(baseline[-1])
        last_pchange = float(data_slice.iloc[-1]['change']) + 1
        baseline_return = round(last_percent * last_pchange, 2)
        baseline.append(baseline_return)

        # 调用策略
        m_data = minute_data.loc[account.current_date]
        for m in range(len(m_data)):
            account.current_time = m_data.iloc[m]['time']
            account.current_time = "{:02d}:{:02d}".format(int(account.current_time.seconds / 3600),
                                                          (account.current_time.seconds % 3600) // 60)
            account.current_price = m_data.iloc[m]['close']
            handle_data(account, m_data)

        # 输出K线图 并且计算收益率
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
    pass


