"""
保存一些基础的类，用于后面的继承使用
"""
import os
import pandas as pd
from pymongo import MongoClient

class Factor(object):
    """
    因子：收益的来源，用于计算一个资产类别对应的因子数值
    """
    def __init__(self, date, stockcodes, label):
        """

        """
        if not isinstance(date, str):
            print("日期格式不对")
        elif not isinstance(stockcodes, list):
            print("代码格式不对")
        else:
            self.date = date
            self.stockcodes = stockcodes
            self.windLabel = label

    def get_data(self):

        pass


class CheckWindData:
    def __init__(self):
        """

        :param data:
        """
        pass

    def check_wind_data(self, data):
        """

        :return:
        """
        if data.ErrorCode != 0:
            raise Exception("数据提取异常")

    def check_file_data(self, date, classname, funcname, label, window):
        """

        :return:
        """
        filename = date + "_" + str(classname) + "_"+str(funcname) + label + str(window) + ".csv"
        if os.path.exists(filename):
            return True

    def get_file_data(self, filename):
        """

        :param filename:
        :return:
        """
        data = pd.read_csv(filename)

        return data

class CheckMongoDB:
    def __init__(self):
        """

        """
        pass

    def check_collection_data(self, date, classname, funcname, label, window ):
        """

        :param date:
        :param classname:
        :param funcname:
        :param label:
        :param window:
        :return:
        """
        pass









