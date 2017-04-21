'''
每个引擎负责一只股票的历史回测
所以如果需要测试多个股票，可以同时创建多个引擎实例
然后按照同步的外部时钟进行 tick触发，每个引擎输出一副图表
外部时钟按自然日来循环，这一天有数据就触发 没有就跳过
'''

from DataProviders.DailyData import *
from DataProviders.MinutesData import *
from Engine.Visualizers.KChart import *
from Engine.Visualizers.RealtimeChart import *
from Engine.Visualizers.RealtimeAnalysis import *
from Engine.Visualizers.ReturnChart import *
from Engine.Visualizers.PatternState import *
from Engine.Visualizers.PatternGraph import *
from Engine.Visualizers.EnvAnalysis import *
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

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
        self._tick_count = 0
        self._day_count = 0
        self._visualizers = {
            'kchart': None,
            'realtime': None,
            'environment_analysis': None,
            'realtime_analysis': None,
            'pattern_graph': None,
            'pattern_state': None,
            'return': None,
        }
        self._figure = None
        pass

    def get_security_id(self):
        return self._sec_id

    def get_security_price(self):
        # 从account里面获取时间 获取当时收盘价
        current_date = self.get_account().current_date
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        current_time = self.get_account().current_time
        h = current_time[0:2]
        m = current_time[3:5]
        seconds = int(h) * 3600 + int(m) * 60
        min_pos = self._minutes_data.loc[current_date]['time'].tolist().index(timedelta(seconds=seconds))
        rec = self._minutes_data.loc[current_date].iloc[min_pos]
        return rec['close']

    def has_data(self):
        current_date = self.get_account().current_date
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        return current_date in self._minutes_data.index.values

    def get_security_init_price(self):
        # 从account里面获取时间 获取当时收盘价
        # get open_price for the first day
        return self._daily_data.iloc[self._daily_prepend_window]['open']

    def get_account(self):
        return self._account

    def get_tick_count(self):
        return self._tick_count

    def get_day_count(self):
        return self._day_count

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

        self._figure = plt.figure(figsize=(16, 8))
        self._figure.set_tight_layout(True)
        gs = mpl.gridspec.GridSpec(13, 12)

        self._visualizers = {
            'kchart': KChart(self._figure.add_subplot(gs[0:5, 0:6])),
            'realtime': RealtimeChart(self._figure.add_subplot(gs[0:5, 6:12])),
            'environment_analysis': EnvironmentAnalysis(self._figure.add_subplot(gs[5:9, 0:4])),
            'realtime_analysis': RealtimeAnalysis(self._figure.add_subplot(gs[5:9, 4:8])),
            'pattern_graph': PatternGraph(self._figure.add_subplot(gs[5:9, 8:12])),
            'return': ReturnChart(self._figure.add_subplot(gs[9:13, 0:6])),
            'pattern_state': PatternState(self._figure.add_subplot(gs[9:13, 6:12])),
        }

        self._figure.canvas.set_window_title('Back Test - Sec: {} Date: {} {}'
                                             .format(self._sec_id,
                                                     self._start_date,
                                                     self._end_date))
        return

    def _clean_output(self):
        # 清空输出目录
        for cur, _dirs, files in os.walk(config.OUTPUT_DIR):
            for f in files:
                os.remove(os.path.join(cur, f))
        return

    def _save_screenshot(self):
        fig_name = "{}-{}-{}.png".format(self._sec_id, self._day_count, self.get_account().current_date)
        plt.savefig(os.path.join(config.OUTPUT_DIR, fig_name), format='png')
        return

    # 更新各自需要被更新的可视化视图
    def _update_visualizer(self):
        self._visualizers['kchart'].draw(self)
        self._visualizers['realtime'].draw(self)
        self._visualizers['environment_analysis'].draw(self)
        self._visualizers['realtime_analysis'].draw(self)
        self._visualizers['pattern_graph'].draw(self)
        self._visualizers['pattern_state'].draw(self)
        self._visualizers['return'].draw(self)
        pass

    # 每天交易完成后更新各种状态
    # 例如利润结算，并且决定是否要触发学习
    def daily_update(self):
        # update counter
        self._tick_count = 0
        self._day_count += 1

        # update UI output
        self._update_visualizer()
        self._save_screenshot()

        pass

    def init(self):
        # preparation
        self._prepare_data()
        self._init_visualizer()
        self._clean_output()
        pass

    def tick(self):
        # print('--', self._sec_id, self.get_account().current_date, self.get_account().current_time)
        # check
        if callable(self._data_callback) is False:
            return

        if self.get_account() is None:
            return

        # setup account security price
        data = {
            'sec_id': self._sec_id,
            'current_price': 0
        }

        # trigger callback
        self._data_callback(self.get_account(), data)

        self._tick_count += 1
        print('tick_count:',self._tick_count)
        return
