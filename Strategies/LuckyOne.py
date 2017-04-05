import numpy as np

strategy_info = {
    'last_ignore_buy_date': None
}


def handle_data(account, data):
    global strategy_info
    if len(account.transcations) \
            and account.current_date == account.transcations.ix[-1].name:
        return

    if strategy_info['last_ignore_buy_date'] != account.current_date:
        if should_ignore_buy_signal(account, data):
            strategy_info['last_ignore_buy_date'] = account.current_date
        elif should_buy(account, data):
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
    open_price = data.iloc[0]['open']
    lowest_price = np.min(data['low'].values)
    highest_price = np.max(data['high'].values)
    current_price = account.security_price

    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]

    # if prev['sar'] < 0: return False


    # 绿柱后平开 开盘即可买入
    if account.current_time == "10:00" \
            and (prev['close'] - prev['open']) / prev['open'] < -0.035 \
            and np.abs((open_price - prev['close']) / prev['close']) < 0.005 \
            and (account.security_price - open_price) / open_price > 0.004:
        print(account.current_date, 'follow green bar')
        return True

    def check_not_too_far_from_highest(current_price, open_price, highest_price):
        if current_price > open_price and highest_price > 0:
            upline = (highest_price - current_price)
            downline = (open_price - lowest_price)
            body = (current_price - open_price)
            if downline == 0:
                if upline > 0:
                    # 如果上引线小于实体柱大于上引线2倍 也可以买入
                    if (body - upline) / upline > 1:
                        return True
                    else:
                        return False
                elif upline == 0:
                    return True
                else:
                    if (upline - downline) / downline < 0.5:
                        return True
        return False

    # todo: 最高点要高过昨天收盘价再买入
    # todo: 如果当前价格高过昨天最高价格就买入

    # 光头光脚阳柱 大约3个点 啥时候都可以买
    # 昨天不能是暴跌 昨天的实体+最高价跌幅不能大于7%
    if is_pure_red_bar(account.security_price, open_price, highest_price, lowest_price, ratio=0.035):
        # print((prev['close'] - prev['high']) / prev['high'])
        # if prev['close'] - prev['high'] == 0:
        #     print(account.current_date, account.current_time, 'buy pure red bar after 0% changes')
        #     return True
        #
        # if (prev['close'] - prev['high']) / prev['high'] > -0.07:
        #     print(account.current_date, account.current_time, 'buy pure red bar')
        return True

    if account.current_time == "14:48" \
            and check_not_too_far_from_highest(account.security_price, open_price, highest_price) \
            and (is_red_bar(account.security_price, open_price, ratio=0.015)
                 or (is_red_bar(account.security_price, open_price, ratio=0.005)
                     and is_red_bar(account.security_price, lowest_price, ratio=0.015))):
        print(account.current_date, account.current_time, 'buy in the end')
        return True

    # 今日涨幅 2% 但是上引线不能超过实体的50%
    if account.current_time in ["13:30", "14:00", "14:30", "14:40", "14:48"]:
        if is_red_bar(account.security_price, open_price, ratio=0.015):
            upline = (highest_price - current_price)
            body = (current_price - open_price)
            if upline / body < 0.5:
                print(account.current_date, account.current_time, 'buy in the afternoon, today > 2%')
                return True

    # 如果是危险区
    if prev['sar'] < 0:
        pass
    # 如果是安全区
    else:
        if account.current_time in ["10:00", "10:30", "11:00"]:
            if is_red_bar(account.security_price, open_price, ratio=0.01) \
                    and check_not_too_far_from_highest(account.security_price, open_price, highest_price):
                print(account.current_date, account.current_time, 'buy in the morning')
                return True
        # 如果下午开盘的时候已经是红柱就买入
        if account.current_time in ["13:01", "13:30", "14:00", "14:30", "14:45"]:
            if is_red_bar(account.security_price, lowest_price, ratio=0.015) \
                    and check_not_too_far_from_highest(account.security_price, open_price, highest_price) \
                    and is_red_bar(account.security_price, open_price, ratio=0.005):
                print(account.current_date, account.current_time, 'buy in the afternoon')
                return True

    return False  # 两次时间点判断杀跌


