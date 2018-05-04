"""
保存一些基础的类，用于后面的继承使用
"""


class Factor(object):
    """
    因子：收益的来源，用于计算一个资产类别对应的因子数值
    """
    def __init__(self, date, stockcodes, label):
        """

        """
        if not isinstance(date, str):
            print("日期格式不对")
        elif not isinstance(stockcodes, list):
            print("代码格式不对")
        else:
            self.date = date
            self.stockcodes = stockcodes
            self.windLabel = label

    def get_data(self):

        pass



