'''
任务调度器，
每个引擎处理一只股票的回测
调度器可以模拟多个引擎（机器人）同时操盘一个共享资金账户的情况
'''

from datetime import timedelta, datetime
from Engine.MainEngineV2 import Engine


class Dispatcher:
    '''
    任务调度器，
    每个引擎处理一只股票的回测
    调度器可以模拟多个引擎（机器人）同时操盘一个共享资金账户的情况
    '''

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
            engine = Engine(sec_id, start_date, end_date)
            engine.init()
            self._engines.append(engine)

        pass

    def back_test(self):
        if len(self._engines) == 0:
            return

        start_date = datetime.strptime(self._start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self._end_date, "%Y-%m-%d").date()

        def date_range(_start_date, _end_date):
            for n in range(int((_end_date - _start_date).days)):
                yield _start_date + timedelta(n)

        # 生成分钟字符串索引 每天240分钟
        # 09:30 + 120min | 13:00 + 120min
        trading_mintues = []
        morning_open = 32400
        afternoon_open = 46800
        for i in range(240):
            if i < 120:
                current_sec = morning_open + (i + 1) * 60
            else:
                current_sec = afternoon_open + (i + 1 - 120) * 60
            current_minute = "{:02d}:{:02d}".format(int(current_sec / 3600),
                                                    int((current_sec % 3600) / 60))
            trading_mintues.append(current_minute)

        # 按自然日循环
        for current_date in date_range(start_date, end_date):
            current_date = current_date.strftime("%Y-%m-%d")
            # 按交易分钟循环
            for current_minute in trading_mintues:
                # 分别触发每只股票的引擎
                for engine in self._engines:
                    engine.tick(current_date, current_minute)
        return
