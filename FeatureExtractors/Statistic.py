import talib as ta

short_period = 5
long_period = 9


def extract_beta(data):
    data['beta'] = ta.BETA(data['high'].values,
                           data['low'].values,
                           timeperiod=5)
    return data


def extract_linear_reg(data):
    data['linear_reg_angle'] = ta.LINEARREG_ANGLE(data['close'].values,
                                                  timeperiod=short_period)
    data['linear_reg_slope'] = ta.LINEARREG_SLOPE(data['close'].values,
                                                  timeperiod=short_period)
    return data
