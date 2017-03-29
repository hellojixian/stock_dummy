#!/usr/bin/env python3

import os, sys, datetime
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from Visualizers.CandleChart import plot_kchart
from DataProviders.DailyData import fetch_daily_data
from FeatureExtractors.OverlapStudies import extract_ma

secId = 'sh600529'
start_date = '2007-01-01'
end_date = '2008-12-30'

data = fetch_daily_data(secId, start_date, end_date)
data = extract_ma(data)

window_size = 0
view_size = 60
plt.ion()
for i in range(window_size, len(data)-view_size):
    data_slice = data[i:i+view_size]
    plot_kchart(secId, data_slice).show()
    plt.pause(0.5)
plt.ioff()
plt.show()
