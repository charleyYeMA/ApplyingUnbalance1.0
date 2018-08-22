"""
股票池，选取可以进行投资的股票
"""
from WindPy import *
from pandas import DataFrame
from pandas.tseries.offsets import YearEnd
from factors.BasicTool import CheckWindData, MongoClient
import numpy as np
import pandas as pd

w.start()
class StockPool:

    def __init__(self, date):
        self.date = date

    def select_stock(self):
        """
        股票池选择标准如下：
        1：剔除当期*ST，ST个股
        2：剔除当期停牌的个股，剔除上市未满四年的个股
        3：剔除当期涨停的股票
        4：近三年经营活动现金流为正，ROE>10 OR FCF/销售收入>5 ,盈利增长速度协调一致
        5：近三年营业利润为正，且发行在外的总股本增长不明显
        :return:
        """
        stockdata = {}
        # 剔除*ST，ST
        stock = w.wset("sectorconstituent", "date=" + self.date + ";sectorid=a001010f00000000")
        stockdata['Codes'] = stock.Data[1]
        # 剔除当期停牌的个股

        status = w.wss(stockdata['Codes'], "trade_status", "tradeDate=" + self.date)
        stockdata['status'] = status.Data[0]

        df = DataFrame(stockdata)
        df = df[df['status'] == u'交易']
        # 剔除涨停的股票
        maxud = w.wss(df['Codes'].values.tolist(), "maxupordown", "tradeDate=" + self.date)
        df['maxud'] = maxud.Data[0]

        df = df[df['maxud'] < 1]
        # 剔除上市未满三年的股票
        ipo_days = w.wss(df['Codes'].values.tolist(), "ipo_listdays", "tradeDate=" + self.date)
        df['ipo_days'] = ipo_days.Data[0]
        df = df[df['ipo_days'] > 4 * 365]
        # 股票池标准
        date = self.date
        date_1 = datetime.strptime(date, "%Y-%m-%d")
        if date_1.month >= 5:
            pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(1)
            pre_year_date1 = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date2 = datetime.strptime(date, "%Y-%m-%d") - YearEnd(3)
        else:
            pre_year_date = datetime.strptime(date, "%Y-%m-%d") - YearEnd(2)
            pre_year_date1 = datetime.strptime(date, "%Y-%m-%d") - YearEnd(3)
            pre_year_date2 = datetime.strptime(date, "%Y-%m-%d") - YearEnd(4)

        # roe > 5, pe > 0, inc > 0
        roe = w.wss(df['Codes'].values.tolist(), "roe", "rptDate=" + pre_year_date.strftime("%Y-%m-%d"))
        df['roe'] = roe.Data[0]
        pe = w.wss(df['Codes'].values.tolist(), "pe","tradeDate=" + pre_year_date.strftime("%Y-%m-%d")+ ";ruleType=10")
        df['pe'] = pe.Data[0]
        inc = w.wss(df['Codes'].values.tolist(), "wgsd_net_inc","unit=1;rptDate="+pre_year_date.strftime("%Y-%m-%d")+";rptType=1;currencyType=")
        df['net_inc'] = inc.Data[0]
        df = df[df['roe'] > 5]
        df = df[df['pe'] > 0]
        df = df[df['net_inc'] > 0]




        stockcodes = df['Codes'].values.tolist()

        return stockcodes


