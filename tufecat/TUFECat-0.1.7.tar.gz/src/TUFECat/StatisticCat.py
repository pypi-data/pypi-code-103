# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 13:30:56 2021

@author: 11426
"""

from  scipy.stats import chi2_contingency
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame,Series
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
plt.rcParams['font.sans-serif'] = ['SimHei']#声明黑体解决中文乱码,这里有好几种方式，篇幅有限，一种就够了
plt.rcParams['axes.unicode_minus'] = False

def chi2_Contingency(list1=[],list2=[],alpha=0.05):
    kf_data = np.array([list1, list2])
    kf = chi2_contingency(kf_data)
    print('检验两个类别变量是否独立：原假设：事件1和事件2是相互独立的事件')
    print('检验结果：chisq-statistic=%.4f, p-value=%.4f, df=%i expected_frep=%s'%kf)
    if kf[1] >= alpha:
        print('原假设成立，事件1和事件2相互独立')
    else:
        print('拒绝原假设，事件1和事件2不相互独立')
        
def Multiple_linear_regression(data,x,y,train_size = 0.6):
    print('数据描述：')
    print('head:',data.head(),'\nShape:',data.shape)
    print(data.describe())
    print('缺失值检验：')
    print(data[data.isnull()==True].count())
    print('数据箱型图：')
    data.boxplot()
    plt.xlabel('指标')
    plt.ylabel('指标数值')
    print('数据线性相关性：')
    f,ax = plt.subplots(figsize = (10,5))
    sns.heatmap(data.corr(),annot = True)
    print('建模分析：')
    X_train,X_test,Y_train,Y_test = train_test_split(x,y,train_size=train_size)
    model = LinearRegression()
    model.fit(X_train,Y_train)
    a  = model.intercept_#截距
    b = model.coef_#回归系数
    print("最佳拟合线:截距",a,",回归系数：",b)
    score = model.score(X_test,Y_test)
    print("R方检测:",score)
    print('对线性回归进行预测：')
    Y_pred = model.predict(X_test)
    plt.figure(figsize=(10,5))
    plt.plot(range(len(Y_pred)),Y_pred,'b',label="predict",linestyle='-.',alpha=0.5)
    plt.plot(range(len(Y_pred)),Y_test,'r',label='test',linestyle='-',alpha=0.5)
    plt.legend()
    plt.xlabel("测试次序")
    plt.ylabel("预测值")
    #显示图像
    plt.show()