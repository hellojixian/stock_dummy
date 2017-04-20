'''
任务调度器，
每个引擎处理一只股票的回测
调度器可以模拟多个引擎（机器人）同时操盘一个共享资金账户的情况
'''

from datetime import timedelta, datetime
from Engine.MainEngineV2 import Engine
import matplotlib.pyplot as plt


class Dispatcher:
    def __init__(self, account, sec_ids, start_date, end_date, data_callback):
        self._account = account
        self._sec_ids = sec_ids
        self._start_date = start_date
        self._end_date = end_date
        self._data_callback = data_callback

        self._engines = []
        if len(sec_ids) == 0:
            return

        for sec_id in sec_ids:
            engine = Engine(account, sec_id, start_date, end_date)
            engine.init()
            self._engines.append(engine)

        pass

    def back_test(self):
        if len(self._engines) == 0:
            return

        start_date = datetime.strptime(self._start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self._end_date, "%Y-%m-%d").date()
        account = self._account
        plt.ion()

        self._init_account_baseline()

        def date_range(_start_date, _end_date):
            for n in range(int((_end_date - _start_date).days)):
                yield _start_date + timedelta(n)

        # 生成分钟字符串索引 每天240分钟
        # 09:30 + 120min | 13:00 + 120min
        trading_mintues = []
        morning_open = 34200
        afternoon_open = 46800
        for i in range(240):
            if i < 120:
                current_sec = morning_open + (i + 1) * 60
            else:
                current_sec = afternoon_open + (i + 1 - 120) * 60
            current_time = "{:02d}:{:02d}".format(int(current_sec / 3600),
                                                    int((current_sec % 3600) / 60))
            trading_mintues.append(current_time)

        # 按自然日循环
        for current_date in date_range(start_date, end_date):
            current_date = current_date.strftime("%Y-%m-%d")
            # 按交易分钟循环
            for current_time in trading_mintues:
                # 分别触发每只股票的引擎
                security_quotes = {}
                for engine in self._engines:
                    account.current_date = current_date
                    account.current_time = current_time
                    if engine.has_data():
                        security_quotes[engine.get_security_id()] = engine.get_security_price()
                        engine.tick()
                # 触发账户每日自动结算
                account.baseline_update(security_quotes)
                account.daily_update()

            # 触发引擎每日更新
            for engine in self._engines:
                engine.daily_update()
            plt.pause(0.01)

        # back test finished
        plt.ioff()
        plt.show()
        return

    def _init_account_baseline(self):
        # 初始化账户的基线收益计算
        account = self._account
        security_quotes = {}
        for engine in self._engines:
            security_quotes[engine.get_security_id()] = engine.get_security_init_price()
        account.baseline_init(security_quotes)
        return
