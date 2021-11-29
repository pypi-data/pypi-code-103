# -*- coding: utf-8 -*-

from fbprophet import Prophet
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from fbprophet.plot import add_changepoints_to_plot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima_model import ARIMA 
import warnings
warnings.filterwarnings(action = 'ignore')#忽略代码运行过程中的警告信息

def Forecast_Time_Serise(df,freq='1d',periods=30):
    df.columns = ['ds','y']
    df['ds'] = pd.to_datetime(df['ds'])
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=periods, freq=freq)
    future.tail()
    forecast = m.predict(future)
    fig = m.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), m, forecast)
    x1 = forecast['ds']
    y1 = forecast['yhat']
    y2 = forecast['yhat_lower']
    y3 = forecast['yhat_upper']
    plt.plot(x1,y1)
    plt.plot(x1,y2)
    plt.plot(x1,y3)
    plt.show()
    m.plot_components(forecast)
    print('所有预测结果为：\n',forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
    print('最后五个预测结果为：\n',forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
    

def ARIMA_Prefare(data,n):   
    plt.rcParams['font.sans-serif'] = ['SimHei']    #定义使其正常显示中文字体黑体
    plt.rcParams['axes.unicode_minus'] = False      #用来正常显示表示负号
    print('数据概览：')
    plt.plot(data)
    plt.show()
    print('自相关性图：')
    #画出自相关性图
    plot_acf(data)
    plt.show()
    #平稳性检测
    print('原始序列的平稳性检验结果为：',adfuller(data.iloc[:,0:1]))
    print('返回值依次为：adf, pvalue p值， usedlag, nobs, critical values临界值 , icbest, regresults, resstore')
    print('若adf分别大于3中不同检验水平的3个临界值，单位检测统计量对应的p值显著大于 0.05 ，说明序列可以判定为非平稳序列')
    #对数据进行差分后得到 自相关图和 偏相关图
    D_data = data.diff().dropna()
    print('差分后的时序图：')
    fig = plt.figure(figsize=(6.5,4.5))
    plt.plot(D_data)   #画出差分后的时序图
    plt.show()
    print('差分后的自相关图：')
    plot_acf(D_data)    #画出自相关图
    plt.show()
    print('差分后的偏相关图：')
    plot_pacf(D_data)   #画出偏相关图
    plt.show()
    print(u'差分序列的ADF 检验结果为： ', adfuller(D_data.iloc[:,0:1]))   #平稳性检验
    print('一阶差分后的序列的时序图在均值附近比较稳的波动， 自相关性有很强的短期相关性， 单位根检验 p值小于 0.05 ，所以说一阶差分后的序列是平稳序列')
    print(u'差分序列的白噪声检验结果（第二项为p值）：',acorr_ljungbox(D_data, lags= 1))


def ARIMA_Model(data,pmax,qmax,n):
    bic_matrix = []
    for p in range(pmax +1):
        temp= []
        for q in range(qmax+1):
            try:
                temp.append(ARIMA(data.iloc[:,0:1], (p, 1, q)).fit().bic)
            except:
                temp.append(None)
            bic_matrix.append(temp)

    bic_matrix = pd.DataFrame(bic_matrix)   #将其转换成Dataframe 数据结构
    p,q = bic_matrix.stack().idxmin()   #先使用stack 展*， 然后使用 idxmin 找出最小值的位置
    print(u'BIC 最小的p值 和 q 值：%s,%s' %(p,q))  #  BIC 最小的p值 和 q 值：0,1
    #所以可以建立ARIMA 模型，ARIMA(0,1,1)
    model = ARIMA(data, (p,1,q)).fit()
    print('模型报告：')
    model.summary2()        #生成一份模型报告
    print(f'为未来{n}天进行预测，返回预测结果，标准误差和置信区间：')
    model.forecast(n)   #为未来5天进行预测， 返回预测结果， 标准误差， 和置信区间
