import numpy as np

strategy_info = {
    'last_ignore_buy_date': None,
    'ignore_first_n_mins': 0
}


def handle_data(account, data):
    global strategy_info
    if len(account.transcations) \
            and account.current_date == account.transcations.ix[-1].name:
        return

    if strategy_info['last_ignore_buy_date'] != account.current_date:
        if len(data) > strategy_info['ignore_first_n_mins'] or strategy_info['ignore_first_n_mins'] == 0:
            if should_ignore_buy_signal(account, data):
                strategy_info['last_ignore_buy_date'] = account.current_date
            elif account.security_amount == 0 and should_buy(account, data):
                percent = 100
                vol = int(account.cash * percent / 100 / account.security_price)
                account.order(vol)

    if should_sell(account, data):
        account.order(-account.security_amount)
    pass


# 连续2坏 休息2次
# 两次时间点判断追涨
def should_buy(account, data):
    open_price = data.iloc[0]['open']
    lowest_price = np.min(data['low'].values)
    highest_price = np.max(data['high'].values)
    current_price = account.security_price

    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]
    current_change = (account.security_price - prev['close']) / prev['close']

    # 如果需要 则忽略前N分钟
    if len(data) < strategy_info['ignore_first_n_mins']:
        return False

    # 重置计数器
    strategy_info['ignore_first_n_mins'] = 0

    # 任何时候 >6% 且 <10% 立即买入
    if 0.06 < current_change < 0.095:
        print(account.current_date, account.current_time, 'try to catch the boost')
        return True

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
    if is_pure_red_bar(account.security_price, open_price, highest_price, lowest_price, ratio=0.035):
        return True

    if account.current_time == "14:48" \
            and check_not_too_far_from_highest(account.security_price, open_price, highest_price) \
            and (is_red_bar(account.security_price, open_price, ratio=0.015)
                 or (is_red_bar(account.security_price, open_price, ratio=0.005)
                     and is_red_bar(account.security_price, lowest_price, ratio=0.015))):
        print(account.current_date, account.current_time, 'buy in the end')
        return True

    # 今日涨幅 2% 但是上引线不能超过实体的50%
    if len(data) > 90:
        if is_red_bar(account.security_price, open_price, ratio=0.020):
            upline = (highest_price - current_price)
            body = (current_price - open_price)
            if upline / body < 0.5:
                print(account.current_date, account.current_time, 'buy after 1.5 hour open, today > 2%')
                return True

    # 尾盘200分钟以后 大于1.5 且没有上引线 并且举例最低点3个点
    upline = (highest_price - current_price)
    if len(data) > 200 \
            and is_red_bar(current_price, open_price, ratio=0.015) \
            and is_red_bar(current_price, lowest_price, ratio=0.03) \
            and upline / current_price < 0.002:
        print(account.current_date, account.current_time, 'buy at the end (180m), today is red bar 1.5% no upline')
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
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev_2 = account.history_data.iloc[prev_pos - 1]
    prev_close = prev['close']
    prev_open = prev['open']
    open_price = data.iloc[0]['open']
    highest_price = np.max(data['high'].values)

    # 如果昨天光头红柱，今天没有低开，那就拿住了
    if is_red_bar(prev['close'], prev['open'], ratio=0.03) \
            and prev['close'] == prev['high'] \
            and (open_price - prev_close) / prev_close > - 0.005 \
            and prev['change'] < 0.07:
        return False

    # 以下是开盘止损策略
    if len(data) == 1:
        # 前天涨停一字板，昨天开板了，今天一早就卖出
        if prev_2['change'] > 0.09 and np.abs((prev_2['close'] - prev_2['open']) / prev_2['open']) < 0.01 \
                and prev['change'] > 0.09 and (prev['close'] - prev['open']) / prev['open'] > 0.02:
            print(account.current_date, account.current_time, 'stop loss yesterday not hold 10%')
            return True

        # 如果昨天是个倒锤子 今天开盘就卖出 上引线大于实体 实体>2%
        if prev['change'] > 0.02 \
                and ((prev['close'] - prev['open']) / prev['open']) != 0 \
                and ((prev['high'] - prev['close']) / prev['close']) / (
                            (prev['close'] - prev['open']) / prev['open']) > 1.1:
            print(account.current_date, account.current_time, 'stop loss yesterday upline is greater than body')
            return True

        # 如果昨天是 - 字 加1.5点以上的上影线，并且没有下引线支持，开盘就卖出
        if np.abs((prev['close'] - prev['open']) / prev['open']) < 0.01 \
                and np.abs((prev['close'] - prev['low']) / prev['close']) < 0.01 \
                and np.abs((prev['high'] - prev['close']) / prev['close']) > 0.02:
            print(account.current_date, account.current_time,
                  'stop loss yesterday is -- and no downline, only have upline')
            return True

        # todo: 如果昨天是第一次翻红，没有下引线 但是有很长的上引线，开盘就卖出

    # 如果高开，但是中午跌破昨天涨幅的40% 就赶快卖出
    if account.current_time in ["11:00", "11:25", "13:01", "13:30"] \
            and (open_price - prev_close) / prev_close > - 0.002:
        today_change = (account.security_price - prev_close) / prev_close
        prev_change = (prev_close - prev_open) / prev_open
        if today_change < 0 and prev_change != 0 and (prev_change - (prev_change + today_change)) / prev_change > 0.65:
            print(account.current_date, account.current_time, 'stop loss today lower than yesterday change 65%')
            return True

    # 昨天上影线长度 且 涨幅2个点 平开超过0.0055 开盘卖出
    if prev['change'] > 0.023 and len(data) == 1 \
            and (prev['close'] - prev['open']) / prev['close'] != 0 \
            and ((prev['high'] - prev['close']) / prev['close']) / (
                        (prev['close'] - prev['open']) / prev['close']) > 0.8 \
            and (prev['close'] - prev['low']) / prev['close'] < 0.005:
        print(account.current_date, account.current_time, "should not hold, yesterday upline is too long")
        return True

    # todo: 暴跌>8%之后 遇到高开 当天尾盘卖出

    # 跌破买入价就卖出 & 强制停损
    if len(data) > 90 \
            and (account.security_price - bought_price) / bought_price < -0.04 \
            and is_going_down(account.security_price, data, 15):
        print(account.current_date, account.current_time, 'stop loss today dropped -4% in the day time')
        return True

    # 如果早盘跌破2.5% 就止损
    if 90 > len(data) > 30 \
            and (account.security_price - bought_price) / bought_price < -0.025 \
            and is_going_down(account.security_price, data, 15):
        print(account.current_date, account.current_time, 'stop loss today dropped -2.5% in the morning')
        return True

    # 如果昨天的SAR是负数数，使用危险区卖出原则
    # 这些原则都非常谨小慎微
    if prev['sar'] < 0:
        # 在危险区内 如果昨天是红柱 今天高开或者平开，比开盘价走低2个点就卖出
        if (open_price - prev_close) / prev_close > - 0.002 \
                and (account.security_price - bought_price) / bought_price < -0.02:
            print(account.current_date, 'stop loss - lower than bought price > 2%')
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
                print(account.current_date, account.current_time,
                      'cannot hold it - dropped 2.5% from today highest price')
                return True

        if account.current_time == "14:45":
            if not is_red_bar(account.security_price, open_price, ratio=0.001):
                print(account.current_date, account.current_time, 'cannot hold it - close price lower than yesterday')
                return True
    # 下面是在安全区的策略
    else:
        # 如果昨天是涨停 并且今天不是涨停开盘 跌破上影线3.5%也要卖出
        if (account.security_price - bought_price) / bought_price > 0.03 \
                and prev['change'] > 0.09 \
                and (open_price - prev['close']) / prev['close'] < 0.091 \
                and (account.security_price - highest_price) / highest_price < -0.035:
            print(account.current_date, account.current_time,
                  'cannot hold it - dropped 3.5% from today highest price and yesterday changes is >9%')
            return True

        # 当日下跌过昨日收盘价 超过3个点卖出
        if (account.security_price - prev_close) / prev_close < -0.035:
            print(account.current_date, account.current_time, 'should sell today dropped 3.5%')
            return True
        # 下午的时候比昨天的收盘价还低 说明已经上涨无力了
        if account.current_time in ["14:30", "14:45"]:
            if not is_red_bar(account.security_price, prev_close, ratio=0.001):
                print(account.current_date, account.current_time, 'cannot hold it - close price lower than yesterday')
                return True
    return False


