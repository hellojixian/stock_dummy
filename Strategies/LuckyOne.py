import numpy as np

strategy_info = {
    'last_ignore_buy_date': None,
    'ignore_first_n_mins': 0,
    'buy_at_same_day': False,
    'too_violent_today': False
}


# 默认当天只交易一次，除非早盘就清仓了，
def handle_data(account, data):
    global strategy_info
    if len(account.transcations) \
            and account.current_date == account.transcations.ix[-1].name:
        return

    # reset settings
    # 重置计数器
    if len(data) == 1:
        strategy_info['too_violent_today'] = False
        strategy_info['ignore_first_n_mins'] = 0

    if strategy_info['last_ignore_buy_date'] != account.current_date:
        # 如果局势突然反转
        if should_ignore_buy_signal_exception(account, data):
            if account.security_amount == 0 and should_buy(account, data):
                percent = 100
                vol = int(account.cash * percent / 100 / account.security_price)
                account.order(vol)
        # 普通时候
        elif len(data) > strategy_info['ignore_first_n_mins'] or strategy_info['ignore_first_n_mins'] == 0:
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
    lowest_price_pos = list(data['low'].values).index(lowest_price)
    highest_price = np.max(data['high'].values)
    highest_price_pos = list(data['high'].values).index(highest_price)
    highest_close_price = np.max(data['close'].values)
    current_price = account.security_price
    highest_price_morning = highest_price

    data_len = len(data)
    if data_len > 120:
        highest_price_morning = np.max(data[:120]['high'].values)

    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]
    prev_2 = account.history_data.iloc[prev_pos - 1]
    prev_3 = account.history_data.iloc[prev_pos - 2]
    prev_close = prev['close']
    current_change = (current_price - prev['close']) / prev['close']    
    prev_bar = (prev['close'] - prev['open']) / prev['open']
    prev_2_bar = (prev_2['close'] - prev_2['open']) / prev_2['open']
    current_bar = (current_price - open_price) / open_price
    open_change = (open_price - prev_close) / prev_close
    
    # 如果需要 则忽略前N分钟
    if data_len < strategy_info['ignore_first_n_mins']:
        return False

    # 如果昨天是小红平台 今天随时张过一倍就买入
    if np.abs(prev['change']) < 0.002 \
            and np.abs(current_bar) - np.abs(prev_bar) > 0.01:
        print(account.current_date, account.current_time, 'follow red platform')
        return True

    if data_len == 10:
        # 跟星星策略
        if 0.015 > prev['change'] > 0 \
                and open_price - prev_close > prev_close - prev['open'] \
                and np.abs(prev_bar) > 0.05 \
                and account.security_price > open_price:
            print(account.current_date, account.current_time, 'follow red star')
            return True

    if 30 > data_len > 10:
        # 跟双星策略
        if np.abs(prev_bar) < 0.015 \
                and (prev_close - prev['low']) / prev_close > 0.01 \
                and (prev['open'] - prev['low']) / prev['open'] > 0.01 \
                and np.abs(prev_2_bar) < 0.015 \
                and (prev_2['close'] - prev_2['low']) / prev_2['close'] > 0.01 \
                and (prev_2['open'] - prev_2['low']) / prev_2['open'] > 0.01 \
                and open_price - prev_close > prev_close - prev['open'] \
                and account.security_price > open_price \
                and np.abs(prev['change']) < 0.03 \
                and prev_bar + prev_2_bar > -0.015:
            # 当前价格超过 买入时不能有0.5点以上的上影线
            if (current_price - highest_price) / highest_price < -0.005 \
                    and np.abs(current_bar) - np.abs(prev_bar) > 0.01:
                print(account.current_date, account.current_time, 'follow 2 stars - try luck!', current_bar, prev_bar)
                return True

    if data_len > 120:
        # 跟平行双星，开盘收盘振幅 < 1%
        # 昨天振幅小于 0.5%
        # 今天已经上涨2个点
        if np.abs(prev_bar) < 0.005 \
                and np.abs(prev_2_bar) < 0.01 \
                and current_bar > 0.02 \
                and np.abs(prev['change']) < 0.03:
            print(account.current_date, account.current_time, 'follow 2 stars in the afternoon - try luck!')
            return True

    # 跟十字星 必须是早上，否则就是上涨无力了
    if 120 > data_len > 10:
        # 之前双星 当前上涨已经超过昨日收盘价 并且当前价格高于开盘价 1.5个点
        if np.abs(prev_bar) < 0.015 \
                and (prev_close - prev['low']) / prev_close > 0.01 \
                and (prev['open'] - prev['low']) / prev['open'] > 0.01 \
                and np.abs(prev_2_bar) < 0.015 \
                and (prev_2['close'] - prev_2['low']) / prev_2['close'] > 0.01 \
                and (prev_2['open'] - prev_2['low']) / prev_2['open'] > 0.01 \
                and account.security_price > prev_close \
                and prev_bar + prev_2_bar > -0.015:
            if current_bar > 0.015:
                print(account.current_date, account.current_time, 'follow 2 stars - today low open - try luck!')
                return True

        # 单一十字星 高开高走一点点 昨天不能跌太狠
        if np.abs(prev_bar) < 0.015 \
                and -0.45 > (current_price - prev_close) / prev_close > 0.02 \
                and current_bar > 0.016 \
                and open_change > 0.001 \
                and prev['change'] > -0.045:
            print(account.current_date, account.current_time, 'follow single stars - today going up - try luck!')
            return True

    if data_len > 30:
        # 任何时候 当天的时价超过当日开盘价的 >6% 且 <10% 立即买入 只在正常情况想
        if 0.06 < current_bar < 0.095 \
                and 0.025 < open_change < -0.025:
            print(account.current_date, account.current_time, 'try to catch the boost')
            return True

        # 如果昨天从最高位到收盘 下跌>8% 除非有4%的下影线在跟入
        if (prev_close - prev['high']) / prev['high'] < -0.08:
            if np.abs(open_change) < 0.005 \
                    and current_price > open_price \
                    and (current_price - lowest_price) / lowest_price > 0.04:
                print(account.current_date, account.current_time, 'follow big green bar with downline')
                return True
        else:
            # 普通绿柱后平开 早盘即可买入
            if prev_bar < -0.035 \
                    and np.abs(open_change) < 0.005 \
                    and current_bar > 0.004:
                print(account.current_date, account.current_time, 'follow green bar')
                return True

    if data_len > 45:
        # 光头光脚阳柱 大约3个点 啥时候都可以买
        if is_pure_red_bar(current_price, open_price, highest_price, lowest_price, ratio=0.035):
            print(account.current_date, account.current_time, 'pure red bar and increased 3%')
            return True

        # 抄底 早盘跌倒 -9% 反弹回-3%
        if data_len > 120 and (lowest_price - prev_close) / prev_close < -0.085 \
                and (current_price - prev_close) / prev_close > -0.03 \
                and (highest_price - prev_close) / prev_close < 0.02:
            if has_touch_bottom_jump_up(data[:lowest_price_pos], prev_close) is False:
                print(account.current_date, account.current_time, 'touched the bottom (<-9%) and jump up >-3%')
                if data_len > 180 and (current_price - prev_close) / prev_close < 0.05:
                    return True
                elif (current_price - prev_close) / prev_close < 0.01:
                    return True
            else:
                print(account.current_date, account.current_time,
                      'too violent today - today already touched bottom but still dropping')
                strategy_info['too_violent_today'] = True
                return False

        # 抄底 -2 早盘跌倒 -9% 尾盘爆涨 >9%
        if data_len > 180 and (lowest_price - prev_close) / prev_close < -0.085 \
                and (current_price - prev_close) / prev_close > -0.03 \
                and (highest_close_price - prev_close) / prev_close > 0.085:
            if has_touch_bottom_jump_up(data[:lowest_price_pos], prev_close) is False:
                print(account.current_date, account.current_time, 'touched the bottom (<-9%) and jump up >+9%')
                return True

        # 如果 今天有触底 最高价是在早盘，并且当前尾盘没有跌破昨日收盘价
        if data_len > 220 and (lowest_price - prev_close) / prev_close < -0.085 \
                and (current_price - prev_close) / prev_close > 0.005 \
                and (highest_price - prev_close) / prev_close < 0.05 \
                and highest_price_pos < 120:
            if has_touch_bottom_jump_up(data[:lowest_price_pos], prev_close) is False:
                print(account.current_date, account.current_time,
                      'touched the bottom (<-9%) and jump back in the morning, not break down before ending')
                return True

        # 今日高开 今日涨幅 超过昨日总涨幅，昨日没有上影线, 并且当前没有上影线
        if (prev['high'] - prev['close']) / prev['close'] < 0.005 \
                and prev_bar > 0.01 \
                and (highest_price - current_price) / current_price < 0.011 \
                and current_change - prev_bar > 0.001:
            print(account.current_date, account.current_time, 'buy growth higher than yesterday full body')
            return True

    if data_len > 120:
        # 抄底 早盘跌倒 -5% 反弹回-1.5%
        if (lowest_price - prev_close) / prev_close < -0.05 \
                and (current_price - prev_close) / prev_close > -0.02 \
                and 30 < lowest_price_pos < 120:
            if has_touch_bottom_jump_up(data[:lowest_price_pos], prev_close) is False:
                print(account.current_date, account.current_time, 'touched the bottom (<-5%) and jump up >-1.5%')
                return True
            else:
                print(account.current_date, account.current_time,
                      'too violent today - today already touched bottom but still dropping')
                strategy_info['too_violent_today'] = True
                return False

        # 低开涨过了昨天的最高价
        if open_change < - 0.01 \
                and (prev['close'] - prev['open']) / prev['open'] < 0.005 \
                and (current_price - prev['high']) / prev['high'] > 0:
            print(account.current_date, account.current_time,
                  'buy - low open grow higher than yesterday highest')
            return True

    if data_len > 150:
        # 低开一直盘着，昨天有支撑
        if (prev['low'] - prev['open']) / prev['open'] < -0.04 \
                and -0.015 < open_change < 0.01 \
                and (highest_price - prev_close) / prev_close < 0.011 \
                and (lowest_price - prev_close) / prev_close > -0.012:
            print(account.current_date, account.current_time,
                  'buy - low open and yesterday have downline, not break prev_close until afternoon')
            return True

        # --------- 这个策略 风险最高 获利可能性也最大 可以抵抗连续十字星 ------------
        # 触底反弹 最低价已经下跌 < -0.06 当前价已经相对于最低价反弹了3个点
        # 发生的最低价 至少距离我现在30分钟 这才算弹起来了
        # 而且吃反弹 不能弹得太高了
        if strategy_info['too_violent_today'] is False \
                and (lowest_price - open_price) / open_price < -0.06 \
                and (current_price - lowest_price) / lowest_price > 0.03 \
                and (highest_price - open_price) / open_price > 0.005 \
                and open_change < 0.015 \
                and current_change < -0.03:

            highest_price_after_lowest = np.max(data[lowest_price_pos:]['high'].values)
            if has_touch_bottom_jump_up(data[:lowest_price_pos], prev_close):
                # 之前已经有过触底反弹了
                print(account.current_date, account.current_time,
                      'too violent today - today already touched bottom but still dropping')
                strategy_info['too_violent_today'] = True
                return False
            # 双底反弹不能吃 之前距离最高价下跌过5个点，
            # 找到最低价之前的高价，比较这个价格和在之前的最低价 而且前底价已经低于<4.5% 不能超过3% 如果超过3个点的反弹没弹起来，这一天就算了 太危险
            # print(account.current_date, account.current_time, 'lowest_price_pos:', lowest_price_pos)
            if (highest_price_after_lowest - prev_close) / prev_close > - 0.015 \
                    and (current_price - highest_price_after_lowest) / highest_price_after_lowest < - 0.035:
                # 从最低点到现在 没有更高点(> -0.01)了
                # 如果有 太危险了，直接尾盘再见
                print(account.current_date, account.current_time, 'too violent today - setup mark')
                strategy_info['too_violent_today'] = True
                return False
            elif (data_len - lowest_price_pos > 20) \
                    or (data_len > 180 and (data_len - lowest_price_pos >= 5)):
                print(account.current_date, account.current_time, 'touched the bottom (<-6%) and jump up +3%')
                return True

        if strategy_info['too_violent_today'] is False \
                and (lowest_price - open_price) / open_price < -0.06 \
                and data_len > 180 \
                and data_len - lowest_price_pos >= 5 \
                and (lowest_price - open_price) / open_price < -0.07 \
                and (current_price - lowest_price) / lowest_price > 0.03 \
                and (highest_price - open_price) / open_price > 0.005 \
                and open_change < 0.015:
            print(account.current_date, account.current_time, 'touched the bottom (<-6%) and rapidly jump up +3%')
            return True

        if account.current_time == "14:48" \
                and check_not_too_far_from_highest(current_price, open_price, highest_price, lowest_price) \
                and (is_red_bar(current_price, open_price, ratio=0.015)
                     or (is_red_bar(current_price, open_price, ratio=0.005)
                         and is_red_bar(current_price, lowest_price, ratio=0.015))):
            print(account.current_date, account.current_time, 'buy in the end')
            return True

    # 今日涨幅 2% 但是上引线不能超过实体的50% 而且今日不是跌停开盘的
    if data_len > 90:
        if is_red_bar(current_price, open_price, ratio=0.020):
            upline = (highest_price - current_price)
            body = (current_price - open_price)
            if upline / body < 0.5 \
                    and open_change > 0.08:
                print(account.current_date, account.current_time, 'buy after 1.5 hour open, today > 2%')
                return True

    if 120 > data_len > 90:
        # 昨天小涨幅
        if prev['change'] > 0.5 \
                and open_change > - 0.01 \
                and current_bar > 0.035:
            print(account.current_date, account.current_time, 'buy after 1.5 hour open, today > 3.5%')
            return True

        # 昨天没跌太狠
        if 0.02 > prev['change'] > -0.5 \
                and open_change > - 0.02 \
                and current_bar > 0.035:
            print(account.current_date, account.current_time, 'buy after 1.5 hour open, today > 3.5%')
            return True

    # 尾盘200分钟以后 大于1.5 且没有上引线 并且举例最低点3个点
    upline = (highest_price - current_price)
    if data_len > 200 \
            and is_red_bar(current_price, open_price, ratio=0.015) \
            and is_red_bar(current_price, lowest_price, ratio=0.03) \
            and upline / current_price < 0.002 \
            and current_change < 0.055:
        print(account.current_date, account.current_time, 'buy at the end (180m), today is red bar 1.5% no upline')
        return True

    # 如果昨天是绿柱 今天红色实体超过昨天就可以买入 并且3小时以后
    if prev['change'] < - 0.01 \
            and current_price - open_price > prev['open'] - prev_close \
            and current_bar > 0.01 \
            and open_price > prev_close \
            and prev_2['change'] > -0.075 \
            and data_len > 200:
        print(account.current_date, account.current_time, 'buy - today growth is overed yesterday')
        return True

    # 如果已经是3小时以后，并且高过最低价2个点了 并且没有上影线 则买入
    # 并且没有2.5个点以上的跳空低开
    if data_len > 180 \
            and prev_close < prev['open'] \
            and (current_price - lowest_price) / lowest_price > 0.03 \
            and (highest_price - current_price) / highest_price < 0.005 \
            and open_change > - 0.02 \
            and (current_price - highest_price_morning) / highest_price_morning > 0.01:
        print(account.current_date, account.current_time,
              'buy - at the end (180m) price is already higher than lowest 3%')
        return True

    if data_len > 30:
        # 今日涨幅高于昨日 2.5倍 就试一下运气
        if prev_close > prev['open'] \
                and prev_2['change'] > -0.075 \
                and (current_price - prev_close) / prev_close > 0.01 \
                and current_bar > 0.02 \
                and open_change > - 0.025:
            if (prev_bar < 0.01 and current_bar / prev_bar > 2) \
                    or (prev_bar < 0.015 and current_bar / prev_bar > 2.5):
                print(account.current_date, account.current_time,
                      'buy - today growth higher than yesterday x2.5times, try luck !')
                return True

    # 低开 高过昨天收盘价 昨天是阳柱子>0.01 且高于最低价>0.02
    if data_len > 60:
        if 0.06 > prev['change'] > 0 and prev_bar > 0.015 \
                and open_price < prev_close \
                and (current_price - lowest_price) / lowest_price > 0.02 \
                and (current_price - prev_close) / prev_close > 0.05:
            print(account.current_date, account.current_time,
                  'buy - today growth higher than yesterday and having downline, try luck !')
            return True

    if 120 > data_len > 60:
        if (lowest_price - open_price) / open_price > -0.025 \
                and (current_price - lowest_price) / open_price > 0.05 \
                and open_change > -0.035:
            print(account.current_date, account.current_time,
                  'buy - catch today red bar, try luck !')
            return True

    # 如果下影线 有4.5个点，并且现在已经上涨了1个点 ，并且上影线小于2个点 就试一下运气
    if data_len > 180:
        if prev_2['change'] > -0.075 \
                and (highest_price - prev_close) / prev_close < 0.025 \
                and (current_price - lowest_price) / lowest_price > 0.045 \
                and current_bar > 0.01 \
                and (highest_price - current_price) / highest_price < 0.02 \
                and open_change > -0.02 \
                and current_change < 0.04:
            print(account.current_date, account.current_time,
                  'buy - today downline is >4.5% and current grow >1%, try luck !')
            return True

        if open_change > 0.02 \
                and (lowest_price - prev_close) / prev_close < - 0.015 \
                and current_bar > 0:
            print(account.current_date, account.current_time, 'buy - high open touch bottom grow back')
            return True

        # 低开<2.5点下午走平 最低价没有突破一个点
        if -0.05 < open_change < -0.025 \
                and -0.03 < (lowest_price - open_price) / open_price < 0.015 \
                and current_bar > 0:
            print(account.current_date, account.current_time, 'buy - low open grow up back in the afternoon')
            return True

        # < 昨天绿柱 -8% 平开，最低价没有跌破 1% 下午则买入 最高价没超过4%
        if (prev['close'] - prev['open']) / prev['open'] < -0.05 \
                and prev['change'] < -0.08 \
                and np.abs(open_change) < 0.005 \
                and (lowest_price - prev_close) / prev_close > -0.01 \
                and (highest_price - prev_close) / prev_close < 0.04:
            print(account.current_date, account.current_time, 'buy - after green bar, flat open, dropping less than 1%')
            return True

        # 暴跌之后 触底反弹3个点
        if (prev['close'] - prev['open']) / prev['open'] < - 0.08 \
                and (open_price - prev_close) / open_price < -0.02 \
                and (lowest_price - prev_close) / prev_close < -0.05 \
                and (current_price - lowest_price) / lowest_price > 0.03 \
                and (highest_price - prev_close) / prev_close < 0.02:
            print(account.current_date, account.current_time, 'buy - touch bottom < -5% and jump up 3% after big drop')
            return True

    # 如果是危险区
    if prev['sar'] < 0:
        pass
    # 如果是安全区
    else:
        # 安全区域抢买点 随时超过3.5就买入
        if data_len > 30 \
                and 0.035 < current_bar < 0.095 \
                and prev_close > prev['open'] and prev['change'] >= 0 \
                and open_change > 0.015:
            print(account.current_date, account.current_time, 'try to catch the boost in safe period')
            return True

        if data_len > 180:
            # 如果下影线 有3.5个点，并且现在已经上涨了1个点  就试一下运气
            if prev_2['change'] > -0.075 \
                    and (current_price - lowest_price) / lowest_price > 0.035 \
                    and prev_bar > 0.015 \
                    and current_bar > 0.01:
                print(account.current_date, account.current_time,
                      'buy - today downline is >3.5% and current grow >1%, try luck !')
                return True

            # 如果昨天大于1个点 今天大于昨天1.8倍 就买入
            if prev['change'] > 0.005 \
                    and prev_bar > 0.01 \
                    and current_bar / prev_bar > 1.8:
                print(account.current_date, account.current_time,
                      'buy - today grow more yesterday x1.8 times, try luck !')
                return True

        if account.current_time in ["10:00", "10:30", "11:00"]:
            if is_red_bar(current_price, open_price, ratio=0.01) \
                    and check_not_too_far_from_highest(current_price, open_price, highest_price, lowest_price) \
                    and (prev_close > prev['open'] and (open_price - prev['open']) / prev['open'] > 0.02):
                print(account.current_date, account.current_time, 'buy in the morning')
                return True
        # 如果下午开盘的时候已经是红柱就买入
        if account.current_time in ["13:01", "13:30", "14:00", "14:30", "14:45"]:
            if is_red_bar(current_price, lowest_price, ratio=0.015) \
                    and check_not_too_far_from_highest(current_price, open_price, highest_price, lowest_price) \
                    and is_red_bar(current_price, open_price, ratio=0.005):
                print(account.current_date, account.current_time, 'buy in the afternoon')
                return True

    return False


