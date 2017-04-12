# 研究课题 - 1
寻找一种概率比较大的图形做早期信号
或者提前买入信号 或者提前忽略信号
* 先把1-2天的K线抽象化
* 然后尝试聚类
* 然后统计第二天输赢的比例
* 筛选出比例大于3：7开的图形 绘图输出

#### 应用：
如果看到早期买入信号，那么当天尾盘买入，第二天坚持拿到尾盘再做决定
如果看到早期危险信号，那么直接忽略第二天的决策

#### 原理
概率大的时候用自动模式，
概率小的时候用手动模式


应该设计两类策略 动态切换
当连续出现上下影线比实体柱大的时候 清档切换为第二策略

如果没有最近连续3连红的概率 那么就最多拿2天
直到再次看见3连红（盈利）在解除

如果前面22交易日只有2连红 那么第二天只要高开就卖出

如果错买了十字星，未来10天就等下午14：00点以后在买入


# 动态画图
## 曲线
current_jump = (current_price - lowest_price) / lowest_price
current_drop = (current_price - highest_price) / highest_price
current_upline
current_downline

## 直线
current_return = (current_price - bought_price) / bought_price 