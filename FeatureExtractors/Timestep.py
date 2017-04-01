import pandas as pd

lookback = 5


# 过去 N 天的价格变化
def extract_timestamp_changes(data):
    data['change_p1'] = [None] + list(data['change'][:-1].values)
    data['change_p2'] = [None, None] + list(data['change'][:-2].values)
    data['change_p3'] = [None, None, None] + list(data['change'][:-3].values)
    data['change_p4'] = [None, None, None, None] + list(data['change'][:-4].values)
    return data