# 如果跌破买入价就立即卖出
# 如果第二天高开，开盘就买
def should_sell(account, data):
    # 如果本身是空仓就忽略
    if account.security_amount == 0: return False

    data_len = len(data)
    bought_price = account.transcations.iloc[-1]['price']
    prev = account.history_data.loc[account.previous_date]
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev_2 = account.history_data.iloc[prev_pos - 1]
    prev_3 = account.history_data.iloc[prev_pos - 2]
    prev_4 = account.history_data.iloc[prev_pos - 3]
    prev_close = prev['close']
    prev_open = prev['open']
    open_price = data.iloc[0]['open']
    highest_price = np.max(data['high'].values)
    lowest_price = np.min(data['low'].values)
    current_price = account.security_price
    current_change = (current_price - prev_close) / prev_close
    prev_bar = (prev['close'] - prev['open']) / prev['open']
    current_bar = (current_price - open_price) / open_price
    current_return = (current_price - bought_price) / bought_price
    open_change = (open_price - prev_close) / prev_close
    
    if data_len > 200 \
            and (lowest_price - open_price) / open_price < -0.05 \
            and (lowest_price - open_price) / open_price < - 0.01 \
            and open_change > 0.05:
        print(account.current_date, account.current_time,
              'stop winning at the end, today dropped too much')
        return True

    if data_len > 160 \
            and (highest_price - prev_close) / prev_close > 0.085 \
            and prev['change'] > 0.08 \
            and (current_price - highest_price) / highest_price < -0.05:
        print(account.current_date, account.current_time,
              'stop winning at the end, yesterday >9% today upline >5%')
        return True

    # 如果昨天光头红柱，今天没有低开，那就拿住了
    if is_red_bar(prev['close'], prev['open'], ratio=0.03) \
            and prev['close'] == prev['high'] \
            and open_change > - 0.005 \
            and prev['change'] < 0.07:
        return False

    # 如果高开两个点 没有跌破 > -0.005 昨日收盘价 就拿着
    if open_change > 0.02 \
            and (current_price - prev_close) / prev_close > - 0.005:
        return False

    # 如果昨天买在了上影线，今天低开，超过开盘价就卖出
    if data_len > 30:
        if bought_price < prev['high'] \
                and np.abs((prev['close'] - prev['open']) / prev['open']) < 0.01 \
                and (prev['close'] > prev['open'] and (bought_price - prev['close']) / prev['close'] > 0.015) \
                and (current_price - prev_close) / prev_close > 0.005:
            print(account.current_date, account.current_time, 'stop risk, yesterday bought a star')
            return True

    # todo: 如果昨天刚买但是买成了绿柱>0.005 只要见高就卖出 !!!

    # 如果昨天买成了倒垂头 今天还低开 见高就止损卖出
    if np.abs((prev['close'] - prev['open']) / prev['open']) < 0.01 \
            and (prev['low'] - prev['high']) / prev['high'] < -0.06 \
            and (prev['high'] - prev['open']) / prev['open'] < 0.01 \
            and open_change < -0.025:
        if (current_price - prev_close) / prev_close > - 0.02:
            print(account.current_date, account.current_time,
                  'stop loss - low open after is a T')
            return True

    # 按正确的原则 策略不应该买在星星上

    # 如果昨天是十字星，今天跳水< -0.04%开盘 那么距离最高价 1个点就卖出
    if data_len > 30:
        if np.abs((prev['close'] - prev['open']) / prev['open']) < 0.01 \
                and (open_price - prev['close']) / prev['close'] < -0.04 \
                and (highest_price - current_price) / highest_price > 0.01:
            print(account.current_date, account.current_time,
                  'stop loss - today open price is too low')
            return True

    if 30 > data_len:
        if (current_price - bought_price) / bought_price < 0.005 \
                and open_change < -0.01 \
                and (current_price - prev_close) / prev_close < -0.045 \
                and current_return < -0.02:
            print(account.current_date, account.current_time,
                  'stop loss - dropping too much in the morning', current_return)
            return True

    # 低开 没有突破最昨日高价就会落 低于今日开盘价 立即卖出
    if data_len > 10:
        if (open_price - prev['close']) / prev['close'] < -0.03 \
                and (highest_price - current_price) / highest_price > 0.015 \
                and highest_price < prev_close:
            print(account.current_date, account.current_time,
                  'stop loss - open low and not grow over prev close ')
            return True

    # 如果昨天是个大绿柱 并且已经亏损1个点 随时准备卖出
    if prev['change'] < -0.05 \
            and (prev['close'] - prev['open']) / prev['open'] < -0.05 \
            and (current_price - prev_close) / prev_close < 0 \
            and (current_price - bought_price) / bought_price < - 0.015:
        print(account.current_date, account.current_time,
              'stop loss - yesterday is big green bar < -5%')
        return True

    # 以下是开盘止损策略
    if data_len == 1:
        # 大前天是 >-4.5%以上的下跌，今天开盘价低于前天的收盘价，开盘及止损
        if prev_3['change'] < -0.045 \
                and open_price < prev_2['close'] \
                and (open_price - bought_price) / bought_price < -0.005:
            print(account.current_date, account.current_time,
                  'stop loss - open price lower than close price at 2days ago')
            return True

        # 前天涨停一字板，昨天开板了，今天一早就卖出
        if prev_2['change'] > 0.09 and np.abs((prev_2['close'] - prev_2['open']) / prev_2['open']) < 0.01 \
                and prev['change'] > 0.09 and (prev['close'] - prev['open']) / prev['open'] > 0.02:
            print(account.current_date, account.current_time, 'stop loss yesterday not hold 10%')
            return True

        # 如果昨天是个倒锤子 今天开盘就卖出 上引线大于实体 实体>2%
        # 并且如果刚刚没有经历过大跌
        if 0.04 > prev['change'] > 0.025 \
                and prev_3['change'] > - 0.075 \
                and prev_4['change'] > - 0.075 \
                and (prev['close'] - prev['open']) / prev['open'] > 0.025 \
                and ((prev['close'] - prev['open']) / prev['open']) != 0 \
                and ((prev['high'] - prev['close']) / prev['close']) / (
                            (prev['close'] - prev['open']) / prev['open']) > 1.1:
            print(account.current_date, account.current_time, 'stop loss yesterday upline is greater than body')
            return True

        # 如果昨天是 - 字 加1.5点以上的上影线，并且没有下引线支持，开盘就卖出
        if np.abs((prev['close'] - prev['open']) / prev['open']) < 0.01 \
                and np.abs((prev['open'] - prev['low']) / prev['open']) < 0.01 \
                and np.abs((prev['high'] - prev['close']) / prev['close']) > 0.02:
            print(account.current_date, account.current_time,
                  'stop loss yesterday is -- and no downline, only have upline')
            return True

        # 如果昨天是第一次翻红，没有下引线 但是有很长的上引线，开盘就卖出
        if (prev_2['close'] - prev_2['open']) / prev_2['open'] < 0 \
                and prev['change'] > 0.005 \
                and np.abs((prev['open'] - prev['low']) / prev['open']) < 0.01 \
                and np.abs((prev['high'] - prev['close']) / prev['close']) > 0.02 \
                and current_bar < -0.005:
            print(account.current_date, account.current_time,
                  'stop loss yesterday bought a long upline by unlucky and today is dropping')
            return True

    # 如果高开，但是中午跌破昨天涨幅的40% 就赶快卖出
    if data_len > 30:
        if open_change > - 0.002:
            today_change = current_change
            prev_change = (prev_close - prev_open) / prev_open
            if today_change < 0 and prev_change != 0 \
                    and (prev_change - (prev_change + today_change)) / prev_change > 0.65 \
                    and current_price > prev_close:
                print(account.current_date, account.current_time, 'stop loss today lower than yesterday change 65%')
                return True

        # 考虑 如果当前价格跌破昨天最高价的 4%要不要卖出？ 并且昨天没有大的4.5%底部支撑 并且
        if 0.025 > prev['change'] > 0.005 \
                and (prev['open'] - prev['low']) / prev['open'] < 0.045 \
                and (prev['high'] - current_price) / prev['high'] > 0.035:
            if data_len > 120:
                print(account.current_date, account.current_time,
                      'stop loss - price lower than yesterday highest < -3.5% - in afternoon')
                return True
            elif 30 < data_len <= 120 and current_change < - 0.02:
                print(account.current_date, account.current_time,
                      'stop loss - price lower than yesterday highest < -3.5% - in morning')
                return True

        # 如果高开 低走，低于昨天开盘价1个点则卖出
        if open_change > 0.02 \
                and prev_bar < 0 \
                and current_price < prev_close:
            print(account.current_date, account.current_time,
                  'stop loss - high open >2% goes down, lower then yesterday close')
            return True

        if open_change > 0.015 \
                and prev_bar < 0 \
                and current_change < -0.01:
            print(account.current_date, account.current_time,
                  'stop loss - high open > 1.5% goes down, lower then yesterday close < -1%')
            return True

    # 昨天上影线长度 且 涨幅2个点 平开超过0.0055 开盘卖出
    if prev['change'] > 0.023 and data_len == 1 \
            and (prev['close'] - prev['open']) / prev['close'] != 0 \
            and ((prev['high'] - prev['close']) / prev['close']) / (
                        (prev['close'] - prev['open']) / prev['close']) > 0.8 \
            and (prev['close'] - prev['low']) / prev['close'] < 0.005:
        print(account.current_date, account.current_time, "should not hold, yesterday upline is too long")
        return True

    # 跌破买入价就卖出 & 强制停损
    if data_len > 90 \
            and (current_price - bought_price) / bought_price < -0.04 \
            and is_going_down(current_price, data, 15):
        print(account.current_date, account.current_time, 'stop loss today dropped -4% in the day time')
        return True

    # 如果早盘跌破2.5% 就止损
    if 90 > data_len > 30 \
            and (current_price - bought_price) / bought_price < -0.025 \
            and prev['change'] < 0.08 \
            and is_going_down(current_price, data, 15):
        print(account.current_date, account.current_time, 'stop loss today dropped -2.5% in the morning')
        return True

    if 120 > data_len > 60 \
            and (lowest_price - bought_price) / bought_price < -0.01 \
            and (lowest_price - prev_close) / prev_close < -0.035 \
            and current_change < - 0.005 \
            and (current_price - bought_price) / bought_price > 0.01 \
            and prev['change'] < 0.08:
        print(account.current_date, account.current_time, 'stop loss today dropped -2.5% in the morning now jump back')
        return True

    if data_len > 160:
        if (highest_price - current_price) / highest_price > 0.03 \
                and current_price < open_price \
                and current_price == lowest_price \
                and (open_price - current_price) / open_price > 0.015:
            print(account.current_date, account.current_time, 'stop loss after 2hour got a green bar and long upline')
            return True

    if data_len > 220:
        if (highest_price - current_price) / highest_price > 0.01 \
                and current_change < 0.005:
            print(account.current_date, account.current_time, 'stop loss at the end not growing and long upline')
            return True

        # 连续2涨停 今天出现上影线>4%
        if (highest_price - current_price) / highest_price > 0.04 \
                and prev['change'] > 0.08 and prev_2['change'] > 0.08:
            print(account.current_date, account.current_time, 'stop winning at the end, yesterday >9% today upline >4%')
            return True

    if data_len > 230:
        # 尾盘看今天如果没怎么涨，并且上影线比实体还长 就卖出
        if 0.04 > current_change > 0.025 \
                and prev_2['change'] > - 0.075 \
                and prev_3['change'] > - 0.075 \
                and current_change != 0 \
                and ((highest_price - current_price) / current_price) / current_change > 1.1:
            print(account.current_date, account.current_time, 'stop loss today at the end upline is greater than body')
            return True

        # 尾盘，如果昨天有上影线，并且今天最高价没有突破昨天的最高价，那么就在尾盘卖出
        if (prev['high'] - prev['open']) / prev['open'] > 0.04 \
                and np.abs((prev['close'] - prev['open']) / prev['open']) < 0.02 \
                and highest_price < prev['high']:
            print(account.current_date, account.current_time, 'sell in the afternoon, no power to grow')
            return True

    # 如果昨天的SAR是负数数，使用危险区卖出原则
    # 这些原则都非常谨小慎微
    if prev['sar'] < 0:
        # 在危险区内 如果昨天是红柱 今天高开或者平开，比开盘价走低2个点就卖出
        if open_change > - 0.002 \
                and current_change < -0.02 \
                and (current_price - bought_price) / bought_price < -0.02:
            print(account.current_date, account.current_time, 'stop loss - lower than bought price > 2%')
            return True

        # 如果第二天高开
        if open_change > 0.015:
            # 高开一小时后低走1个点 立即买出
            if current_bar < -0.01 \
                    and data_len > 60:
                print(account.current_date, account.current_time, 'stop loss - open price is jump higher 1%')
                return True

        # 如果昨天买到的是2个点以上的绿柱，并且不高于3个点的开盘 开盘立即卖出 并且已经亏损
        if (prev['close'] - prev['open']) / prev['open'] < -0.02 \
                and open_change < 0.03:
            if current_bar > 0.005 \
                    and (current_price - bought_price) / bought_price < -0.015:
                print(account.current_date, account.current_time, 'stop loss because yesterday')
                return True

        # 危险区 刚刚超过买入价后1个点 回落1个点就卖出 并且当前涨幅小于5%
        if (highest_price - bought_price) / bought_price > 0.01 \
                and open_price < bought_price \
                and (highest_price - current_price) / highest_price > 0.015 \
                and highest_price > open_price \
                and current_change < 0.05 \
                and current_bar < 0.02 \
                and data_len > 40:
            if (current_price - bought_price) / bought_price < 0.005:
                print(account.current_date, account.current_time,
                      'cannot hold it - highest price higher than bought price and drop down 1.5%')
                return True

        # 上影线原则：当前距离最高点 低于1个点则卖出 当前价格已经高于买入价格
        if account.current_time in ["13:01", "13:30", "14:00", "14:30"]:
            if 0.03 > (current_price - bought_price) / bought_price > 0 \
                    and (current_price - highest_price) / highest_price < -0.035 \
                    and current_bar < -0.035:
                print(account.current_date, account.current_time,
                      'cannot hold it - current price lower than bought price 1%')
                return True

            if highest_price > prev['high']:
                if (current_price - bought_price) / bought_price > 0.03 \
                        and (current_price - highest_price) / highest_price < -0.035:
                    print(account.current_date, account.current_time,
                          'cannot hold it - dropped 3.5% from today highest price')
                    return True
            else:
                if (current_price - bought_price) / bought_price > 0.03 \
                        and (current_price - highest_price) / highest_price < -0.025:
                    print(account.current_date, account.current_time,
                          'cannot hold it - dropped 2.5% from today highest price')
                    return True

        # 如果下午已经上涨无力，并且今天开盘不是高跳水
        if account.current_time == "14:45":
            if not is_red_bar(current_price, open_price, ratio=0.001) \
                    and (current_price - prev['close']) / prev['close'] < 0.01:
                print(account.current_date, account.current_time,
                      'cannot hold it - close price is growth rate not higher than yesterday 1% after 14:45 ')
                return True
    # 下面是在安全区的策略
    else:
        # 如果昨天是涨停 并且今天不是涨停开盘 跌破上影线3.5%也要卖出
        # 这个策略会止盈过度
        if (current_price - bought_price) / bought_price > 0.03 \
                and prev['change'] > 0.09 \
                and (open_price - prev['close']) / prev['close'] < 0.091 \
                and current_bar < -0.055:
            print(account.current_date, account.current_time,
                  'cannot hold it - dropped 4.5% from today highest price and yesterday changes is >9%')
            return True

        # 当日下跌过昨日收盘价 超过3个点卖出
        if data_len > 20 and current_change < -0.035 \
                and open_change < 0.08:
            if (current_price - bought_price) / bought_price < -0.015:
                print(account.current_date, account.current_time,
                      'should sell today dropped 3.5% and lower than bought_price 1.5%')
                return True
            elif data_len > 120:
                print(account.current_date, account.current_time, 'should sell today dropped 3.5% in the afternoon')
                return True

        if data_len > 20 and current_change < -0.035 \
                and open_change < -0.015:
            if (current_price - bought_price) / bought_price < -0.001:
                print(account.current_date, account.current_time,
                      'should sell today low open dropped 3.5% and lower than bought_price 1.5%')
                return True

        # 下午的时候比昨天的收盘价还低 说明已经上涨无力了
        if account.current_time in ["14:30", "14:45"]:
            if not is_red_bar(current_price, prev_close, ratio=0.001):
                print(account.current_date, account.current_time, 'cannot hold it - current price lower than yesterday')
                return True
    return False


