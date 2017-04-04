import numpy as np

strategy_info = {}

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

# 连续2坏 休息2次
# 两次时间点判断追涨
def should_buy(account, data):
    # 如果这个连续上涨已经买过了 就忽略
    # if prev is red bar and prev_2 is also red bar then ignore it
    prev = account.history_data.loc[account.previous_date]
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev_2 = account.history_data.iloc[prev_pos-1]
    if is_red_bar(prev['close'], prev['open'], 0.002) \
        and is_red_bar(prev_2['close'], prev_2['open'], 0.002):
        return False
    # 一个红柱也不追
    if is_red_bar(prev['close'], prev['open'], 0.002) :
        return False

    # 如果昨天收红但是没买到，那么开盘就买
    # if account.current_time == "09:31" \
    #         and is_red_bar(prev['close'], prev['open']):
    #     return True

    # 当天大跳水不买入 不管高低
    open_price = data.iloc[0]['open']
    if np.abs((open_price - prev['close'])/prev['close']) > 0.005:
        return False

    # 如果下午开盘的时候已经是红柱就买入
    if account.current_time == "13:05" \
            and is_red_bar(account.security_price, data.iloc[0]['open'], ratio=0.01):
        # 如果没有上影线 长度小于0.1 可以买入

        return True

    # 如果下午收盘前也变成了红柱 就买入
    if account.current_time == "14:45" \
            and is_red_bar(account.security_price, data.iloc[0]['open'], ratio=0.01):
        return True
    return False


# 两次时间点判断杀跌
# 如果跌破买入价就立即卖出
# 如果第二天高开，开盘就买
def should_sell(account, data):
    # 如果本身是空仓就忽略
    if account.security_amount == 0: return False

    # 如果今天刚买的就忽略
    last_action = account.transcations.iloc[-1]['action']
    last_trans_date = account.transcations.ix[-1].name
    if last_trans_date == account.current_date and last_action == 'buy': return False

    # 如果第二天高开，开盘就买
    prev = account.history_data.loc[account.previous_date]
    prev_close = prev['close']
    open_price = data.iloc[0]['open']
    if account.current_time == "09:31" and (open_price - prev_close) / prev_close > 0:
        return True

    # 跌破买入价就卖出 & 强制停损
    bought_price = account.transcations.iloc[-1]['price']
    if account.current_time == "13:35" \
            and (account.security_price - bought_price) / bought_price < -0.04 \
            and is_going_down(account.security_price, data, 60):
        return True

    if account.current_time == "14:45":
        if not is_red_bar(account.security_price, open_price, ratio=0.001):
            return True
    return False


def is_going_down(current_price, data, lookback):
    prev_price = data.iloc[-lookback]['close']
    if (current_price - prev_price) / prev_price > 0.005:
        return False
    return True


def is_red_bar(current, open, ratio=0.005):
    if (current - open) / open > ratio:
        return True
    return False
