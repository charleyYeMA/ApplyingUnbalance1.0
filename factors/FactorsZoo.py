"""
    本脚本主要测试各种因子，包括数据提取，返回因子数据
"""
from WindPy import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import YearEnd,BusinessDay
from sklearn import linear_model
from pandas import DataFrame, Series
import math
from scipy.ndimage.interpolation import shift
from BasicTool import Factor
w.start()

class FactorsZoo(object):

    class Size(Factor):
        def __init__(self, date, stockcodes, label):
            """

            :param date:  "YYYY-MM-DD"
            :param stockCodes: List
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            mkt_cap_ard = "从数据库中提取数据"

            return mkt_cap_ard

    class Mom(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:  "YYYY-MM-DD"
            :param stockCodes: List
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            mom = "从数据库中提取数据"

            return mom

    class Pct(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            pct = "提取数据"

            return pct

    class Pe(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            pe = "提取数据"

            return pe

    class TurnPer(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            turn_per = "提取数据"
            return turn_per

    class VolPer(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getData(self):
            """

            :return:
            """
            vol_per = "提取数据"

            return vol_per

    class NetInc(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            net_inc = "提取数据"

            return net_inc

    class Dividend(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            dividend = "提取数据"

            return dividend

    class Yoyprofit(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            yoyprofit = "提取数据"

            return yoyprofit

    class YoyTr(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            yoy_tr = "提取数据"

            return yoy_tr

    class DeductedProfit(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            deductedprofit = "提取数据"

            return deductedprofit

    class Volitality(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            volitality = "提取数据"

            return volitality

    class CashNetOperAct(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            cash_net_oper_act = "提取数据"

            return cash_net_oper_act

    class Industry(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            super(Factor, self).__init__(date, stockcodes, label)

        def getdata(self):
            """

            :return:
            """
            industry = "获取行业数据"
            return industry