def should_ignore_buy_signal(account, data):
    global strategy_info
    data_len = len(data)
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]
    prev_2 = account.history_data.iloc[prev_pos - 1]
    prev_3 = account.history_data.iloc[prev_pos - 2]
    prev_4 = account.history_data.iloc[prev_pos - 3]
    prev_5 = account.history_data.iloc[prev_pos - 4]
    open_price = data.iloc[0]['open']
    prev_close = prev['close']
    prev_open = prev['open']
    current_price = account.security_price
    lowest_price = np.min(data['low'].values)
    highest_price = np.max(data['high'].values)
    prev_bar = (prev['close'] - prev['open']) / prev['open']
    current_bar = (current_price - open_price) / open_price

    # 大红大绿 大红大绿 今天忽略
    if (prev['close'] - prev['open']) / prev['open'] < -0.065 \
            and (prev_2['close'] - prev_2['open']) / prev_2['open'] > 0.07 \
            and (prev_3['close'] - prev_3['open']) / prev_3['open'] < - 0.07 \
            and (prev_4['close'] - prev_4['open']) / prev_4['open'] > 0.07:
        print(account.current_date, 'too violent recently , Red Green Red Green in a row')
        strategy_info['too_violent_today'] = True
        return True

    # 四天最高价连续走低 也可以作为屏蔽原则

    # 任何趋势 如果前面3连红 就看尾盘了
    if is_red_bar(prev['close'], prev['open'], 0.01) \
            and is_red_bar(prev_2['close'], prev_2['open'], 0.01) \
            and is_red_bar(prev_3['close'], prev_3['open'], 0.01) \
            and data_len <= 200:
        print(account.current_date, 'ignore - do not follow 3 red bar')
        strategy_info['ignore_first_n_mins'] = 200

    # 如果下跌趋势 一个红柱也不追早盘 全看尾盘
    if prev['sar'] < 0:
        if prev['close'] > prev['open'] \
                and is_red_bar(prev['close'], prev['open'], 0.002) \
                and data_len <= 180 \
                and prev_bar > 0.025 \
                and prev_2['close'] < prev_2['open']:
            print(account.current_date, 'ignore - do not follow red bar in down trend')
            strategy_info['ignore_first_n_mins'] = 180

    # 两个涨停 一个跌停 就等尾盘再说
    if prev['change'] < -0.08 \
            and prev_2['change'] > 0.08 \
            and prev_3['change'] > 0.08 \
            and data_len <= 0:
        print(account.current_date, 'ignore - too violent +10% +10% -10% ')
        strategy_info['ignore_first_n_mins'] = 220

    # 四红一绿，等晚盘再操作
    if prev['change'] < 0 \
            and prev_2['change'] > 0 \
            and prev_3['change'] > 0 \
            and prev_4['change'] > 0 \
            and prev_5['change'] > 0 and data_len <= 220:
        print(account.current_date, '4 red 1green - wait until before closing ')
        strategy_info['ignore_first_n_mins'] = 220
    elif prev['change'] < 0 \
            and prev_2['change'] > 0 and (prev_2['close'] - prev_2['open']) / prev_2['open'] > 0.015 \
            and prev_3['change'] > 0 and (prev_3['close'] - prev_3['open']) / prev_3['open'] > 0.015 \
            and data_len <= 180:
        print(account.current_date, '2 red 1green - wait until before closing ')
        strategy_info['ignore_first_n_mins'] = 180
    elif prev['change'] > 0.01 \
            and (prev['close'] - prev['open']) / prev['open'] > 0.01 \
            and prev_2['change'] > 0.01 \
            and (prev_2['close'] - prev_2['open']) / prev_2['open'] > 0.01 \
            and data_len <= 120:
        print(account.current_date, '2 red - wait until before closing ')
        strategy_info['ignore_first_n_mins'] = 120

    if prev['change'] > 0 and prev['close'] > prev['open'] \
            and prev_2['change'] > 0 and prev_2['close'] > prev_2['open'] \
            and prev_3['change'] > 0 and prev_3['close'] > prev_3['open'] \
            and data_len <= 180:
        print(account.current_date, 'skip first (180m) - 3win in a row')
        strategy_info['ignore_first_n_mins'] = 180

    # 昨天下跌>7% 还低开8% 直接忽略
    if (prev['close'] - prev['open']) / prev['open'] < -0.07 \
            and (open_price - prev['close']) / prev['close'] < -0.07:
        print(account.current_date, 'ignore today - dropped too much')
        return True

    # 昨天拉着上引线暴跌 >8% 并且光脚，今天直接忽略 凶多吉少
    upline = (prev['high'] - prev['close'])
    downline = (prev['close'] - prev['low'])
    body = (prev['close'] - prev['open'])
    if (prev['close'] - prev['high']) / prev['high'] < -0.08 \
            and downline == 0 and data_len <= 200:
        if body == 0:
            print(account.current_date, 'ignore - yesterday drop >8%')
            strategy_info['ignore_first_n_mins'] = 200
        elif (upline - np.abs(body)) / np.abs(body) > 0.85:
            print(account.current_date, 'ignore - yesterday drop >8%')
            strategy_info['ignore_first_n_mins'] = 200

    # 如果昨天从最高位到收盘 下跌>8% 今天凶多吉少
    if (prev['close'] - prev['high']) / prev['high'] < -0.08 \
            and prev['close'] < prev['open'] \
            and data_len <= 100:
        print(account.current_date, 'ignore - yesterday drop >8% from highest to close')
        strategy_info['ignore_first_n_mins'] = 100

    return False