def should_ignore_buy_signal(account, data):
    global strategy_info
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]
    prev_2 = account.history_data.iloc[prev_pos - 1]
    prev_3 = account.history_data.iloc[prev_pos - 2]
    prev_4 = account.history_data.iloc[prev_pos - 3]
    prev_5 = account.history_data.iloc[prev_pos - 4]
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

    # 四红一绿，等晚盘再操作
    if prev['change'] < 0 \
            and prev_2['change'] > 0 \
            and prev_3['change'] > 0 \
            and prev_4['change'] > 0 \
            and prev_5['change'] > 0 and len(data) <= 220:
        print(account.current_date, '4red 1green - wait until before closing ')
        strategy_info['ignore_first_n_mins'] = 220
    elif prev['change'] < 0 \
            and prev_2['change'] > 0 \
            and prev_3['change'] > 0 and len(data) <= 180:
        print(account.current_date, '2red 1green - wait until before closing ')
        strategy_info['ignore_first_n_mins'] = 180
    elif prev['change'] > 0 \
            and prev_2['change'] > 0 and len(data) <= 180:
        print(account.current_date, '2red - wait until before closing ')
        strategy_info['ignore_first_n_mins'] = 180

    # if prev['change'] < 0.09:
    #     print(account.current_date, 'yesterday dropped > 9% - wait until before closing ')
    #     strategy_info['ignore_first_n_mins'] = 200


    if prev['change'] > 0 \
            and prev_2['change'] > 0 \
            and prev_3['change'] > 0:
        return True

    # 昨天下跌>7% 还低开8% 直接忽略
    if (prev['close'] - prev['open']) / prev['open'] < -0.07 \
            and (open_price - prev['close']) / prev['close'] < -0.07:
        return True

    # 昨天拉着上引线暴跌 >8% 并且光脚，今天直接忽略 凶多吉少
    upline = (prev['high'] - prev['close'])
    downline = (prev['close'] - prev['low'])
    body = (prev['close'] - prev['open'])
    if (prev['close'] - prev['high']) / prev['high'] < -0.08 \
            and downline == 0 and len(data) <= 200:
        if body == 0:
            print(account.current_date, 'ignore - yesterday drop >8%')
            strategy_info['ignore_first_n_mins'] = 200

        elif (upline - np.abs(body)) / np.abs(body) > 0.85:
            print(account.current_date, 'ignore - yesterday drop >8%')
            strategy_info['ignore_first_n_mins'] = 200

    # 如果昨天从最高位到收盘 下跌>8% 今天凶多吉少
    if (prev['close'] - prev['high']) / prev['high'] < -0.08 \
            and prev['close'] < prev['open'] and len(data) <= 200:
        print(account.current_date, 'ignore - yesterday drop >8% from highest to close')
        strategy_info['ignore_first_n_mins'] = 200

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


def search_nearest_lowest(data):
    lowest = data['low'][-1]
    for i in range(len(data)):
        pos = len(data) - i - 2
        if data['low'][pos] < lowest:
            lowest = data['low'][pos]
        else:
            break
    return lowest
