import math

def get_static_env(date, engine):
    daily_data = engine.get_daily_data()
    index_data = engine.get_index_daily_data()
    env_data = {}
    data = {}

    current_date = date
    prev_date = engine.get_prev_date(offset=1)
    prev2_date = engine.get_prev_date(offset=2)
    prev3_date = engine.get_prev_date(offset=3)
    prev4_date = engine.get_prev_date(offset=4)

    # 处理个股数据
    data['current'] = {
        'index': index_data.loc[current_date],
        'stock': daily_data.loc[current_date]
    }
    data['prev'] = {
        'index': index_data.loc[prev_date],
        'stock': daily_data.loc[prev_date]
    }
    data['prev2'] = {
        'index': index_data.loc[prev2_date],
        'stock': daily_data.loc[prev2_date]
    }
    data['prev3'] = {
        'index': index_data.loc[prev3_date],
        'stock': daily_data.loc[prev3_date]
    }
    data['prev4'] = {
        'index': index_data.loc[prev4_date],
        'stock': daily_data.loc[prev4_date]
    }

    env_data['current'] = {
        'date': current_date.strftime('%Y-%m-%d'),
        'index': _get_current_data(data, 'index'),
        'stock': _get_current_data(data, 'stock'),
    }
    env_data['prev'] = {
        'date': prev_date.strftime('%Y-%m-%d'),
        'index': _get_prev_data(data, 'index'),
        'stock': _get_prev_data(data, 'stock'),
    }
    env_data['prev2'] = {
        'date': prev_date.strftime('%Y-%m-%d'),
        'index': _get_prev2_data(data, 'index'),
        'stock': _get_prev2_data(data, 'stock'),
    }
    env_data['prev3'] = {
        'date': prev_date.strftime('%Y-%m-%d'),
        'index': _get_prev3_data(data, 'index'),
        'stock': _get_prev3_data(data, 'stock'),
    }

    # 处理大盘指数
    # import json
    # print(json.dumps(env_data, indent=4))

    return env_data


def _get_current_data(data, key):
    open_rate = (data['current'][key]['open'] - data['prev'][key]['close']) / data['prev'][key]['close'] * 100
    result = {
        'open': open_rate
    }
    return result


def _get_prev_data(data, key):
    prev4_close = data['prev4'][key]['close']
    prev3_close = data['prev3'][key]['close']
    prev2_close = data['prev2'][key]['close']
    prev_open = data['prev'][key]['open']
    prev_close = data['prev'][key]['close']
    prev_high = data['prev'][key]['high']
    prev_low = data['prev'][key]['low']
    prev_vol = data['prev'][key]['vol']
    prev_vol_30 = data['prev'][key]['vol_ma30']
    prev_vol_60 = data['prev'][key]['vol_ma60']

    # 相对前日的变化
    open_rate = (prev_open - prev2_close) / prev2_close * 100
    high_rate = (prev_high - prev2_close) / prev2_close * 100
    low_rate = (prev_low - prev2_close) / prev2_close * 100
    close_rate = (prev_close - prev2_close) / prev2_close * 100

    # 相对前2日的变化
    open_2_rate = (prev_open - prev3_close) / prev3_close * 100
    high_2_rate = (prev_high - prev3_close) / prev3_close * 100
    low_2_rate = (prev_low - prev3_close) / prev3_close * 100
    close_2_rate = (prev_close - prev3_close) / prev3_close * 100

    # 相对前3日的变化
    open_3_rate = (prev_open - prev4_close) / prev4_close * 100
    high_3_rate = (prev_high - prev4_close) / prev4_close * 100
    low_3_rate = (prev_low - prev4_close) / prev4_close * 100
    close_3_rate = (prev_close - prev4_close) / prev4_close * 100

    bar = (prev_close - prev_open) / prev_open * 100

    # 量变化
    vol30_rate = prev_vol / prev_vol_30
    vol60_rate = prev_vol / prev_vol_60

    if close_rate > 0:
        # 红柱
        upline = ((prev_high - prev_close) / prev_open) * 100
        downline = ((prev_open - prev_low) / prev_open) * 100
    else:
        # 绿柱
        upline = ((prev_high - prev_open) / prev_open) * 100
        downline = ((prev_close - prev_low) / prev_open) * 100

    if math.isnan(vol60_rate):
        vol60_rate = vol30_rate

    result = {
        'open': open_rate,
        'high': high_rate,
        'low': low_rate,
        'close': close_rate,

        'open_2': open_2_rate,
        'high_2': high_2_rate,
        'low_2': low_2_rate,
        'close_2': close_2_rate,

        'open_3': open_3_rate,
        'high_3': high_3_rate,
        'low_3': low_3_rate,
        'close_3': close_3_rate,

        'bar': bar,
        'upline': upline,
        'downline': downline,

        'vol30': vol30_rate,
        'vol60': vol60_rate
    }
    return result


def _get_prev2_data(data, key):
    prev3_close = data['prev3'][key]['close']
    prev2_open = data['prev2'][key]['open']
    prev2_close = data['prev2'][key]['close']
    prev2_high = data['prev2'][key]['high']
    prev2_low = data['prev2'][key]['low']
    prev2_vol = data['prev2'][key]['vol']
    prev2_vol_30 = data['prev2'][key]['vol_ma30']
    prev2_vol_60 = data['prev2'][key]['vol_ma60']

    # 相对前日的变化
    open_rate = (prev2_open - prev3_close) / prev3_close * 100
    high_rate = (prev2_high - prev3_close) / prev3_close * 100
    low_rate = (prev2_low - prev3_close) / prev3_close * 100
    close_rate = (prev2_close - prev3_close) / prev3_close * 100

    bar = (prev2_close - prev2_open) / prev2_open * 100

    # 量变化
    vol30_rate = prev2_vol / prev2_vol_30
    vol60_rate = prev2_vol / prev2_vol_60

    if close_rate > 0:
        # 红柱
        upline = ((prev2_high - prev2_close) / prev2_open) * 100
        downline = ((prev2_open - prev2_low) / prev2_open) * 100
    else:
        # 绿柱
        upline = ((prev2_high - prev2_open) / prev2_open) * 100
        downline = ((prev2_close - prev2_low) / prev2_open) * 100

    if math.isnan(vol60_rate):
        vol60_rate = vol30_rate

    result = {
        'open': open_rate,
        'high': high_rate,
        'low': low_rate,
        'close': close_rate,

        'bar': bar,
        'upline': upline,
        'downline': downline,

        'vol30': vol30_rate,
        'vol60': vol60_rate
    }
    return result


def _get_prev3_data(data, key):
    prev4_close = data['prev4'][key]['close']
    prev3_open = data['prev3'][key]['open']
    prev3_close = data['prev3'][key]['close']
    prev3_vol = data['prev3'][key]['vol']
    prev3_vol_30 = data['prev3'][key]['vol_ma30']
    prev3_vol_60 = data['prev3'][key]['vol_ma60']

    vol30_rate = prev3_vol / prev3_vol_30
    vol60_rate = prev3_vol / prev3_vol_60

    close_rate = (prev3_close - prev4_close) / prev4_close * 100
    bar = (prev3_close - prev3_open) / prev3_open * 100

    if math.isnan(vol60_rate):
        vol60_rate = vol30_rate

    result = {
        'change': close_rate,
        'bar': bar,
        'vol30': vol30_rate,
        'vol60': vol60_rate
    }
    return result
