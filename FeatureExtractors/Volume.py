import talib as ta

short_period = 5
long_period = 9


def extract_obv(data):
    data['obv'] = ta.OBV(data['close'].values,
                         data['vol'].values)

    return data
