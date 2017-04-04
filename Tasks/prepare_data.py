#!/usr/bin/env python3

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from DataProviders.DailyData import *
from DataProviders.MinutesData import *
from Engine.MainEngine import *

import numpy as np

code = 'sh600003'
start_date = '2005-01-01'
end_date = '2008-12-30'
prepend_window = 60
account.cash = 10000

data = fetch_daily_data(code, start_date, end_date)
prepend_data = fetch_daily_history_data(code, start_date, range=prepend_window)
data = extract_daily_features(prepend_data.append(data))
minute_data = fetch_minutes_data(code, start_date, end_date)


def handle_data(account, data):
    if account.current_time == '09:35':
        if np.random.uniform() > 0.5:
            account.order(10)
        else:
            account.order(-10)
    pass


back_test(code, data, prepend_window,
          minute_data, handle_data)
