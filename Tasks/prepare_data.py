#!/usr/bin/env python3

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from DataProviders.DailyData import *
from DataProviders.MinutesData import *
from Engine.MainEngine import *

code = 'sh600003'
start_date = '2005-01-01'
end_date = '2008-12-30'

account.cash = 10000

data = fetch_daily_data(code, start_date, end_date)
data = extract_daily_features(data)
minute_data = fetch_minutes_data(code, start_date, end_date)

def handle_data(account, data):
    pass

back_test(code, data, minute_data, handle_data)
