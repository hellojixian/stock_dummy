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
        self.current_date = None
        self.current_time = None
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
        for sec_id, price in quotes.items():
            vol = int(max_available_fund / (price * 100))
            cost = vol * price * 100
            self._security_latest_price[sec_id] = price
            self._baseline_vol[sec_id] = vol
            self._baseline_cash -= cost
        return

    def baseline_update(self, quotes, engines):
        """
        动态计算基线的回报率
        """
        if len(quotes) == 0:
            return
        value = 0
        value += self._baseline_cash
        for sec_id, price in self._baseline_vol.items():
            if sec_id in quotes.keys():
                price = quotes[sec_id]
                self._security_latest_price[sec_id] = price
            else:
                price = self._security_latest_price[sec_id]
            engine = engines[sec_id]
            if engine.has_data():
                prev_close = engine.get_prev_close()
                open_price = engine.get_open_price()
                if (open_price - prev_close) / prev_close < -0.12:
                    # 处理SPO的特殊情况逻辑
                    money = float(self._baseline_vol[sec_id] * prev_close * 100)
                    new_vol = int(money / (open_price * 100))
                    new_cost = float(new_vol * open_price * 100)
                    self._baseline_vol[sec_id] = new_vol
                    self._baseline_cash += float(money - new_cost)
                    value += float(money - new_cost)
            value += self._baseline_vol[sec_id] * price * 100
        self._baseline_return = ((value - self._baseline_init_cash) / self._baseline_init_cash) * 100
        self._baseline_return = round(self._baseline_return, 2)
        return self._baseline_return

    def baseline_return(self):
        """
        返回基线策略回报率
        """
        return self._baseline_return

    def strategies_update(self, quotes, engines):
        """
        动态计算策略的回报率
        """
        value = 0
        value += self._cash
        for sec_id, price in self._vol.items():
            if sec_id in quotes.keys():
                price = quotes[sec_id]
                self._security_latest_price[sec_id] = price
            else:
                price = self._security_latest_price[sec_id]
            value += self._vol[sec_id] * price * 100
        self._strategies_return = ((value - self._init_cash) / self._init_cash) * 100
        self._strategies_return = round(self._strategies_return, 2)
        return self._strategies_return

    def get_security_price(self, sec_id):
        return self._security_latest_price[sec_id]

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
