#!/usr/bin/env python3

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from Visualizers.CandleChart import plot_kchart
from DataProviders.DailyData import *
from sklearn.model_selection import train_test_split

secId = 'sh600003'
start_date = '2005-01-01'
end_date = '2008-12-30'

data = fetch_daily_data(secId, start_date, end_date)
data = extract_daily_features(data)
data = transform_daily_features(data)
results = generate_resultset(data)
data, results = trim_dataset(data, results, 60)
