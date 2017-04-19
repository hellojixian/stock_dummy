'''
每个引擎负责一只股票的历史回测
所以如果需要测试多个股票，可以同时创建多个引擎实例
然后按照同步的外部时钟进行 tick触发，每个引擎输出一副图表
外部时钟按自然日来循环，这一天有数据就触发 没有就跳过
'''

from DataProviders.DailyData import *
from DataProviders.MinutesData import *
from datetime import datetime, timedelta


class Engine:
    def __init__(self, account=None, sec_id="", start_date="", end_date="", data_callback=None):
        self._sec_id = sec_id
        self._account = account
        self._start_date = start_date
        self._end_date = end_date
        self._data_callback = data_callback
        self._daily_data = None
        self._minutes_data = None
        self._daily_prepend_window = 60
        self._visualizers = {
            'kchart': None,
            'realtime': None,
            'environment_analysis': None,
            'realtime_analysis': None,
            'pattern_graph': None,
            'pattern_state': None,
            'return': None,
        }
        pass

    def get_security_id(self):
        return self._sec_id

    def get_security_price(self):
        # 从account里面获取时间 获取当时收盘价
        current_date = self._account.current_date
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        current_minute = self._account.current_minute
        h = current_minute[0:2]
        m = current_minute[3:5]
        seconds = int(h) * 3600 + int(m) * 60
        min_pos = self._minutes_data.loc[current_date]['time'].tolist().index(timedelta(seconds=seconds))
        rec = self._minutes_data.loc[current_date].iloc[min_pos]
        return rec['close']

    def has_data(self):
        current_date = self._account.current_date
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        return current_date in self._minutes_data.index.values

    def get_security_init_price(self):
        # 从account里面获取时间 获取当时收盘价
        # get open_price for the first day
        return self._daily_data.iloc[self._daily_prepend_window]['open']

    # 初始化数据，
    def _prepare_data(self):
        self._daily_data = None
        self._minutes_data = None
        data = fetch_daily_data(self._sec_id,
                                self._start_date,
                                self._end_date)
        prepend_data = fetch_daily_history_data(self._sec_id,
                                                self._start_date,
                                                range=self._daily_prepend_window)
        self._daily_data = extract_daily_features(prepend_data.append(data))
        self._minutes_data = fetch_minutes_data(self._sec_id,
                                                self._start_date,
                                                self._end_date)
        pass

    # 初始化数据可视化视图，布局
    def _init_visualizer(self):
        pass

    # 更新各自需要被更新的可视化视图
    def _update_visualizer(self):
        pass

    # 每天交易完成后更新各种状态
    # 例如利润结算，并且决定是否要触发学习
    def daily_update(self):
        # update UI output
        self._update_visualizer()

        pass

    def init(self):
        # preparation
        self._prepare_data()
        self._init_visualizer()
        pass

    def tick(self):
        print('--', self._sec_id, self._account.current_date, self._account.current_minute)
        # check
        if callable(self._data_callback) is False:
            return

        if self._account is None:
            return

        # setup account security price
        data = {
            'sec_id': self._sec_id,
            'current_price': 0
        }
        # trigger callback
        self._data_callback(self._account, data)

        pass
