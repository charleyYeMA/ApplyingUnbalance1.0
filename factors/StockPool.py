"""
股票池，选取可以进行投资的股票
"""
from WindPy import *
from pandas import DataFrame
w.start()
class StockPool:

    def __init__(self, date):
        self.date = date

    def select_stock(self):
        """
        股票池选择标准如下：
        1：剔除当期*ST，ST个股
        2：剔除当期停牌的个股，剔除上市未满三年的个股
        3：剔除当期涨停的股票
        4：
        5：
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
        df = df[df['ipo_days'] > 3 * 365]

        stockcodes = df['Codes'].values.tolist()

        return stockcodes
