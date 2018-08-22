"""
市场无效性场景的探测，主要有一下步骤：
1：单个股票，挖掘市场无效性的时段，将市场无效性时段前后的价量关系，基本面变化，提炼出来。
2：将股票出现市场无效性前后的收益率对指数和相关基本面价量关系变化因子进行回归，找到解释能力比较强的因子
3：提炼出因子，对因子进行样本外测试
"""


class MarketIneffectiveDetection:

    def __init__(self, stockcode, pct, window):
        """
        以周线，计算趋势的收益率，将连续10周的收益滚动计算，如果连续10周收益大于20%，定义为市场无效阶段
        :param stockcode:
        :param pct:
        :param window:
        """
        self.stock = stockcode
        self.pct = pct
        self.window = window

    def calculate_bias(self):
        """
        计算由于市场投资者偏见带来的收率偏差
        :return:
        """
        signs = "计算按照周的收益率，大于pct标准的计算为偏差"

        return signs

    def produce_factor(self):
        """
        根据signs前后的数据的变化（基本面，价量，预期数据）生成因子
        :return:
        """
        pass


    def attribute(self):
        """
        对超额收益进行归因分析，挖掘有效因子
        :return:
        """
        pass

