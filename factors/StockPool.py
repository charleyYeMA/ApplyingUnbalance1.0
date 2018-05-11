"""
股票池，选取可以进行投资的股票
"""
from WindPy import *
from pandas import DataFrame
from pandas.tseries.offsets import YearEnd
from factors.BasicTool import CheckWindData
import numpy as np

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
        filename = 'date_StockPool_select_stock_status0.csv'
        if CheckWindData().check_file_data(self.date, 'StockPool', 'select_stock', 'status', 0):
            stockdata['status'] = CheckWindData().get_file_data(filename)
        else:
            status = w.wss(stockdata['Codes'], "trade_status", "tradeDate=" + self.date)
            CheckWindData(status).check_wind_data()
            stockdata['status'] = status.Data[0]
            DataFrame(stockdata['status']).to_csv(filename, encoding='gbk')

        df = DataFrame(stockdata)
        df = df[df['status'] == u'交易']
        # 剔除涨停的股票
        maxud = w.wss(df['Codes'].values.tolist(), "maxupordown", "tradeDate=" + self.date)
        CheckWindData(maxud).check_wind_data()
        df['maxud'] = maxud.Data[0]

        df = df[df['maxud'] < 1]
        # 剔除上市未满三年的股票
        ipo_days = w.wss(df['Codes'].values.tolist(), "ipo_listdays", "tradeDate=" + self.date)
        CheckWindData(ipo_days).check_wind_data()
        df['ipo_days'] = ipo_days.Data[0]
        df = df[df['ipo_days'] > 4 * 365]

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

        # 近三年营业利润为正
        ebit_oper = w.wss(df['Codes'].values.tolist(), "wgsd_ebit_oper",
                          "unit=1;rptDate=" + pre_year_date.strftime("%Y-%m-%d") +";rptType=1;currencyType=")
        ebit_oper1 = w.wss(df['Codes'].values.tolist(), "wgsd_ebit_oper",
                           "unit=1;rptDate=" + pre_year_date1.strftime("%Y-%m-%d") +";rptType=1;currencyType=")
        ebit_oper2 = w.wss(df['Codes'].values.tolist(), "wgsd_ebit_oper",
                           "unit=1;rptDate=" + pre_year_date2.strftime("%Y-%m-%d") + ";rptType=1;currencyType=")
        if ebit_oper.ErrorCode != 0:
            print("数据提取异常")
            raise Exception("数据提取异常")
        df['ebit_oper'] = ebit_oper.Data[0]
        if ebit_oper1.ErrorCode != 0:
            print("数据提取异常")
            raise Exception("数据提取异常")
        df['ebit_oper1'] = ebit_oper1.Data[0]
        if ebit_oper2.ErrorCode != 0:
            print("数据提取异常")
            raise Exception("数据提取异常")
        df['ebit_oper2'] = ebit_oper2.Data[0]
        df = df[df['ebit_oper'] > 0]
        df = df[df['ebit_oper1'] > 0]
        df = df[df['ebit_oper2'] > 0]

        # 近三年FCF和营业收入的比值
        fcf = w.wss(df['Codes'].values.tolist(), "fcff", "unit=1;rptDate=" + pre_year_date.strftime("%Y-%m-%d"))
        fcf1 = w.wss(df['Codes'].values.tolist(), "fcff", "unit=1;rptDate=" + pre_year_date1.strftime("%Y-%m-%d"))
        fcf2 = w.wss(df['Codes'].values.tolist(), "fcff", "unit=1;rptDate=" + pre_year_date2.strftime("%Y-%m-%d"))

        oper_rev = w.wss(df['Codes'].values.tolist(), "oper_rev",
                          "unit=1;rptDate="+ pre_year_date.strftime("%Y-%m-%d") +";rptType=1")
        oper_rev1 = w.wss(df['Codes'].values.tolist(), "oper_rev",
                          "unit=1;rptDate=" + pre_year_date1.strftime("%Y-%m-%d") + ";rptType=1")
        oper_rev2 = w.wss(df['Codes'].values.tolist(), "oper_rev",
                          "unit=1;rptDate=" + pre_year_date2.strftime("%Y-%m-%d") + ";rptType=1")
        if any([fcf.ErrorCode, fcf1.ErrorCode, fcf2.ErrorCode, oper_rev.ErrorCode, oper_rev1.ErrorCode, oper_rev2.ErrorCode]):
            raise Exception("数据提取异常")
        df['fcf_oper'] = np.array(fcf.Data[0])/np.array(oper_rev.Data[0])
        df['fcf1_oper1'] = np.array(fcf1.Data[0])/np.array(oper_rev1.Data[0])
        df['fcf2_oper2'] = np.array(fcf2.Data[0])/np.array(oper_rev2.Data[0])
        df = df[df['fcf_oper'] > 0.05]
        df = df[df['fcf1_oper1'] > 0.05]
        df = df[df['fcf2_oper2'] > 0.05]

        # 近三年ROE的值
        roe = w.wss(df['Codes'].values.tolist(), "roe", "rptDate="+ pre_year_date.strftime("%Y-%m-%d"))
        roe1 = w.wss(df['Codes'].values.tolist(), "roe", "rptDate=" + pre_year_date1.strftime("%Y-%m-%d"))
        roe2 = w.wss(df['Codes'].values.tolist(), "roe", "rptDate=" + pre_year_date2.strftime("%Y-%m-%d"))

        if any([roe.ErrorCode, roe1.ErrorCode, roe2.ErrorCode]):
            raise Exception("数据提取异常")
        df['roe'] = roe.Data[0]
        df['roe1'] = roe1.Data[0]
        df['roe2'] = roe2.Data[0]

        df = df[df['roe'] > 8]
        df = df[df['roe1'] > 8]
        df = df[df['roe2'] > 8]
        stockcodes = df['Codes'].values.tolist()

        return stockcodes
