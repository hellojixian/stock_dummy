#!/usr/bin/env python3

import os, sys, datetime
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from Visualizers.CandleChart import plot_kchart
from DataProviders.DailyData import fetch_daily_data
from FeatureExtractors.OverlapStudies import *
from FeatureExtractors.Momentum import *
from FeatureExtractors.Statistic import *
from FeatureExtractors.Pattern import *

secId = 'sh600001'
start_date = '2007-01-01'
end_date = '2008-12-30'

data = fetch_daily_data(secId, start_date, end_date)

# overlap studies
data = extract_ma(data)
data = extract_sar(data)

# # momentum
# data = extract_aroon(data)
# data = extract_bop(data)
# data = extract_cmo(data)
# data = extract_dx(data)
# data = extract_mom(data)
# data = extract_roc(data)
# data = extract_ppo(data)
# data = extract_uos(data)
# data = extract_willr(data)
# data = extract_cci(data)
# data = extract_rsi(data)
# data = extract_kd(data)

# # statistics
# data = extract_beta(data)
# data = extract_linear_reg(data)

# pattern
data = extract_pattern(data)

data['change_100'] = data['change'] * 100

# print(data[['date', 'change_100', 'close', 'linear_reg_angle', 'linear_reg_slope', 'beta',
#             'rsi', 'cci', 'willr', 'uos', 'roc', 'ppo', 'mom', 'bop', 'cmo', 'dx']])

print(data)

window_size = 0
view_size = 80
plt.ion()
for i in range(window_size, len(data) - view_size):
    data_slice = data[i:i + view_size]
    price_ax, vol_ax = plot_kchart(secId, data_slice)
    plt.pause(0.2)
plt.ioff()
plt.show()