def should_ignore_buy_signal_exception(account, data):
    data_len = len(data)
    prev_pos = account.history_data.index.get_loc(account.previous_date)
    prev = account.history_data.loc[account.previous_date]
    prev_2 = account.history_data.iloc[prev_pos - 1]
    open_price = data.iloc[0]['open']
    current_price = account.security_price
    lowest_price = np.min(data['low'].values)
    highest_price = np.max(data['high'].values)
    prev_close = prev['close']
    prev_open = prev['open']
    prev_bar = (prev['close'] - prev['open']) / prev['open']
    current_bar = (current_price - open_price) / open_price

    if data_len > 30:
        # 触底反弹 最低价已经下跌 < -0.06 当前价已经相对于最低价反弹了3个点
        if strategy_info['ignore_first_n_mins'] is False \
                and (lowest_price - open_price) / open_price < -0.06 \
                and (current_price - lowest_price) / lowest_price > 0.03:
            # 从最低点到现在 没有更高点(> -0.01)了
            lowest_price_pos = list(data['low'].values).index(lowest_price)
            highest_price_after_lowest = np.max(data[lowest_price_pos:]['high'].values)
            # todo: 当前价高过错过的最高点
            if (highest_price_after_lowest - prev_close) / prev_close > - 0.015 \
                    and (current_price - highest_price_after_lowest) / highest_price_after_lowest > 0.05:
                # 如果有 太危险了，直接尾盘再见
                print(account.current_date, account.current_time, 'too violent today')
                strategy_info['ignore_first_n_mins'] = 200
                strategy_info['too_violent_today'] = True
                return False
            else:
                print(account.current_date, account.current_time,
                      '-- Cancel ignoring, touched the bottom (<-6%) and jump up +3%')
                strategy_info['ignore_first_n_mins'] = 0
                return True

        if (lowest_price - prev_close) / prev_close < -0.085 \
                and 0.01 > (current_price - prev_close) / prev_close > -0.03:
            print(account.current_date, account.current_time,
                  '-- Cancel ignoring, touched the bottom (<-9%) and jump up >+3%')
            strategy_info['ignore_first_n_mins'] = 0
            return True

        if (lowest_price - open_price) / open_price > -0.025 \
                and (current_price - lowest_price) / open_price > 0.05:
            strategy_info['ignore_first_n_mins'] = 0
            return True

    if data_len > 60:
        if (prev['close'] - prev['open']) / prev['open'] < -0.07 \
                and (prev_2['close'] - prev_2['open']) / prev_2['open'] > 0.07 \
                and open_price < prev['close'] \
                and current_price > prev_2['close']:
            print(account.current_date, account.current_time,
                  '-- Cancel ignoring, current price is already higher than 2days ago close price')
            strategy_info['ignore_first_n_mins'] = 0
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


