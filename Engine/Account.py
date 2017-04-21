'''
Account 主要管理可共享的资金账户信息和最近交易信息
独立出一个对象为了实现多个线程同时回测
'''


class Account:
    def __init__(self, init_cash=10000, baseline_sec=[]):
        self._init_cash = init_cash
        self._cash = init_cash
        self._vol = {}
        self._baseline_vol = {}
        self._security_latest_price = {}
        self._baseline_cash = init_cash
        self._baseline_init_cash = init_cash
        self._baseline_return = 0
        self._strategies_return = 0
        pass

    def daily_update(self):
        """
        更新基线收益率
        """
        pass

    def baseline_init(self, quotes):
        """
        更新基线收益率 将全部资金分仓买入个股票
        """
        max_available_fund = self._baseline_cash / len(quotes)
        for quote, price in quotes.items():
            vol = int(max_available_fund / (price * 100))
            cost = vol * price * 100
            self._security_latest_price[quote] = price
            self._baseline_vol[quote] = vol
            self._baseline_cash -= cost
        return

    def baseline_update(self, quotes):
        """
        动态计算基线的回报率
        """
        if len(quotes) == 0:
            return
        value = 0
        value += self._baseline_cash
        for quote, price in self._baseline_vol.items():
            if quote in quotes.keys():
                price = quotes[quote]
                self._security_latest_price[quote] = price
            else:
                price = self._security_latest_price[quote]
            value += self._baseline_vol[quote] * price * 100
        self._baseline_return = ((value - self._baseline_init_cash) / self._baseline_init_cash) * 100
        self._baseline_return = round(self._baseline_return, 2)
        return self._baseline_return

    def baseline_return(self):
        """
        返回基线策略回报率
        """
        return self._baseline_return

    def strategies_update(self, quotes):
        """
        动态计算策略的回报率
        """
        value = 0
        value += self._cash
        for quote, price in self._vol.items():
            if quote in quotes.keys():
                price = quotes[quote]
                self._security_latest_price[quote] = price
            else:
                price = self._security_latest_price[quote]
            value += self._vol[quote] * price * 100
        self._strategies_return = ((value - self._init_cash) / self._init_cash) * 100
        self._strategies_return = round(self._strategies_return, 2)
        return self._strategies_return


    def strategies_return(self):
        """
        返回策略回报率
        """
        return self._strategies_return

    def current_return(self):
        """
        返回策略回报率
        """
        return self.strategies_return()