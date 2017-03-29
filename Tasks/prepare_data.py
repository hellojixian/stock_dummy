#!/usr/bin/env python3

import os, sys, datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from Visualizers.CandleChart import plot_kchart
from DataProviders.DailyData import fetch_daily_data

secId = 'sh600529'
start_date = '2007-01-01'
end_date = '2008-12-30'

data = fetch_daily_data(secId, start_date, end_date)
plot_kchart(secId, data[:90]).show()
print(data)