def search_nearest_lowest(data):
    lowest = data['low'][-1]
    for i in range(len(data)):
        pos = len(data) - i - 2
        if data['low'][pos] < lowest:
            lowest = data['low'][pos]
        else:
            break
    return lowest


def observe_nearest_continue_win(data):
    mcw = 0
    return mcw


def observe_star_count(data):
    count = 0
    return count


def check_not_too_far_from_highest(current_price, open_price, highest_price, lowest_price):
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


def is_star(rec):
    # 上下影线总和比实体长 并且实体小于3个点
    if rec['close'] >= rec['open']:
        body = rec['close'] - rec['open']
        upline = rec['high'] - rec['close']
        downline = rec['close'] - rec['low']
    else:
        body = rec['open'] - rec['close']
        upline = rec['high'] - rec['open']
        downline = rec['open'] - rec['low']
    if np.abs(body / rec['open']) > 0.03 \
            and (upline + downline) >= body \
            and downline != downline != 0 \
            and np.abs(upline / downline) > 0.6:
        return True

    return False


def has_touch_bottom_jump_up(data, prev_close):
    open_price = data.iloc[0]['open']
    has_bottom = False
    lowest_price = 0
    lowest_price_pos = 0

    for i in range(1, len(data)):
        data_slice = data[:i]
        lowest_price = np.min(data_slice['low'].values)
        lowest_price_pos = list(data_slice['low'].values).index(lowest_price)
        if (lowest_price - prev_close) / prev_close < -0.05:
            has_bottom = True
            break

    if has_bottom and lowest_price_pos:
        data_slice = data[lowest_price_pos:]
        highest_price = np.max(data_slice['high'].values)
        highest_price_pos = list(data_slice['high'].values).index(highest_price)
        if (highest_price - lowest_price) / lowest_price > 0.03 \
                and (lowest_price - open_price) / open_price < -0.045 \
                and highest_price_pos > 5:
            print('--detected has previous touch bottom--')
            return True
    return False
