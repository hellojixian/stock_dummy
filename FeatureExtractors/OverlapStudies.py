import talib as ta


def extract_ma(data):
    data['ma5'] = ta.MA(data['close'].values, timeperiod=5, matype=0)
    data['ma10'] = ta.MA(data['close'].values, timeperiod=10, matype=0)
    data['ma30'] = ta.MA(data['close'].values, timeperiod=30, matype=0)
    data['ma60'] = ta.MA(data['close'].values, timeperiod=60, matype=0)
    data['vol_ma30'] = ta.MA(data['vol'].values, timeperiod=30, matype=0)
    data['vol_ma60'] = ta.MA(data['vol'].values, timeperiod=60, matype=0)
    return data
