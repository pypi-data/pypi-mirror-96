#!/usr/bin/python
# -*- coding: utf8 -*-
# cp936
#
# The MIT License (MIT)
#
# Copyright (c) 2010-2017 fasiondog
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#===============================================================================
# History:
# 1. 20170704, Added by fasiondog
#===============================================================================

from hikyuu import OrderBrokerBase
from hikyuu import Datetime


class OrderBrokerWrap(OrderBrokerBase):
    """订单代理包装类，用户可以参考自定义自己的订单代理，加入额外的处理
       包装只有买卖操作参数只有(code, price, num)的交易接口类
    """
    def __init__(self, broker, real=True, slip=0.03):
        """
        订单代理包装类，用户可以参考自定义自己的订单代理，加入额外的处理
    
        :param bool real: 下单前是否重新实时获取实时分笔数据
        :param float slip: 如果当前的卖一价格和指示买入的价格绝对差值不超过slip则下单，
                            否则忽略; 对卖出操作无效，立即以当前价卖出
        """
        super(OrderBrokerWrap, self).__init__()
        self._broker = broker
        self._real = real
        self._slip = slip

    def _buy(self, datetime, market, code, price, num):
        """实现 OrderBrokerBase 的 _buy 接口"""
        if self._real:
            import tushare as ts
            df = ts.get_realtime_quotes(code)
            new_price = float(df.ix[0]['ask'])
            if (abs(new_price - price) <= self._slip):
                self._broker.buy(code, new_price, num)
            else:
                print("out of slip, not buy!!!!!!!!!!")
            return Datetime.now()
        else:
            self._broker.buy(code, price, num)
            return datetime

    def _sell(self, datetime, market, code, price, num):
        """实现 OrderBrokerBase 的 _sell 接口"""
        if self._real:
            import tushare as ts
            df = ts.get_realtime_quotes(code)
            new_price = float(df.ix[0]['bid'])
            self._broker.sell(code, new_price, num)
            return Datetime.now()
        else:
            self._broker.sell(code, price, num)
            return datetime


class TestOrderBroker:
    """用于测试的订单代理，仅在执行买入/卖出时打印信息"""
    def __init__(self):
        pass

    def buy(self, code, price, num):
        print("买入：%s  %.3f  %i" % (code, price, num))

    def sell(self, code, price, num):
        print("卖出：%s  %.3f  %i" % (code, price, num))


def crtOB(broker, real=True, slip=0.03):
    """
    快速生成订单代理包装对象
    
    :param broker: 订单代理示例，必须拥有buy和sell方法，并且参数为 code, price, num
    :param bool real: 下单前是否重新实时获取实时分笔数据
    :param float slip: 如果当前的卖一价格和指示买入的价格绝对差值不超过slip则下单，
                        否则忽略; 对卖出操作无效，立即以当前价卖出
    """
    return OrderBrokerWrap(broker, real, slip)