# 如果跌破买入价就立即卖出
# 如果第二天高开，开盘就买
def should_sell(account, data):
    # 如果本身是空仓就忽略
    if account.security_amount == 0: return False

    bought_price = account.transcations.iloc[-1]['price']
    prev = account.history_data.loc[account.previous_date]
    prev_close = prev['close']
    prev_open = prev['open']
    open_price = data.iloc[0]['open']
    highest_price = np.max(data['high'].values)

    # 如果昨天光头，今天没有低开，那就拿住了
    if is_red_bar(prev['close'], prev['open'], ratio=0.03) \
            and prev['close'] == prev['high'] \
            and (open_price - prev_close) / prev_close > - 0.005:
        return False

    # 如果高开，但是中午跌破昨天涨幅的40% 就赶快卖出
    if account.current_time in ["11:00", "11:25", "13:01", "13:30"] \
            and (open_price - prev_close) / prev_close > - 0.002:
        today_change = (account.security_price - prev_close) / prev_close
        prev_change = (prev_close - prev_open) / prev_open
        if today_change < 0 and (prev_change - (prev_change + today_change)) / prev_change > 0.65:
            print('stop loss today lower than yesterday change 65%')
            return True

    # todo: 暴跌>8%之后 遇到高开 当天尾盘卖出

    # 跌破买入价就卖出 & 强制停损
    if account.current_time in ["10:00", "10:30", "11:00", "11:25", "13:01", "13:30", "14:00", "14:30"] \
            and (account.security_price - bought_price) / bought_price < -0.04 \
            and is_going_down(account.security_price, data, 15):
        print('stop loss today')
        return True

    # 如果昨天的SAR是负数数，使用危险区卖出原则
    # 这些原则都非常谨小慎微
    if prev['sar'] < 0:
        # 如果高开或者平开，比开盘价走低2个点就卖出
        if (open_price - prev_close) / prev_close > - 0.002 \
                and (account.security_price - bought_price) / bought_price < -0.02:
            print('stop loss today 2')
            return True

        # 如果第二天高开低走1个点 立即买出
        if (open_price - prev_close) / prev_close > 0.015 \
                and account.current_time in ["10:00", "10:30"]:
            if (account.security_price - open_price) / open_price < -0.01:
                return True

        # 如果昨天买到的是2个点以上的绿柱，开盘立即卖出
        if (prev['close'] - prev['open']) / prev['open'] < -0.02:
            if (account.security_price - open_price) / open_price > 0.005:
                print(account.current_date, 'stop loss because yesterday')
                return True

        # 上影线原则：当前距离最高点 低于1个点则卖出 当前价格已经高于买入价格
        if account.current_time in ["13:01", "13:30", "14:00", "14:30"]:
            if 0.03 > (account.security_price - bought_price) / bought_price > 0 \
                    and (account.security_price - highest_price) / highest_price < -0.005:
                print(account.current_date, account.current_time, 'cannot hold it')
                return True
            if (account.security_price - bought_price) / bought_price > 0.03 \
                    and (account.security_price - highest_price) / highest_price < -0.025:
                print(account.current_date, account.current_time, 'cannot hold it - droped 3% from today highest price')
                return True

        if account.current_time == "14:45":
            if not is_red_bar(account.security_price, open_price, ratio=0.001):
                print(account.current_date, account.current_time, 'cannot hold it - close price lower than yesterday')
                return True
    # 下面是在安全区的策略
    else:
        # 当日下跌过昨日收盘价 超过3个点卖出
        if (account.security_price - prev_close) / prev_close < -0.035:
            print(account.current_date, account.current_time, 'should sell today dropped 3.5%')
            return True
        # 下午的时候比昨天的收盘价还低 说明已经上涨无力了
        if account.current_time in ["14:30", "14:45"]:
            if not is_red_bar(account.security_price, prev_close, ratio=0.001):
                print('cannot hold it - close price lower than yesterday')
                return True
    return False


def should_ignore_buy_signal(account, data):
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]
    prev_2 = account.history_data.iloc[prev_pos - 1]
    prev_3 = account.history_data.iloc[prev_pos - 2]
    open_price = data.iloc[0]['open']

    # 任何趋势 如果前面3连红 也不要追了
    if is_red_bar(prev['close'], prev['open'], 0.01) \
            and is_red_bar(prev_2['close'], prev_2['open'], 0.01) \
            and is_red_bar(prev_3['close'], prev_3['open'], 0.01):
        return True

    # 如果下跌趋势 一个红柱也不追
    if prev['sar'] < 0:
        if prev['close'] > prev['open'] \
                and is_red_bar(prev['close'], prev['open'], 0.002):
            # print(account.current_date, 'ignore - do not follow red bar in down trend')
            return True

    # 三红一绿4，直接忽略

    # 四红二绿，直接忽略

    # 绿红红绿，直接忽略

    # 昨天下跌>7% 还低开8% 直接忽略
    if (prev['close'] - prev['open']) / prev['open'] < -0.07 \
            and (open_price - prev['close']) / prev['close'] < -0.07:
        return True

    # 昨天拉着上引线暴跌 >8% 并且光脚，今天直接忽略 凶多吉少
    upline = (prev['high'] - prev['close'])
    downline = (prev['close'] - prev['low'])
    body = (prev['close'] - prev['open'])
    if (prev['close'] - prev['high']) / prev['high'] < -0.08 \
            and downline == 0:
        if body == 0:
            print(account.current_date, 'ignore - yesterday drop >8%')
            return True
        elif (upline - np.abs(body)) / np.abs(body) > 0.85:
            print(account.current_date, 'ignore - yesterday drop >8%')
            return True

    # 如果昨天从最高位到收盘 下跌>8% 今天凶多吉少
    if (prev['close'] - prev['high']) / prev['high'] < -0.08 \
            and prev['close'] < prev['open']:
        print(account.current_date, 'ignore - yesterday drop >8% from highest to close')
        return True

    return False


def should_ignore_sell_signal(account, data):
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


def is_pure_red_bar(current, open_price, highest_price, lowest_price, ratio=0.03):
    if is_red_bar(current, open_price, ratio) \
            and open_price == lowest_price \
            and current == highest_price:
        return True
    return False
