import numpy as np


def handle_data(account, data):
    # pos = account.history_data.index.get_loc(account.previous_date)
    if should_buy(account, data):
        percent = 100
        vol = int(account.cash * percent / 100 / account.security_price)
        account.order(vol)
    if should_sell(account, data):
        account.order(-account.security_amount)
    pass


def search_nearest_lowest(data):
    lowest = data['low'][-1]
    for i in range(len(data)):
        pos = len(data) - i - 2
        if data['low'][pos] < lowest:
            lowest = data['low'][pos]
        else:
            break
    return lowest


# 两次时间点判断追涨
def should_buy(account, data):
    # 如果这个连续上涨已经买过了 就忽略
    # if prev is red bar then ignore it
    prev = account.history_data.loc[account.previous_date]
    if is_red_bar(prev['close'], prev['open'], 0.002):
        return False

    # 如果下午开盘的时候已经是红柱就买入
    if account.current_time == "13:05" \
            and is_red_bar(account.security_price, data.iloc[0]['open']):
        return True

    # 如果下午收盘前也变成了红柱 就买入
    if account.current_time == "14:45" \
            and is_red_bar(account.security_price, data.iloc[0]['open'], ratio=0.001):
        return True
    return False


# 两次时间点判断杀跌
def should_sell(account, data):
    # 如果本身是空仓就忽略
    if account.security_amount == 0: return False

    # 如果今天刚买的就忽略
    last_action = account.transcations.iloc[-1]['action']
    last_trans_date = account.transcations.ix[-1].name
    if last_trans_date == account.current_date and last_action == 'buy': return False

    if account.current_time == "14:45":
        return True
    return False


def is_red_bar(current, open, ratio=0.005):
    if (current - open) / open > ratio:
        return True
    return False
