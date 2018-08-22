"""
研究出超额收益的因子后，下一步就是讲超额收益的因子转换成一个对应的组合，这类方法很多，可以在该脚本是任意扩展
"""
from WindPy import *
from .FactorPreprocess  import FactorProcess
from .FactorStyleProcess import FactorStyle
from .StockPool import StockPool
import pandas as pd
import numpy as np
from math import sqrt
from cvxopt import matrix
from cvxopt.blas import dot
from cvxopt.solvers import qp
import pylab
from cvxpy import *

from pandas import DataFrame
w.start()
class PortfolioManagement:
    """

    """
    class EvolutionaryModel:
        """
            进化模型是基于前一段时间因子归因分析的结果，对下一段时间组合因子进行超配或低配，这样组合的因子能够跟随市场风格
            不断的进化
        """
        def __init__(self, stockcodes, df, df1, date, factors, window, Neutral=False):
            if not Neutral:
                print("先进行因子中性化处理")
            self.stockcodes = stockcodes
            self.df = df
            self.df1 = df1
            self.date = date
            self.factors = factors
            self.window = window
            self.Neutral = Neutral

        def evolute_factors(self):
            """

            :return:
            """
            stockcodes = self.stockcodes
            df = self.df
            df1 = self.df1
            date = self.date
            window = self.window
            factors = self.factors
            if not self.Neutral:
                df = FactorProcess.neutralize_factor(df, factors)
                alpha_hat = FactorProcess.get_alpha(stockcodes, date, window)
                coef_ = FactorProcess.calac_beta(alpha_hat, df, factors)
                df1 = FactorProcess.neutralize_factor(df1, factors)
                alpha = FactorProcess.forcast_alpha(coef_, df1, factors)
            df1['Alpha'] = alpha
            stock = df1.sort_values(['Alpha'], ascending=False).head(50)

            return stock

    class FractionalKelly:
        """

        """
        def __init__(self, date, window, factors):

            self.date = date
            self.window = window
            self.factors = factors

        def construct_portfolio(self):
            """
            根据每个因子的风格收益，来配置不同的权重，核心是根据凯利公司法则
            :return: 返回基于kelly公式计算的每个因子的权重
            """

            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
                    df = DataFrame(data = [f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_weight = style_return.mean() / style_return.var()
            k = style_weight / style_weight.sum().values
            return k

    class MedianKelly:
        """

        """
        def __init__(self, date, window, factors, risk_free_rate):

            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """
            根据每个因子的风格收益，来配置不同的权重，核心是根据凯利公司法则
            :return: 返回基于kelly公式计算的每个因子的权重
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_weight = (style_return.median() - self.risk_free_rate) / style_return.var()
            k = style_weight / style_weight.sum().values
            return k

    class OptKelly:
        """
        最优凯利
        """
        pass

    class KfilterKelly:
        """

        """
        def __init__(self, date, window, factors, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """
            根据风格因子的收益和kf预测的结果，计算不同风格的权重
            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data

            performance = FactorStyle.performance_curve(style_return)
            sign = FactorStyle.kpredict(performance)
            sign1 = np.where(sign==1, sign, 0)
            style_weight = (style_return.mean() - self.risk_free_rate) / style_return.var()
            k = style_weight / style_weight.sum().values
            weight = DataFrame(data=k.values * sign1, columns=k.columns)

            return weight

    class SmaFractionalKelly:
        """

        """
        def __init__(self, date, window, factors):

            self.date = date
            self.window = window
            self.factors = factors

        def construct_portfolio(self):
            """
            根据每个因子的风格收益，来配置不同的权重，核心是根据凯利公司法则
            :return: 返回基于kelly公式计算的每个因子的权重
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_weight = style_return.mean() / style_return.var()
            k = style_weight / style_weight.sum().values
            performance = FactorStyle.performance_curve(style_return)
            sign = np.sign(performance.values[-1] - performance.mean())
            sign1 = np.where(sign==1,sign, 0)
            weight = DataFrame(data=k.values * sign1, columns=k.columns)
            return weight

    class SmaMedianKelly:
        """

        """
        def __init__(self, date, window, factors):

            self.date = date
            self.window = window
            self.factors = factors

        def construct_portfolio(self):
            """
            根据每个因子的风格收益，来配置不同的权重，核心是根据凯利公司法则
            :return: 返回基于kelly公式计算的每个因子的权重
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
                    df = DataFrame(data = [f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_weight = style_return.median() / style_return.var()
            k = style_weight / style_weight.sum().values
            performance = FactorStyle.performance_curve(style_return)
            sign = np.sign(performance.values[-1] - performance.mean())
            sign1 = np.where(sign==1,sign, 0)
            weight = DataFrame(data=k.values * sign1, columns=k.columns)
            return weight

    class KfilterMedianKelly:
        """

        """
        def __init__(self, date, window, factors, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """
            根据风格因子的收益和kf预测的结果，计算不同风格的权重
            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]
            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data

            performance = FactorStyle.performance_curve(style_return)
            sign = FactorStyle.kpredict(performance)
            sign1 = np.where(sign==1, sign, 0)
            style_weight = (style_return.median() - self.risk_free_rate) / style_return.var()
            k = style_weight / style_weight.sum().values
            weight = DataFrame(data=k.values * sign1, columns=k.columns)

            return weight

    class EqualWeightPortfolio:
        def __init__(self, factors):
            self.factors = factors

        def weight(self):

            wt = 1/len(self.factors)
            weight_hat = np.full(len(self.factors), wt)
            return weight_hat

    class MaximumDiversificationPortfolio:
        def __init__(self, date, window, factors, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """

            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]
            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            S = matrix(style_return.cov().values)
            pbar = matrix(style_return.std().values)
            n = len(self.factors)
            G = matrix(0.0, (n, n))
            G[::n + 1] = -1.0
            h = matrix(0.0, (n, 1))
            A = matrix(1.0, (1, n))
            b = matrix(1.0)
            portfolio_weight = qp(S, -pbar, G, h, A, b)['x']

            return portfolio_weight

    class MinimumVariancePortfolio:
        def __init__(self, date, window, factors, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """

            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]
            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            S = matrix(style_return.cov().values)
            pbar = matrix(np.zeros_like(style_return.std().values))
            n = len(self.factors)
            G = matrix(0.0, (n, n))
            G[::n + 1] = -1.0
            h = matrix(0.0, (n, 1))
            A = matrix(1.0, (1, n))
            b = matrix(1.0)
            portfolio_weight = qp(S, -pbar, G, h, A, b)['x']

    class EqualRiskContributionPortfolio:
        def __init__(self, date, window, factors, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """

            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]
            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            S = style_return.cov().values
            n = len(self.factors)
            Sigma = S.T.dot(S)
            weight = Variable(n)
            gamma = Parameter(sign="positive")
            risk = quad_form(weight, Sigma)
            prob = Problem(Maximize(-gamma * risk),
                           [sum_entries(weight) == 1,
                           weight >= 0])
            gamma.value = 1
            prob.solve()
            Weight = weight.value / np.sum(weight.value)
            return Weight

    class InverseVolatilityPortfolio:
        def __init__(self, date, window, factors, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """

            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]
            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_sigma = style_return.std()
            weight = (1/style_sigma) / np.sum(1/style_sigma)
            return weight

    class MaximumSharpeRatioPortfolio:
        pass

    class VolatilityWeightingOverTime:
        def __init__(self, date, window, factors, target, risk_free_rate):
            self.date = date
            self.window = window
            self.factors = factors
            self.target = target
            self.risk_free_rate = risk_free_rate

        def construct_portfolio(self):
            """

            :return:
            """
            pre_date_data = w.tdaysoffset(-self.window, self.date, "Period=M")
            pre_date = pre_date_data.Data[0][0].strftime("%Y-%m-%d")
            tradedays_data = w.tdays(pre_date, self.date, "Period=M")
            tradedayslist = tradedays_data[0]
            tradedays = [td.strftime("%Y-%m-%d") for td in tradedayslist]
            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = FactorProcess.get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
                    df = DataFrame(data=[f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_sigma = style_return.std()
            weight = style_sigma / self.target
            weight[weight > 1] = 1
            weight = weight / len(self.factors)

            return weight






















