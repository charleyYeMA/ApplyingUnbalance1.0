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
from factors.BasicTool import Factor
w.start()


class FactorsZoo(object):

    @staticmethod
    def check_data(data):
        """
        检查数据质量，如果提取的数据一半以上是NaN，
        :param data: list
        :return:
        """
        data = np.array(data)
        num = np.count_nonzero(data != data)
        if num > len(data)/2:
            print("数据质量较差，请检查数据库")
            raise Exception("数据质量异常")
        return data.tolist()

    class Size(Factor):
        def __init__(self, date, stockcodes, label):
            """

            :param date:  "YYYY-MM-DD"
            :param stockCodes: List
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            mkt_cap_ard = w.wss(self.stockcodes, "mkt_cap_ard", "unit=1;tradeDate=" + date)
            if mkt_cap_ard.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            size = FactorsZoo.check_data(mkt_cap_ard.Data[0])

            return size

    class Mom(Factor):

        def __init__(self, date, stockcodes, label, window):
            """

            :param date:  "YYYY-MM-DD"
            :param stockCodes: List
            """
            Factor.__init__(self, date, stockcodes, label)
            self.window = window

        def get_data(self):
            """

            :return:
            """
            date = self.date
            window = self.window
            pre_date = w.tdaysoffset(self.window, date, "Period=M")
            if pre_date.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pre_date = pre_date.Data[0][0].strftime("%Y-%m-%d")
            pct_data = w.wss(self.stockcodes, "pct_chg_per", "startDate=" + pre_date + ";endDate=" + date)
            if pct_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pct = pct_data.Data[0]

            return pct

    class Pct(Factor):

        def __init__(self, date, stockcodes, label, window):
            """

            :param date:
            :param stockcodes:
            :param label:
            :param window: 时间窗口（月）
            """
            Factor.__init__(self, date, stockcodes, label)
            self.window = window

        def get_data(self):
            """

            :return:
            """
            date = self.date
            pre_date = w.tdaysoffset(self.window, date, "Period=M")
            if pre_date.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pre_date = pre_date.Data[0][0].strftime("%Y-%m-%d")
            pct_data = w.wss(self.stockcodes, "pct_chg_per", "startDate=" + pre_date + ";endDate=" + date)
            if pct_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pct = FactorsZoo.check_data(pct_data.Data[0])

            return pct

    class Pe(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            pe_data = w.wss(self.stockcodes, "pe", "tradeDate=" + date + ";ruleType=10")
            if pe_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pe = FactorsZoo.check_data(pe_data.Data[0])

            return pe

    class TurnPer(Factor):

        def __init__(self, date, stockcodes, label, window):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)
            self.window = window
        def get_data(self):
            """

            :return:
            """
            date = self.date
            pre_date = w.tdaysoffset(self.window, date, "Period=M")
            if pre_date.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pre_date = pre_date.Data[0][0].strftime("%Y-%m-%d")
            turn_per_data = w.wss(self.stockcodes, "turn_per", "startDate=" + pre_date + ";endDate=" + date)
            if turn_per_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            turn_per = FactorsZoo.check_data(turn_per_data.Data[0])
            return turn_per

    class VolPer(Factor):

        def __init__(self, date, stockcodes, label, window):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)
            self.window = window

        def get_data(self):
            """

            :return:
            """
            date = self.date
            pre_date = w.tdaysoffset(self.window, date, "Period=M")
            if pre_date.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            pre_date = pre_date.Data[0][0].strftime("%Y-%m-%d")
            vol_per_data = w.wss(self.stockcodes, "vol_per", "unit=1;startDate=" + pre_date + ";endDate=" + date)
            if vol_per_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            vol_per = FactorsZoo.check_data(vol_per_data.Data[0])

            return vol_per

    class NetInc(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            date_1 = datetime.strptime(date, "%Y-%m-%d")
            if date_1.month >= 5:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            else:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date = pre_year_date.strftime("%Y-%m-%d")
            net_inc_data = w.wss(self.stockcodes, "wgsd_net_inc", "unit=1;rptDate=" + pre_year_date + ";rptType=1;currencyType=")
            if net_inc_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            net_inc = FactorsZoo.check_data(net_inc_data.Data[0])

            return net_inc

    class Dividend(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            date_1 = datetime.strptime(date, "%Y-%m-%d")
            if date_1.month >= 5:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            else:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date = pre_year_date.strftime("%Y")
            dividend_data = w.wss(self.stockcodes, "div_divpct_3yearaccu","year=" + pre_year_date)
            if dividend_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            dividend = FactorsZoo.check_data(dividend_data.Data[0])

            return dividend

    class Yoyprofit(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            date_1 = datetime.strptime(date, "%Y-%m-%d")
            if date_1.month >= 5:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            else:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date = pre_year_date.strftime("%Y-%m-%d")
            yoyprofit_data = w.wss(self.stockcodes, "yoyprofit", "rptDate=" + pre_year_date)
            if yoyprofit_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            yoyprofit = FactorsZoo.check_data(yoyprofit_data.Data[0])

            return yoyprofit

    class YoyTr(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            date_1 = datetime.strptime(date, "%Y-%m-%d")
            if date_1.month >= 5:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            else:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date = pre_year_date.strftime("%Y-%m-%d")
            yoy_tr_data = w.wss(self.stockcodes, "yoy_tr", "rptDate=" + pre_year_date)
            if yoy_tr_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            yoy_tr = FactorsZoo.check_data(yoy_tr_data.Data[0])

            return yoy_tr

    class DeductedProfit(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            date_1 = datetime.strptime(date, "%Y-%m-%d")
            if date_1.month >= 5:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            else:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date = pre_year_date.strftime("%Y-%m-%d")
            deductedprofit_data = w.wss(self.stockcodes, "deductedprofit", "unit=1;rptDate=" + pre_year_date)
            if deductedprofit_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            deductedprofit = FactorsZoo.check_data(deductedprofit_data.Data[0])

            return deductedprofit

    class Volitality(Factor):

        def __init__(self, date, stockcodes, label, window):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)
            self.window = window
        def get_data(self):
            """

            :return:
            """
            date = self.date
            pre_date = w.tdaysoffset(self.window, date, "Period=M")
            pre_date = pre_date.Data[0][0].strftime("%Y-%m-%d")
            volitality = w.wsd(self.stockcodes, "close", pre_date, date, "Fill=Previous")
            if volitality.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            vol = DataFrame(np.array(volitality.Data).T, columns=volitality.Codes, index=volitality.Times)
            ret = vol / vol.shift(1) - 1
            volitality = FactorsZoo.check_data((math.sqrt(252) * ret.std()).values.tolist())

            return volitality

    class CashNetOperAct(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            date_1 = datetime.strptime(date, "%Y-%m-%d")
            if date_1.month >= 5:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            else:
                pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date = pre_year_date.strftime("%Y-%m-%d")
            cash_data = w.wss(self.stockcodes, "net_cash_flows_oper_act", "unit=1;rptDate="+ pre_year_date +";rptType=1")
            if cash_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")

            cash_net_oper_act = FactorsZoo.check_data(cash_data.Data[0])

            return cash_net_oper_act

    class Industry(Factor):

        def __init__(self, date, stockcodes, label):
            """

            :param date:
            :param stockCodes:
            """
            Factor.__init__(self, date, stockcodes, label)

        def get_data(self):
            """

            :return:
            """
            date = self.date
            industry_data = w.wss(self.stockcodes, "industry_sw", "industryType=1")
            if industry_data.ErrorCode != 0:
                print("数据提取异常")
                raise Exception("数据提取异常")
            industry = FactorsZoo.check_data(industry_data.Data[0])
            return industry



