"""
包含一切因子预处理的工具，中性化，缺失值填充，异常值诊断剔除，因子alpha预测，beta估计等。
"""
from WindPy import *
import pandas as pd
from sklearn import linear_model
import statsmodels.api as sm
import numpy as np


class FactorProcess:

    @classmethod
    def zscore(cls, group):
        """
        标准化处理
        :param group:
        :return:
        """
        return (group - group.median()) / group.std()

    def neutralize_factor(self, df, factors):
        """
        获取pure alpha因子的方法，将当个因子对其他多有因子进行中性化处理，包括行业因子
        :param df:   DataFrame  因子数据
        :param factors:  list   因子简称
        :return:
        """
        df[factors] = df[factors].apply(lambda x: self.zscore(x.rank()))
        industry = "industry"
        if industry not in factors:
            print("没有行业数据，无法中性化，请添加行业因子")
            raise Exception("没有行业数据，无法中性化，请添加行业因子")
        X = pd.get_dummies(df[industry])
        factors.remove('industry')
        df1 = pd.DataFrame()
        for f in factors:
            factor1 = factors.copy()
            y = df[f]
            factor1.remove(f)
            X[factor1] = df[factor1]
            X = sm.add_constant(X)
            model = sm.OLS(y, X)
            results = model.fit()
            df1[f] = results.resid

        return df1

    def get_alpha(self, stockcodes, date, window):
        """

        :param stockcodes:  股票代码 list
        :param date:   日期  str
        :param window:  窗口  int
        :return:  list
        """
        pre_date = w.tdaysoffset(window, date, "Period=M")
        pre_date = pre_date.Data[0][0].strftime("%Y-%m-%d")
        alpha_data = w.wss(stockcodes, "pct_chg_per", "startDate=" + pre_date + ";endDate=" + date)
        alpha = alpha_data.Data[0]
        return alpha



    def calac_beta(self,alpha, df , factors):
        """
        将中性化后的因子对alpha进行回归，估计每个因子的系数值，包括截距项
        :param alpha:
        :param df:
        :param factors:
        :return:
        """

        X = df[factors]
        y = np.array(alpha)
        X = sm.add_constant(X)
        model = sm.OLS(y,X)
        results = model.fit()

        return results.params


    def forcast_alpha(self, coef_, df1, factors):
        """
        计算alpha
        :param coef_:
        :param df1:
        :param factors:
        :return:
        """
        x = df1[factors]
        alpha_f = x.values.dot(coef_.values[1:])
        return alpha_f
