import talib as ta

short_period = 5
long_period = 9


def extract_trange(data):
    data['trange'] = ta.TRANGE(data['high'].values,
                               data['low'].values,
                               data['close'].values)

    return data
