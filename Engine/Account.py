'''
Account 主要管理可共享的资金账户信息和最近交易信息
独立出一个对象为了实现多个线程同时回测
'''


class Account:
    def __init__(self, init_cash=10000, baseline_sec=[]):
        self._init_cash = init_cash
        self._baseline_vol = {}
        self._baseline_cash = init_cash
        self._baseline_init_cash = init_cash
        self._baseline_return = 100
        pass

    def daily_update(self):
        # 更新基线收益率
        pass

    def baseline_init(self, quotes):
        # 更新基线收益率 将全部资金分仓买入个股票
        max_available_fund = self._baseline_cash / len(quotes)
        for quote, price in quotes.items():
            vol = int(max_available_fund / (price * 100))
            cost = vol * price * 100
            self._baseline_vol[quote] = vol
            self._baseline_cash -= cost
        return

    def baseline_update(self, quotes):
        # 动态计算基线的回报率
        value = 0
        value += self._baseline_cash
        for quote, price in self._baseline_vol.items():
            value += self._baseline_vol[quote] * price * 100
        self._baseline_return = (((value - self._baseline_init_cash) / self._baseline_init_cash) - 1) * 100
        return self._baseline_return
