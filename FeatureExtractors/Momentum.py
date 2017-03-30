import talib as ta

short_period = 5
long_period = 9


def extract_aroon(data):
    period = long_period
    data['aroon_down'], data['aroon_up'] = ta.AROON(data['high'].values,
                                                    data['low'].values,
                                                    timeperiod=period)
    data['aroon_osc'] = ta.AROONOSC(data['high'].values,
                                    data['low'].values,
                                    timeperiod=period)
    return data


def extract_bop(data):
    data['bop'] = ta.BOP(data['open'].values,
                         data['high'].values,
                         data['low'].values,
                         data['close'].values)
    return data


def extract_cmo(data):
    data['cmo'] = ta.CMO(data['close'].values,
                         timeperiod=short_period)
    return data


def extract_dx(data):
    data['dx'] = ta.DX(data['high'].values,
                       data['low'].values,
                       data['close'].values,
                       timeperiod=short_period)
    return data


def extract_mom(data):
    data['mom'] = ta.MOM(data['close'].values,
                         timeperiod=short_period)
    return data


def extract_roc(data):
    data['roc'] = ta.ROC(data['close'].values,
                         timeperiod=short_period)
    return data


def extract_ppo(data):
    data['ppo'] = ta.PPO(data['close'].values,
                         fastperiod=3, slowperiod=15, matype=0)
    return data


def extract_uos(data):
    data['uos'] = ta.ULTOSC(data['high'].values,
                            data['low'].values,
                            data['close'].values,
                            timeperiod1=3, timeperiod2=5, timeperiod3=11)
    data['uos'] -= 50
    return data


def extract_willr(data):
    data['willr'] = ta.WILLR(data['high'].values,
                             data['low'].values,
                             data['close'].values,
                             timeperiod=long_period)
    data['willr'] += 50
    return data


def extract_cci(data):
    data['cci'] = ta.CCI(data['high'].values,
                         data['low'].values,
                         data['close'].values,
                         timeperiod=short_period)
    return data


def extract_rsi(data):
    data['rsi'] = ta.RSI(data['close'].values,
                         timeperiod=short_period)
    data['rsi'] -= 50
    return data


def extract_kd(data):
    data['fastk'], data['fastd'] = ta.STOCHF(data['high'].values,
                                             data['low'].values,
                                             data['close'].values,
                                             fastk_period=5, fastd_period=3, fastd_matype=0)
    return data
