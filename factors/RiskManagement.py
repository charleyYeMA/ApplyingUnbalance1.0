"""
本脚本为风控模块，包括一系列风控的方法
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
from scipy.stats import norm, t
from scipy.stats import skew, kurtosis, kurtosistest


class RiskManagement:
    def __init__(self):

        pass

    def control_maximum_drawdown(self, shape_raion_hat, drawdown_para, window, df, rf = 0.03, sigma=None):
        """
        控制最大回撤下，组合应该具有的最大权重
        :param shape_raion_hat:  风险资产预估的夏普比率
        :param drawdown_para:  最大回撤到的净值（0-1）
        :param window:   滚动时间窗口
        :param df:       组合净值数据
        :param sigma:   风险资产波动率水平
        :return:    组合仓位和无风险资产仓位
        """
        WT = []
        if len(df) < window:
            for i in range(len(df)):
                Wt = df.iloc[i] + (len(df) - i - 1) * 0.03 / 242
                WT.append(Wt)
        else:
            for i in range(window):
                Wt = df.iloc[-window+i] + (window - i - 1) * 0.03 / 242
                WT.append(Wt)
        REM = max(WT)
        REDD = 1 - WT[-1]/REM

        weight_risk = max(0, (shape_raion_hat/sigma + 1/2)/(1 - np.power(drawdown_para, 2)) * (drawdown_para - REDD)/
                          (1 - REDD))
        risk_free_weight = 1 - weight_risk

        return weight_risk, risk_free_weight

    def maxdrowdown(self, df):
        """
        计算当前组合的最大回撤
        :param df:
        :return:
        """

        return df / df.cummax() - 1

    def plot_mdd(self, mdd_df):
        """
        根据历史最大回测观察最大回撤所处的区间
        :param mdd_df:
        :return:
        """

        mdd_df = mdd_df.fillna(0)
        mdd_df = mdd_df['Port']
        mu = mdd_df.mean()
        sigma = mdd_df.std()
        x = mdd_df
        pdf = np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))

        plt.scatter(x, pdf, color='g', linewidth=3)
        plt.hist(mdd_df, bins=15, color='r', alpha=0.5, rwidth=0.9, normed=True)
        plt.title('MDD distribution')
        plt.xlabel('MDD score')
        plt.ylabel('Probability')
        plt.show()

    def calculate_VaR(self, df):
        """

        :param df:  array, 组合净值数据
        :return:
        """
        # N(x; mu, sig) best fit (finding: mu, stdev)
        mu_norm, sig_norm = norm.fit(df)
        dx = 0.0001
        x = np.arange(-0.1, 0.1, dx)
        pdf = norm.pdf(x, mu_norm, sig_norm)
        print("Sample mean  = %.5f" % mu_norm)
        print("Sample stdev = %.5f" % sig_norm)
        print()

        # Student t best fit (finding: nu)
        parm = t.fit(df)
        nu, mu_t, sig_t = parm
        nu = np.round(nu)
        pdf2 = t.pdf(x, nu, mu_t, sig_t)
        print("nu = %.2f" % nu)
        print()

        # Compute VaRs and CVaRs

        h = 1
        alpha = 0.01  # significance level
        lev = 100 * (1 - alpha)
        xanu = t.ppf(alpha, nu)

        CVaR_n = alpha ** -1 * norm.pdf(norm.ppf(alpha)) * sig_norm - mu_norm
        VaR_n = norm.ppf(1 - alpha) * sig_norm - mu_norm

        VaR_t = np.sqrt((nu - 2) / nu) * t.ppf(1 - alpha, nu) * sig_norm - h * mu_norm
        CVaR_t = -1 / alpha * (1 - nu) ** (-1) * (nu - 2 + xanu ** 2) * \
                 t.pdf(xanu, nu) * sig_norm - h * mu_norm

        print("%g%% %g-day Normal VaR     = %.2f%%" % (lev, h, VaR_n * 100))
        print("%g%% %g-day Normal t CVaR  = %.2f%%" % (lev, h, CVaR_n * 100))
        print("%g%% %g-day Student t VaR  = %.2f%%" % (lev, h, VaR_t * 100))
        print("%g%% %g-day Student t CVaR = %.2f%%" % (lev, h, CVaR_t * 100))

        plt.figure(num=1, figsize=(11, 6))
        grey = .77, .77, .77
        # main figure
        plt.hist(df, bins=50, normed=True, color=grey, edgecolor='none')
        plt.hold(True)
        plt.axis("tight")
        plt.plot(x, pdf, 'b', label="Normal PDF fit")
        plt.hold(True)
        plt.axis("tight")
        plt.plot(x, pdf2, 'g', label="Student t PDF fit")
        plt.xlim([-0.2, 0.1])
        plt.ylim([0, 50])
        plt.legend(loc="best")
        plt.xlabel("Daily Returns of Port")
        plt.ylabel("Normalised Return Distribution")
        # inset
        a = plt.axes([.22, .35, .3, .4])
        plt.hist(df, bins=50, normed=True, color=grey, edgecolor='none')
        plt.hold(True)
        plt.plot(x, pdf, 'b')
        plt.hold(True)
        plt.plot(x, pdf2, 'g')
        plt.hold(True)
        # Student VaR line
        plt.plot([-CVaR_t, -CVaR_t], [0, 3], c='r')
        # Normal VaR line
        plt.plot([-CVaR_n, -CVaR_n], [0, 4], c='b')
        plt.text(-CVaR_n - 0.015, 4.1, "Norm CVaR", color='b')
        plt.text(-CVaR_t - 0.0171, 3.1, "Student t CVaR", color='r')
        plt.xlim([-0.09, -0.02])
        plt.ylim([0, 5])
        plt.show()


