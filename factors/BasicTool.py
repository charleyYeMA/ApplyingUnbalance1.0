"""

"""


class Factor(object):
    """

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
            self.stockCodes = stockcodes
            self.windLabel = label

    def getdata(self):

        pass
