"""
研究出超额收益的因子后，下一步就是讲超额收益的因子转换成一个对应的组合，这类方法很多，可以在该脚本是任意扩展
"""
from FactorPrerprocess import neutralize_factor, get_alpha, calac_beta, forcast_alpha
from FactorStyleProcess import FactorStyle
import StockPool
import pandas as pd
import numpy as np

from pandas import DataFrame
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
                df = neutralize_factor(df, factors)
                alpha_hat = get_alpha(stockcodes, date, window)
                coef_ = calac_beta(alpha_hat, df, factors)
                df1 = neutralize_factor(df1, factors)
                alpha = forcast_alpha(coef_, df1, factors)
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
            pre_date = self.date - self.window  # 根据实际需要改写
            tradedays = [pre_date: date : "BM"] # 按月度生产交易日

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
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
            pre_date = self.date - self.window  # 根据实际需要改写
            tradedays = [pre_date: date : "BM"] # 按月度生产交易日

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
                    df = DataFrame(data = [f_data, f_ret], columns=[f.windLabel, 'ret'])
                    long_only, long_short = FactorStyle.compute_style_return_month(df, f.windLabel)
                    f_data.append(long_only)
                style_return[f.windLabel] = f_data
            style_weight = (style_return.median() - self.risk_free_rate) / style_return.var()
            k = style_weight / style_weight.sum().values
            return k

    class OptKelly:
        """
        学完凸优化再来搞
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
            pre_date = self.date - self.window  # 根据实际需要改写
            tradedays = [pre_date: date: "BM"]  # 按月度生产交易日

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
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
            pre_date = self.date - self.window  # 根据实际需要改写
            tradedays = [pre_date: date : "BM"] # 按月度生产交易日

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
                    df = DataFrame(data = [f_data, f_ret], columns=[f.windLabel, 'ret'])
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
            pre_date = self.date - self.window  # 根据实际需要改写
            tradedays = [pre_date: date : "BM"] # 按月度生产交易日

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = get_alpha(stockcodes, dt, -1) # 选取一个月的alpha
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
            pre_date = self.date - self.window  # 根据实际需要改写
            tradedays = [pre_date: date: "BM"]  # 按月度生产交易日

            # 提取因子数据
            style_return = DataFrame()
            for f in self.factors:
                f_data = []
                for dt in tradedays:
                    stockcodes = StockPool(dt).select_stock()
                    f_data = f(dt, stockcodes).getdata()
                    f_ret = get_alpha(stockcodes, dt, -1)  # 选取一个月的alpha
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


















