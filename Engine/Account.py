'''
Account 主要管理可共享的资金账户信息和最近交易信息
独立出一个对象为了实现多个线程同时回测
'''

class Account:
    def __init__(self, init_cash=10000):
        self.init_cash = init_cash
        pass