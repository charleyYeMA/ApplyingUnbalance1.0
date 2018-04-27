"""
    本脚本主要测试各种因子，包括数据提取，返回因子数据
"""
from WindPy import *
from Pandas import DataFrame, Series
import numpy as np
w.start()

class FactorsZoo(object):

    class Mkt:
        def __init__(self, date, stockCodes):
            """

            :param date:  "YYYY-MM-DD"
            :param stockCodes: List
            """
            if not isinstance(date, str):
                print("日期格式不对")
            elif not isinstance(stockCodes, list):
                print("代码格式不对")
            else:
                self.date = date
                self.stockCodes = stockCodes
                self.windLabel = "mkt_cap_ard"

        def getData(self):
            """

            :return:
            """
            mkt_cap_ard = "从数据库中提取数据"

            return mkt_cap_ard

    class Mom:



