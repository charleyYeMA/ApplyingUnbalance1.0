from factors.FactorTest import FactorTest
from factors.FactorsZoo import FactorsZoo
from factors.StockPool import StockPool
from WindPy import *
from pandas import DataFrame
import numpy as np
import pandas as pd
import statsmodels.api as sm
w.start()

# 选择需要测试的因子
starttime = '2014-02-01'
endtime = '2017-12-31'

# 生成月度数据
dateseries = w.tdays(starttime, endtime, "Period=M")
hml_list = []
hml_ind_list = []
hml_biv_list = []
hml_ind_biv_list = []
for ds in dateseries.Data[0]:
    date = ds.strftime("%Y-%m-%d")
    stock = StockPool(date).select_stock()
    factor = FactorsZoo.Dividend(date, stock, "dividend").get_data()
    df = DataFrame()
    df['factor'] = factor
    date1 = w.tdaysoffset(1, date, "Period=M")
    date1 = date1.Data[0][0].strftime("%Y-%m-%d")
    ret = FactorsZoo.Pct(date1, stock, "ret", -1).get_data()
    df['ret'] = ret
    # 获取基础因子数据 ['SIZE','industry']作为控制变量
    size = FactorsZoo.Size(date, stock, "SIZE").get_data()
    industry = FactorsZoo.Industry(date, stock, "industry").get_data()

    df['SIZE'] = size
    df['industry'] = industry
    # 因子行业中性处理
    x = pd.get_dummies(df['inustry'])
    x = sm.add_constant(x)
    y = df['factor']
    model = sm.OLS(y, x)
    results = model.fit()

    hml = FactorTest.UnbivariateSorts(df, 'factor').unbivariate_sorts()
    hml_list.append(hml)

    hml_biv = FactorTest.BivariateSorts(df, factor='factor', control='SIZE').bivariate_sorts()
    hml_biv_list.append(hml_biv)

    df['factor'] = results.resid

    hml_ind = FactorTest.UnbivariateSorts(df, 'factor').unbivariate_sorts()
    hml_ind_list.append(hml_ind)
    hml_ind_biv = FactorTest.BivariateSorts(df, 'factor', 'SIZE').bivariate_sorts()
    hml_ind_biv_list.append(hml_ind_biv)


t_stats_unbi = np.array(hml_list).mean() / np.array(hml_list).std()
t_stats_bi = np.array(hml_biv_list).mean() / np.array(hml_biv_list).std()

t_stats_ind_unbi = np.array(hml_ind_list).mean() / np.array(hml_ind_list)
t_stats_ind_bi = np.array(hml_ind_biv_list).mean() / np.array(hml_ind_biv_list)







