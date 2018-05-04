"""


"""
import pykalman
import pandas as pd
import numpy as np
from pandas import DataFrame
class FactorStyle:
    """

    """
    def compute_style_return_month(self, df, factor):
        """
        计算当前日期向前推一个月的收益情况，该收益包括纯多头和多空收益两种。
        :param date: 日期
        :param df:  对应日期的因子数据，要包含每个股票当个月的收益数据,列名[factor, ret]
        :return:    因子组合月度收益率
        """
        if factor is None:
            return

        labels = pd.qcut(df[factor].rank(method='first'), 10, labels=False)
        df['decile'] = labels
        df_high = df[df['decile'] == 9]
        df_low = df[df['decile'] == 0]

        long_short_return = df_high['ret'].mean() - df_low['ret'].mean()
        long_only_return = df_high['ret'].mean()

        return long_only_return, long_short_return

    def performance_curve(self, df):
        """
        将收益率数据转化成累计收益曲线
        :param df:
        :return:
        """
        df = df.fillna(0)
        performance = 100 * np.cumprod(df + 1)
        return performance

    def kfilter(self, df):
        transition_matrices = 1
        observation_matrices = 1
        transition_covariance = None
        observation_covariance = None
        transition_offsets = None
        observation_offsets = None
        initial_state_mean = None
        initial_state_covariance = None
        random_state = None
        em_vars = ['transition_covariance',
                   'observation_covariance',
                   'initial_state_mean',
                   'initial_state_covariance']

        n_dim_state = None
        n_dim_obs = None
        kf = pykalman.KalmanFilter(transition_matrices,
                                   observation_matrices,
                                   transition_covariance,
                                   observation_covariance,
                                   transition_offsets,
                                   observation_offsets,
                                   initial_state_mean,
                                   initial_state_covariance,
                                   random_state,
                                   em_vars,
                                   n_dim_state,
                                   n_dim_obs)

        df_mu, df_sigma = kf.filter(df.values)

        return DataFrame(df_mu, index=df.index, columns=df.columns)

    def kpredict(self, performance_df):
        """

        :param performance_df:
        :return:
        """

        transition_matrices = np.array(1)
        observation_matrices = np.array(1)
        transition_covariance = None
        observation_covariance = None
        transition_offsets = None
        observation_offsets = None
        initial_state_mean = None
        initial_state_covariance = None
        random_state = None
        em_vars = ['transition_covariance',
                   'observation_covariance',
                   'initial_state_mean',
                   'initial_state_covariance']

        n_dim_state = None
        n_dim_obs = None
        kf = pykalman.KalmanFilter(transition_matrices,
                                   observation_matrices,
                                   transition_covariance,
                                   observation_covariance,
                                   transition_offsets,
                                   observation_offsets,
                                   initial_state_mean,
                                   initial_state_covariance,
                                   random_state,
                                   em_vars,
                                   n_dim_state,
                                   n_dim_obs)
        mu, sigma = kf.filter(performance_df.values)
        next_filtered_state_mean, next_filtered_state_covariance = kf.filter_update(mu[-1], sigma[-1],
                                                                                    performance_df.values[-1])

        return np.sign(next_filtered_state_mean - performance_df.values[-1])



