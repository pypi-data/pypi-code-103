from matplotlib import pyplot as plt
from ..lib import utils
class Plot(object):
    def __init__(self):
        utils.info('Initializing Plotting Object')

    """
    输入横轴行为column数据（例如股票symbol）纵轴为时间序列（例如日期index）返回plt对象
            策略A       上证指数
    7500    1.00112    1.00312 
    7501    1.00212    1.00412 
    
    """
    def plot_timeseries_data(self, dataframe):
        (dataframe / dataframe.iloc[0] * 100).plot(figsize=(10, 5))
        return plt
