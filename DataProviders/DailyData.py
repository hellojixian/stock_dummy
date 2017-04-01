import Common.config as config
import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker
from FeatureExtractors.OverlapStudies import *
from FeatureExtractors.Momentum import *
from FeatureExtractors.Statistic import *
from FeatureExtractors.Pattern import *
from FeatureExtractors.Timestep import *


def fetch_daily_data(code, start_date, end_date):
    session = sessionmaker()
    session.configure(bind=config.DB_CONN)
    db = session()
    sql = """
        SELECT
            `date`,
            `open`,
            `high`,
            `low`,
            `close`,
            `volume`,
            `turnover`,
            `change`
        FROM
            raw_stock_trading_daily
        WHERE
            `code` = '{0}'
                AND `date` > '{1}'
                AND `date` < '{2}' ;
        """.format(code, start_date, end_date)
    rs = db.execute(sql)
    df = pd.DataFrame(rs.fetchall())
    df.columns = ['date', 'open', 'high', 'low', 'close', 'vol', 'turnover', 'change']
    db.close()
    return df


def extract_daily_features(data):
    # time steps
    data = extract_timestamp_changes(data)

    # overlap studies
    data = extract_ma(data)
    data = extract_sar(data)

    # momentum
    data = extract_aroon(data)
    data = extract_bop(data)
    data = extract_cmo(data)
    data = extract_dx(data)
    data = extract_mom(data)
    data = extract_roc(data)
    data = extract_ppo(data)
    data = extract_uos(data)
    data = extract_willr(data)
    data = extract_cci(data)
    data = extract_rsi(data)
    data = extract_kd(data)

    # statistics
    data = extract_beta(data)
    data = extract_linear_reg(data)

    # pattern
    data = extract_pattern(data)
    return data


def transform_daily_features(data):
    # 主要将数据以零轴分割 数据分布缩放于 -1 to +1
    new_data = pd.DataFrame()

    new_data['date'] = data['date']
    new_data['change'] = data['change'] * 10
    new_data['change_p1'] = data['change_p1'] * 10
    new_data['change_p2'] = data['change_p2'] * 10
    new_data['change_p3'] = data['change_p3'] * 10
    new_data['change_p4'] = data['change_p4'] * 10
    new_data['turnover'] = data['turnover'] * 10

    # overlap studies
    new_data['ma5_pos'] = (data['close'] / data['ma5'] - 1) * 10
    new_data['ma10_pos'] = (data['close'] / data['ma10'] - 1) * 10
    new_data['ma30_pos'] = (data['close'] / data['ma30'] - 1) * 10
    new_data['ma60_pos'] = (data['close'] / data['ma60'] - 1) * 10
    new_data['vol_ma30'] = data['vol'] / data['vol_ma30'] - 1
    new_data['vol_ma60'] = data['vol'] / data['vol_ma60'] - 1

    # momentum
    new_data['sar'] = data['close'] - np.abs(data['sar'])
    new_data['arn_dn'] = data['aroon_down'] / 100
    new_data['arn_up'] = data['aroon_up'] / 100
    new_data['arn_os'] = data['aroon_osc'] / 100
    new_data['bop'] = data['bop']
    new_data['cmo'] = data['cmo'] / 100
    new_data['dx'] = data['dx'] / 100
    new_data['mom'] = data['mom']
    new_data['roc'] = data['roc'] / 10
    new_data['ppo'] = data['ppo'] / 10
    new_data['uos'] = data['uos'] / 10
    new_data['willr'] = data['willr'] / 50
    new_data['cci'] = data['cci'] / 100
    new_data['rsi'] = data['rsi'] / 100
    new_data['fastk'] = data['fastk'] / 100
    new_data['fastd'] = data['fastd'] / 100
    new_data['beta'] = data['beta']

    # # statistics
    new_data['lr_a'] = data['linear_reg_angle'] / 10
    new_data['lr_s'] = data['linear_reg_slope']

    # patterns
    i = 0
    for col in data.columns:
        if col[:3] == 'cdl':
            new_data['cdl_' + str(i)] = data[col]
            i += 1
    return new_data


def generate_resultset(data):
    result = []
    for i in range(len(data) - 1):
        next_day_change = data['change'].iloc[i + 1]
        if next_day_change > 0:
            result.append([0, 1])
        else:
            result.append([1, 0])
    result = pd.DataFrame(result)
    result.columns = ['up',  'down']
    return result


def trim_dataset(data, results, window_size=60):
    data = data.drop('date', axis=1)
    data = data[window_size:-1].as_matrix()
    results = results[window_size:].as_matrix()
    return [data, results]
