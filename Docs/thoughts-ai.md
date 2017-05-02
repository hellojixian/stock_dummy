训练寻找买入点

红柱之前的那个柱子的最低价之后的反弹
第二天的最低价比今天高
寻找最低价出现之后的次低价位置
敏感区域1个点 距离最低价出现后的最远的次低价作为买入点

先判断是否是可买入日，
在判断哪里是可买入点

expected_sell = next_highest * 0.99 
expected_buy = today_lowest * 1.01
expected_return = (expected_sell - expected_buy) / expected_buy
if expected_return > 0.2 \
    and (next_lowest - today_lowest)/today_lowest > 0.01:
    # nextday has 0.2 profit
    return True 

卖出点是第二天的最高价 低于今天的最高价
尝试匹配今天的最高点

止损风险 假设风险承担能力是-2% 第二天任何时候不会出现跌破买入价-2%的时候



加快学习过程，设置一个值 然后从头到尾跑一遍
如果遇到错误 就回来调整设置，再从头到尾跑一遍
保留正确错误比最大的策略
也许应该允许错误先做统计
第二天只能止损卖出 视为错误


动态策略数据库
每一个买入策略 要跟随一组排除策略，当实战时，排除策略需要动态增加
如果买入点在早盘 那么就要结合昨日尾盘2小时数据来判断


# 动态画图
## 曲线 dynamic last 120 mins
current_jump = (current_price - lowest_price) / lowest_price
current_drop = (current_price - highest_price) / highest_price
current_upline
current_downline

## 直线
current_return = (current_price - bought_price) / bought_price 


# 要做的事情
先画图
标记买入日
测试买入点
计算概率
训练数据必须是100%争取
测试数据只统计胜率
然后训练进化能力


# Knowledge entity
```
entity_id
ranges:
    - static ranges
    - dynamic ranges
preformance:
    - total_win_count
    - total_win_score
    - total_loss_count
    - total_loss_score
exceptions
    - rules
    - timestamp
last_activation
    - result
    - timestamp
    - sec_id
limit:    
    - max_allowed_fund_rate
    - max_stop_loss_rate
```

# Engine
```
提供买卖接口
对基线收益进行结算，
标注数据
    基础数据
    回测所需要的数据
        利润统计
        买卖交易数据
        
也许引擎的工作应该是纯数据的调用
图形输出应该氛围模块化
每一个图标所需要的数据都是不一样的，应该分别调试不同的图表
但是总的UI输出框架可以由引擎负责，这样方便模块化处理               
```

static environment

prev3_bar
prev3_change    +10 to -10
prev2_change    +10 to -10
prev2_bar
prev2_open_change
prev2_upline
prev2_downline
prev2_amp_abs   0 to 20
prev_change     +10 to -10


* 提供动态数据 tick分钟
* 提供接口允许策略获取必须的数据
* 引擎可视化部分也可以有接口来获取自己需要的那部分数据
* 提供交易接口
* 输出记录买卖日志

# Transcation Entity
```
transcation:
    date
    time
    action - [buy,sell]
    price
    vol
    pattern_id
    fee
```
- a trade has many buy action and one sell action
```
trade:    
    - buy_actions 
        - [ t_id ]
    - sell_action
        - t_id
    - start_time
    - end_time
    - duration
    - total_return
    - daily_return
    - fee 
```

# TODO：
- 重新搭建引擎接口
- 允许多次买入，只要还有钱就可以买入
- 允许多次卖出，只要还有货，且不是当天购买的就可以卖出

# Note
按这个链接来看 每次买入和卖出后至少0.8个点才算平本
每次单方向交易成本大约0.4%
- http://baike.baidu.com/item/%E8%82%A1%E7%A5%A8%E4%BA%A4%E6%98%93%E6%89%8B%E7%BB%AD%E8%B4%B9
- http://chaoshi.pingan.com/tool/gupiao.shtml

# Reference
https://matplotlib.org/examples/pylab_examples/barchart_demo2.html
https://matplotlib.org/examples/pylab_examples/barchart_demo.html
https://matplotlib.org/examples/pylab_examples/axes_demo.html
https://matplotlib.org/examples/pylab_examples/axes_zoom_effect.html Zoom