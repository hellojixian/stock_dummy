#!/usr/bin/env python3

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from DataProviders.DailyData import *
from DataProviders.MinutesData import *
from Engine.MainEngine import *
from Strategies.LuckyOne import handle_data

# 训练数据组1
# code = 'sh600552'
# start_date = '2015-04-10'
# end_date = '2016-12-30'

# code = 'sh600486'
# start_date = '2015-01-01'
# end_date = '2016-12-30'
#
# code = 'sh600146'
# start_date = '2015-01-01'
# end_date = '2016-12-30'

# ---------------------------
# start_date = '2016-08-22'
# start_date = '2015-07-01'


# 测试数据组 小价格  10元左右 全是上下影线
# code = 'sh600819'
# start_date = '2015-01-15'
# end_date = '2016-12-30'

# 测试数据组 15 - 20元左右
code = 'sh600201'
start_date = '2015-01-01'
start_date = '2015-10-01'
end_date = '2016-12-30'

prepend_window = 60
account.cash = 100000

data = fetch_daily_data(code, start_date, end_date)
prepend_data = fetch_daily_history_data(code, start_date, range=prepend_window)
data = extract_daily_features(prepend_data.append(data))
minute_data = fetch_minutes_data(code, start_date, end_date)

back_test(code, data, prepend_window,
          minute_data, handle_data)
