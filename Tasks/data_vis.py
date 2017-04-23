#!/usr/bin/env python3

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from Engine.Account import Account
from Engine.Dispatcher import Dispatcher
from Strategies.LuckyOne import handle_data

# 训练数据组1
# code = 'sh600552'
# code = 'sh600201'
# code = 'sh600486'
# code = 'sh600146'
# code = 'sh600021' # - 这个股票训练了很多高风险 买十字星的策略


# 测试数据组 15 - 20元左右
sec_list = ['sh600552',
            'sh600201']

start_date = '2015-01-10'
end_date = '2015-12-30'

init_cash = 100000


dispatcher = Dispatcher(account=Account(init_cash=init_cash),
                        sec_ids=sec_list,
                        start_date=start_date,
                        end_date=end_date,
                        data_callback=handle_data)
dispatcher.back_test()
