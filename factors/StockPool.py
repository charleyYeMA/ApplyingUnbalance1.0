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
        CheckWindData().check_wind_data(status)
        stockdata['status'] = status.Data[0]

        df = DataFrame(stockdata)
        df = df[df['status'] == u'交易']
        # 剔除涨停的股票
        maxud = w.wss(df['Codes'].values.tolist(), "maxupordown", "tradeDate=" + self.date)
        CheckWindData().check_wind_data(maxud)
        df['maxud'] = maxud.Data[0]

        df = df[df['maxud'] < 1]
        # 剔除上市未满三年的股票
        ipo_days = w.wss(df['Codes'].values.tolist(), "ipo_listdays", "tradeDate=" + self.date)
        CheckWindData().check_wind_data(ipo_days)
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
        df_opprofit = DataFrame()
        # 近三年营业利润为正
        try:
            c = MongoClient()
            db = c.fundamentaldata
            collections = [codes[-2:] + codes[0:6] for codes in df['Codes'].values.tolist()]
            for coll in collections:
                # 提取营业利润数据
                for doc in db[coll].find({"year":{"$gte" : pre_year_date2}}):
                    opprofit = doc['profit_statement']['OPPROFIT']
                    op_dict = DataFrame({'ebit_oper' : opprofit[0], 'ebit_oper1':opprofit[1], 'ebit_oper2':opprofit[2]},
                                        index = [pre_year_date])
                    df_opprofit = pd.concat([df_opprofit, op_dict])
                # 提取FCF和营业收入数据
                '''
                FCF计算：息税前利润（1-所得税率）+折旧与摊销-营运资金增加-购建固定悟性和长期资产支付的现金
                所得税率=所得税/利润总额
                营运资金=（流动资产-货币资金) - (流动负债-短期借款-应付短期债券-年内到期的长期借款-一年内到期的应付债券）
                息税前利润= （营业总收入-税金的增加）-(营业成本+利息支出+手续费及佣金支出+销售费用+管理费用+坏账损失+存货跌价损失）

                '''
                for doc in db[coll].find({"year" : pre_year_date}):
                    tax = doc['profit_statement']['TAX']
                    tot_profit = doc['profit_statement']['TOT_PROFIT']

                    tot_cur_assets = doc['balance_sheet']['tot_cur_assets']
                    monetary_cap = doc['balance_sheet']['MONETARY_CAP']
                    tot_cur_liab = doc['balance_sheet']['TOT_CUR_LIAB']
                    st_borrow = doc['balance_sheet']['ST_BORROW']
                    st_bonds_payable = doc['balance_sheet']['ST_BONDS_PAYABLE']
                    non_cur_liab_due_within_1y = doc['balance_sheet']['NON_CUR_LIAB_DUE_WITHIN_1Y']

                    tot_oper_rev = doc['profit_statement']['TOT_OPER_REV']
                    taxes_surcharges_ops = doc['profit_statement']['TAXES_SURCHARGES_OPS']
                    oper_cost = doc['profit_statement']['OPER_COST']
                    int_exp = doc['profit_statement']['INT_EXP']
                    handing_chrg_comm_exp = doc['profit_statement']['HANDING_CHRG_COMM_EXP']
                    selling_dist_exp = doc['profit_statement']['SELLING_DIST_EXP']
                    gerl_admin_exp = doc['profit_statement']['GERL_ADMIN_EXP']

                    cash_pay_acq_const_fiolta = doc['cash_flow_statement']['CASH_PAY_ACQ_CONST_FIOLTA']
                for doc in db[coll].find({"year": pre_year_date1}):
                    tot_cur_assets1 = doc['balance_sheet']['tot_cur_assets']
                    monetary_cap1 = doc['balance_sheet']['MONETARY_CAP']
                    tot_cur_liab1 = doc['balance_sheet']['TOT_CUR_LIAB']
                    st_borrow1 = doc['balance_sheet']['ST_BORROW']
                    st_bonds_payable1 = doc['balance_sheet']['ST_BONDS_PAYABLE']
                    non_cur_liab_due_within_1y1 = doc['balance_sheet']['NON_CUR_LIAB_DUE_WITHIN_1Y']

                 #所得税率
                tax_percent = np.array(tax)/np.array(tot_profit)
                work_cap = (np.array(tot_cur_assets) - np.array(monetary_cap)) - (np.array(tot_cur_liab) - np.array(st_borrow) - np.array(st_bonds_payable) -
                                                              np.array(non_cur_liab_due_within_1y))
                work_cap1 = (np.array(tot_cur_assets1) - np.array(monetary_cap1)) - (np.array(tot_cur_liab1) - np.array(st_borrow1) - np.array(st_bonds_payable1) -
                                                              np.array(non_cur_liab_due_within_1y1))
                delta_work_cap = work_cap - work_cap1

                ebit = (np.array(tot_oper_rev) - np.array(taxes_surcharges_ops)) - (np.array(oper_cost) + np.array(int_exp)+
                                            np.array(handing_chrg_comm_exp) + np.array(selling_dist_exp) + np.array(gerl_admin_exp))
                fcf = ebit * tax_percent - delta_work_cap - np.array(cash_pay_acq_const_fiolta)
                #raise Exception("FCF计算存在缺失，数据不全")

        except Exception as e:
            print(str(e))

        df = df[df_opprofit['ebit_oper'] > 0]
        df = df[df_opprofit['ebit_oper1'] > 0]
        df = df[df_opprofit['ebit_oper2'] > 0]

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
