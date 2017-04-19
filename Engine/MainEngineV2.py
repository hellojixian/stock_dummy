'''
每个引擎负责一只股票的历史回测
所以如果需要测试多个股票，可以同时创建多个引擎实例
然后按照同步的外部时钟进行 tick触发，每个引擎输出一副图表
外部时钟按自然日来循环，这一天有数据就触发 没有就跳过
'''

from DataProviders.DailyData import *
from DataProviders.MinutesData import *


class Engine:
    def __init__(self, sec_id="", start_date="", end_date="", data_callback=None):
        self._sec_id = sec_id
        self._start_date = start_date
        self._end_date = end_date
        self._data_callback = data_callback
        self._daily_data = None
        self._minutes_data = None
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

    # 初始化数据，
    def _prepare_data(self):
        pass

    # 初始化数据可视化视图，布局
    def _init_visualizer(self):
        pass

    # 更新各自需要被更新的可视化视图
    def _update_visualizer(self):
        pass

    # 每天交易完成后更新各种状态
    # 例如利润结算，并且决定是否要触发学习
    def _update_state(self):
        pass

    def init(self):
        # preparation
        self._prepare_data()
        self._init_visualizer()

        # main loop
        # 多只股票的情况可以调用两次这个循环，
        # 先循环日期，然后每分钟分别用股票代码的数据来触发策略回调
        # todo: 思考一下 - 也许每个股票分别画一个图输出更适合多显示器输出监视 或者一个引擎只负责一只股票的回测，但是资金池用数据库独立存储用于方便通过多线程来模拟多个引擎
        # loop per day

        # loop per minutes call handle_data function

        # update data
        self._update_state()

        # update UI output
        self._update_visualizer()
        pass

    def tick(self, current_date, current_minute):
        print(self._sec_id, current_date, current_minute)
        # check
        if callable(self._data_callback) is False:
            return

        pass
