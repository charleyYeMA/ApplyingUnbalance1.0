"""
该脚本主要是一些检验因子的方法，主要包括传统的二元分类，横截面回归，fama三因子，也包括新的数据挖掘方法
"""
from WindPy import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import YearEnd,QuarterEnd,BusinessDay
from sklearn import linear_model
from pandas import DataFrame, Series
import math
import statsmodels.api as sm
from datetime import datetime
from scipy.stats import ttest_ind
from collections import OrderedDict

w.start()


class FactorTest:

    class UnbivariateSorts:

        def __init__(self, df, factor=None, weighting=None):
            """

            :param df:
            :param factor:
            :param weighting:
            """
            if not isinstance(df, DataFrame):
                print("因子格式不对")
            elif not isinstance(factor, str):
                print("代码格式不对")
            else:
                self.df = df
                self.factor = factor
                self.weight = weighting

        def unbivariate_sorts(self):
            '''
                    单变量排序分析，根据因子当前的值根据分位数构造成10个组合，然后分别计算10个组合分
                    位数随后一个月的平均收益率，或者计算四因子模型的alpha，最后计算High-Low的差，并
                    计算T统计量。
            '''
            df = self.df
            factor = self.factor
            if factor is None:
                return
            if self.weight == 'VW':
                df['ret'] = df['ret'] * df['SIZE'] / df['SIZE'].sum() * len(df)

            labels = pd.qcut(df[factor].rank(method='first'), 10, labels=False)
            df['decile'] = labels
            df_high = df[df['decile'] == 9]
            df_low = df[df['decile'] == 0]

            differ_ret = df_high['ret'].mean() - df_low['ret'].mean()

            return differ_ret

    class BivariateSorts:

        @classmethod
        def qt(cls, df, factor=None):
            labels = pd.qcut(df[factor].rank(method='first'), 10, labels=False)
            df['labels'] = labels

            return df

        def __init__(self, df, factor=None, control=None, weighting=None):
            """

            :param factor:
            :param control:
            :param weighting:
            """

            if not isinstance(df, DataFrame):
                print("因子格式不对")
            elif not isinstance(factor, str):
                print("代码格式不对")
            elif not isinstance(control, str):
                print("代码格式不对")
            else:
                self.df = df
                self.factor = factor
                self.control = control
                self.weight = weighting

        def bivariate_sorts(self):
            df = self.df
            factor = self.factor
            control = self.control
            weighting = self.weight

            if factor is None or control is None:
                return

            if weighting == 'VW':
                df['ret'] = df['ret'] * df['SIZE'] / df['SIZE'].sum() * len(df)

            labels = pd.qcut(df[control], 10, labels=False)

            df['control'] = labels

            df2 = df.groupby(['control']).apply(self.qt, factor=factor)

            df_high = df2[df2['labels'] == 9]
            df_low = df2[df2['labels'] == 0]

            differ_ret = df_high['ret'].mean() - df_low['ret'].mean()

            return differ_ret

    class FamaMacbeth:

        def __init__(self, df, y_factors=None, x_factors=None, c_factors=None, weighting=None):
            if not isinstance(df, DataFrame):
                print("因子数据格式不对")
            elif not isinstance(y_factors, DataFrame or np):
                print("格式不对")
            elif not isinstance(x_factors, DataFrame or np):
                print("格式不对")
            elif not isinstance(c_factors, DataFrame or np):
                print("格式不对")

            self.df = df
            self.y_factors = y_factors
            self.x_factors = x_factors
            self.c_factors = c_factors
            self.weight = weighting

        def cross_sectional_regressions(self):
            """
            fama_macbeth 横截面回归
            :return:
            """
            df = self.df
            y_factors = self.y_factors
            x_factors = self.x_factors
            c_factors = self.c_factors
            weighting = self.weight
            if y_factors is None or x_factors is None:
                return
            if weighting == 'VM':
                df['ret'] = df['ret'] * df['SIZE'] / df['SIZE'].sum() * len(df)

            X = sm.add_constant(df[c_factors])
            y = df[x_factors]

            model = sm.OLS(y, X)
            results = model.fit()
            df[x_factors] = results.resid
            resid_x = sm.add_constant(df[x_factors])

            y1 = df[y_factors]
            model = sm.OLS(y1, resid_x)
            results_x = model.fit()

            return results_x.tvalues, results_x.params

    class AlphaTest:

        def __init__(self, df, t_factors, c_factors, weighting=None ):
            """

            :param df: 储存因子数据 DataFrame
            :param t_factors:  待检验的因子 DataFrame
            :param c_factors: 控制变量(CAPM,三因子，多因子） DataFrame
            :param weighting: 收益率加权方式
            """
            if not isinstance(df ,DataFrame):
                print("因子数据格式不对")
            elif not isinstance(t_factors, str):
                print("因子数据不对")
            elif c_factors not in ["CAPM","ThreeFactors","FourFactors"]:
                print("请重新选择测试方法")
            else:
                self.df = df
                self.t_factors = t_factors
                self.c_factors = c_factors
                self.weight = weighting

        def sample_and_test_alpha(self):
            """
            这个过程包含两个步骤：第一根据因子计算多空收益，然后回归获得系数和残差，第二步对残差进行抽样，带入到第一步的
            系数中，计算alpha值，重复10000次，最后求得alpha的统计量，观察alpha是否显著
            :return: alpha的显著水平指标
            """
            df_dict = self.df
            t_factors = self.t_factors
            c_factors = self.c_factors
            weighting = self.weight
            # 计算多空收益率
            r_dict = OrderedDict()
            r_mkt = OrderedDict()
            r_smb = OrderedDict()
            r_hml = OrderedDict()
            r_umd = OrderedDict()
            for date in df_dict:
                if t_factors is None:
                    return
                df = df_dict[date]
                if weighting == "VW":
                    df['ret'] = df['ret'] * df['SIZE'] / df['SIZE'].sum() * len(df)
                r = self.compute_return(df,t_factors)
                r_dict[date] = r
                if c_factors == "CAPM":
                    factors = "MKT"
                    r_m = self.compute_return(df, factors)
                    r_mkt[date] = r_m
                if c_factors == "ThreeFactors":
                    factors = ['SIZE','MKT','PB']
                    r_s = self.compute_return(df, factors[0])
                    r_m = self.compute_return(df, factors[1])
                    r_p = self.compute_return(df, factors[2])
                    r_smb[date] = r_s
                    r_hml[date] = r_p
                    r_mkt[date] = r_m
                if c_factors == "FourFactors":
                    factors = ["SIZE","MKT","PB","MOM"]
                    r_s = self.compute_return(df, factors[0])
                    r_m = self.compute_return(df, factors[1])
                    r_p = self.compute_return(df, factors[2])
                    r_u = self.compute_return(df, factors[3])
                    r_smb[date] = r_s
                    r_hml[date] = r_p
                    r_mkt[date] = r_m
                    r_umd[date] = r_u
            # 进行回归，并保存系数
            if c_factors == "CAPM":
                X1 = DataFrame(data=r_mkt)
                X = sm.add_constant(X1)
                y = DataFrame(data = r_dict)
                model = sm.OLS(y,X)
                results = model.fit()
                params = results.params
                resid = results.resid
            if c_factors == "ThreeFactors":
                X1 = DataFrame(data = [r_mkt, r_smb, r_hml])
                X = sm.add_constant(X1)
                y = DataFrame(data = r_dict)
                model = sm.OLS(y, X)
                results = model.fit()
                params = results.params
                resid = results.resid
            if c_factors == "FourFactors":
                X1 = DataFrame(data = [r_mkt, r_smb, r_hml, r_umd])
                X = sm.add_constant(X1)
                y = DataFrame(data = r_dict)
                model = sm.OLS(y, X)
                results = model.fit()
                params = results.params
                resid = results.resid

            # 抽样过程，随机抽取和残差等数量的伪样本，代入公司中计算alpha

            alpha_set = []
            for i in range(10000):
                samples_resid = self.bootstrap(resid, len(resid))
                alpha_series = r_dict.values - np.array(params).T.dot(X1.values) -  samples_resid
                alpha = alpha_series.mean()
                alpha_set.append(alpha)
            # 计算alpha的t值 和 alpha的均值
            t_values = np.array(alpha_set).mean() / np.array(alpha_set).std()

            return t_values, np.array(alpha_set)



        def compute_return(self, df, factors):
            """

            :return:
            """
            labels = pd.qcut(df[factors].rank(method='first'), 10, labels=False)
            df['decile'] = labels
            df_high = df[df['decile'] == 7]
            df_low = df[df['decile'] == 3]

            r = df_high['ret'].mean() - df_low['ret'].mean()
            return r

        def bootstrap(self, data, num_samples):
            """

            :param num_samples:
            :return:
            """
            n = len(data)
            idx = np.random.randint(0, n, size=(num_samples, n))
            samples = data[idx]

            return samples






