# -*- coding: utf-8 -*-
"""
本模块功能：证券投资组合理论计算函数包
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年7月1日
最新修订日期：2020年7月29日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#统一屏蔽一般性警告
import warnings; warnings.filterwarnings("ignore")   
#==============================================================================
  
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.fama_french import *

import pandas as pd
import datetime
#==============================================================================
import matplotlib.pyplot as plt

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
#==============================================================================
def portfolio_config(tickerlist,sharelist):
    """
    将股票列表tickerlist和份额列表sharelist合成为一个字典
    """
    #整理sharelist的小数点
    ratiolist=[]
    for s in sharelist:
        ss=round(s,4); ratiolist=ratiolist+[ss]
    #合成字典
    new_dict=dict(zip(tickerlist,ratiolist))
    return new_dict

#==============================================================================
def ratiolist_round(sharelist,num=4):
    """
    将股票份额列表sharelist中的数值四舍五入
    """
    #整理sharelist的小数点
    ratiolist=[]
    for s in sharelist:
        ss=round(s,num); ratiolist=ratiolist+[ss]
    return ratiolist

#==============================================================================
def varname(p):
    """
    功能：获得变量的名字本身。
    """
    import inspect
    import re    
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)    

#==============================================================================
def get_start_date(end_date,pastyears=1):
    """
    输入参数：一个日期，年数
    输出参数：几年前的日期
    start_date, end_date是datetime类型
    """
    import pandas as pd
    try:
        end_date=pd.to_datetime(end_date)
    except:
        print("  #Error(get_start_date): invalid date,",end_date)
        return None
    
    from datetime import datetime,timedelta
    start_date=datetime(end_date.year-pastyears,end_date.month,end_date.day)
    start_date=start_date-timedelta(days=1)
    # 日期-1是为了保证计算收益率时得到足够的样本数量
    return start_date

#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    retgroup=StockReturns

def cumulative_returns_plot(retgroup,name_list="",titletxt="投资组合策略：业绩比较", \
                            ylabeltxt="持有收益率",xlabeltxt="", \
                            label_list=[]):
    """
    功能：基于传入的name_list绘制多条持有收益率曲线，并从label_list中取出曲线标记
    注意：最多绘制四条曲线，否则在黑白印刷时无法区分曲线，以此标记为实线、点虚线、划虚线和点划虚线四种
    """
    if name_list=="":
        name_list=list(retgroup)
    
    if len(label_list) < len(name_list):
        label_list=name_list
    
    if xlabeltxt=="":
        #取出观察期
        hstart0=retgroup.index[0]; hstart=str(hstart0.date())
        hend0=retgroup.index[-1]; hend=str(hend0.date())
    
        footnote1="观察期间: "+hstart+'至'+hend
        import datetime as dt; stoday=dt.date.today()    
        footnote2="\n数据来源：新浪/EM/stooq，"+str(stoday)
        xlabeltxt=footnote1+footnote2
    
    # 持有收益曲线绘制函数
    lslist=['-','--',':','-.']
    markerlist=['.','h','+','x','4','3','2','1']
    for name in name_list:
        pos=name_list.index(name)
        rlabel=label_list[pos]
        if pos < len(lslist): 
            thisls=lslist[pos]        
        else: 
            thisls=(45,(55,20))
        
        # 计算持有收益率
        CumulativeReturns = ((1+retgroup[name]).cumprod()-1)
        if pos-len(lslist) < 0:
            CumulativeReturns.plot(label=ectranslate(rlabel),ls=thisls)
        else:
            thismarker=markerlist[pos-len(lslist)]
            CumulativeReturns.plot(label=ectranslate(rlabel),ls=thisls,marker=thismarker,markersize=4)
            
    #plt.axhline(y=0,ls=":",c="red")
    plt.legend(loc='best')
    plt.title(titletxt); plt.ylabel(ylabeltxt); plt.xlabel(xlabeltxt)
    plt.show()
    
    return

if __name__=='__main__':
    retgroup=StockReturns
    cumulative_returns_plot(retgroup,name_list,titletxt,ylabeltxt,xlabeltxt, \
                            label_list=[])

def portfolio_expret_plot(retgroup,name_list="",titletxt="投资组合策略：业绩比较", \
                            ylabeltxt="持有收益率",xlabeltxt="", \
                            label_list=[]):
    """
    功能：套壳函数cumulative_returns_plot
    """
    
    cumulative_returns_plot(retgroup,name_list,titletxt,ylabeltxt,xlabeltxt,label_list) 
    
    return

#==============================================================================
if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.3,'MSFT':.15,'AMZN':.15,'FB':.01,'GOOG':.01}
    Stocks2={'XOM':.02,'JNJ':.02,'JPM':.01,'TSLA':.3,'SBUX':.03}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    thedate='2019-12-31'
    pastyears=1
    rate_period='1Y'
    rate_type='treasury'
    printout=True    

def portfolio_cumret(portfolio,thedate,pastyears=1, \
                     rate_period='1Y',rate_type='shibor',printout=True):
    """
    功能：绘制投资组合的累计收益率趋势图，并与等权和市值加权组合比较
    """
    print("\n  Searching for portfolio info, which may take time ...")
    # 解构投资组合
    scope,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)

    totalshares=round(sum(sharelist),4)
    if totalshares != 1.0:
        print("\n  #Error(portfolio_cumret): total weights is",totalshares,", it requires 1.0 here")
        return None       

    #..........................................................................    
    # 计算历史数据的开始日期
    start=get_start_date(thedate,pastyears)
    
    #一次性获得无风险利率，传递给后续函数，避免后续每次获取，耗费时间    
    rf_df=get_rf_daily(start,thedate,scope,rate_period,rate_type)
    #结果字段中，RF是日利率百分比，rf_daily是日利率数值
    if rf_df is None:
        #print("  #Error(portfolio_cumret): failed to retrieve risk-free interest rate in",scope)
        print("  Warning: all subsequent portfolio optimizations cannot proceed")
        print("  Solution: try again until success")
        return None

    #..........................................................................    
    # 抓取投资组合股价
    prices=get_prices(tickerlist,start,thedate)
    if prices is None:
        print("  #Error(portfolio_cumret): failed to get portfolio prices",pname)
        return None
    if len(prices) == 0:
        print("  #Error(portfolio_cumret): retrieved empty prices for",pname)
        return None
    #..........................................................................
    
    # 取各个成分股的收盘价
    aclose=prices['Close']    
    # 计算各个成分股的日收益率，并丢弃缺失值
    StockReturns = aclose.pct_change().dropna()
    if len(StockReturns) == 0:
        print("\n  #Error(portfolio_cumret): retrieved empty returns for",pname)
        return None
    
    # 保存各个成分股的收益率数据，为了后续调用的方便
    stock_return = StockReturns.copy()
    
    # 将原投资组合的权重存储为numpy数组类型，为了合成投资组合计算方便
    import numpy as np
    portfolio_weights = np.array(sharelist)
    # 合成portfolio的日收益率
    WeightedReturns = stock_return.mul(portfolio_weights, axis=1)
    # 原投资组合的收益率
    StockReturns['Portfolio'] = WeightedReturns.sum(axis=1)
    #..........................................................................
    
    # 绘制原投资组合的收益率曲线，以便使用收益率%来显示
    plotsr = StockReturns['Portfolio']
    plotsr.plot(label=pname)
    plt.axhline(y=0,ls=":",c="red")
    
    plt.title("投资组合: 日收益率的变化趋势")
    plt.ylabel("日收益率")
    
    stoday = datetime.date.today()
    plt.xlabel("数据来源: 新浪/stooq/FRED, "+str(stoday))
    plt.legend()
    plt.show()
    #..........................................................................
    
    # 计算原投资组合的持有收益率，并绘图
    name_list=["Portfolio"]
    label_list=[pname]
    titletxt="投资组合: 持有收益率的变化趋势"
    ylabeltxt="持有收益率"
    stoday = datetime.date.today()
    xlabeltxt="数据来源: 新浪/stooq/FRED, "+str(stoday)
    
    #绘制持有收益率曲线
    cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)
    #..........................................................................
    
    # 构造等权重组合Portfolio_EW的持有收益率
    numstocks = len(tickerlist)
    # 平均分配每一项的权重
    portfolio_weights_ew = np.repeat(1/numstocks, numstocks)
    # 合成等权重组合的收益，按行横向加总
    StockReturns['Portfolio_EW']=stock_return.mul(portfolio_weights_ew,axis=1).sum(axis=1)
    #..........................................................................
    
    # 创建流动性组合：按照成交金额计算流动性
    tamount=prices['Close']*prices['Volume']
    tamountlist=tamount.mean(axis=0)    #求列的均值
    tamountlist_array = np.array(tamountlist)
    # 计算成交金额权重
    portfolio_weights_lw = tamountlist_array / np.sum(tamountlist_array)
    # 计算成交金额加权的组合收益
    StockReturns['Portfolio_LW'] = stock_return.mul(portfolio_weights_lw, axis=1).sum(axis=1)

    #绘制累计收益率对比曲线
    name_list=['Portfolio', 'Portfolio_EW', 'Portfolio_LW']
    label_list=[pname, '等权重组合', '流动性组合']
    titletxt="投资组合策略：业绩对比"
    
    #绘制各个投资组合的持有收益率曲线
    cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)

    #打印各个投资组合的持股比例
    member_returns=stock_return
    if printout:
        portfolio_expectation2(pname,member_returns,portfolio_weights)
        portfolio_expectation2('等权重组合',member_returns,portfolio_weights_ew)
        portfolio_expectation2('流动性组合',member_returns,portfolio_weights_lw)

    #返回投资组合的综合信息
    member_returns=stock_return
    portfolio_returns=StockReturns[name_list]
    
    #投资组合名称改名
    pelist=['Portfolio','Portfolio_EW','Portfolio_LW','Portfolio_MSR','Portfolio_GMV', \
           'Portfolio_MSO','Portfolio_GML','Portfolio_MAR','Portfolio_GMB', \
            'Portfolio_MTR','Portfolio_GMB2']
    pclist=[pname,'等权重组合','流动性组合','MSR组合','GMV组合','MSO组合','GML组合', \
            'MAR组合','GMB组合', 'MTR组合','GMB2组合']
    pecols=list(portfolio_returns)
    for p in pecols:
        ppos=pelist.index(p)
        pc=pclist[ppos]
        portfolio_returns.rename(columns={p:pc},inplace=True)
    
    return [[portfolio,thedate,member_returns,rf_df], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]]

if __name__=='__main__':
    X=portfolio_cumret(portfolio,'2021-9-30')

if __name__=='__main__':
    pf_info=portfolio_cumret(portfolio,'2021-9-30')

#==============================================================================

def portfolio_expret(portfolio,today,pastyears=1):
    """
    功能：绘制投资组合的持有期收益率趋势图，并与等权和市值加权组合比较
    套壳原来的portfolio_cumret函数，以维持兼容性
    expret: expanding return，以维持与前述章节名词的一致性
    hpr: holding period return, 持有（期）收益率
    """
    #处理失败的返回值
    results=portfolio_cumret(portfolio,today,pastyears)
    if results is None: return None
    
    [[portfolio,thedate,member_returns,rf_df], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]] = results

    return [[portfolio,thedate,member_returns,rf_df], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]]

if __name__=='__main__':
    pf_info=portfolio_expret(portfolio,'2021-9-30')

#==============================================================================
def portfolio_corr(pf_info):
    """
    功能：绘制投资组合成分股之间相关关系的热力图
    """
    [[portfolio,thedate,stock_return,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.date())
    hend0=stock_return.index[-1]; hend=str(hend0.date())
        
    sr=stock_return.copy()
    collist=list(sr)
    for col in collist:
        sr.rename(columns={col:codetranslate(col)},inplace=True)

    # 计算相关矩阵
    correlation_matrix = sr.corr()
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(correlation_matrix,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 8})
    plt.title(pname+": 成分股收益率之间的相关系数")
    plt.ylabel("成分股票")
    
    footnote1="观察期间: "+hstart+'至'+hend
    import datetime as dt; stoday=dt.date.today()    
    footnote2="\n数据来源：新浪/EM/stooq，"+str(stoday)
    plt.xlabel(footnote1+footnote2)
    plt.xticks(rotation=90); plt.yticks(rotation=0) 
    plt.show()

    return    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_corr(pf_info)
#==============================================================================
def portfolio_covar(pf_info):
    """
    功能：计算投资组合成分股之间的协方差
    """
    [[portfolio,thedate,stock_return,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.date())
    hend0=stock_return.index[-1]; hend=str(hend0.date())

    # 计算协方差矩阵
    cov_mat = stock_return.cov()
    # 年化协方差矩阵，252个交易日
    cov_mat_annual = cov_mat * 252
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(cov_mat_annual,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 8})
    plt.title(pname+": 成分股之间的协方差")
    plt.ylabel("成分股票")
    
    footnote1="观察期间: "+hstart+'至'+hend
    import datetime as dt; stoday=dt.date.today()    
    footnote2="\n数据来源：新浪/EM/stooq，"+str(stoday)
    plt.xlabel(footnote1+footnote2)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0) 
    plt.show()

    return 

#==============================================================================
def portfolio_expectation(pf_info):
    """
    功能：计算原始投资组合的年均收益率和标准差
    输入：pf_info
    输出：年化收益率和标准差
    """
    [[portfolio,thedate,_,_],[portfolio_returns,portfolio_weights,_,_]]=pf_info
    pname=portfolio_name(portfolio)
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=portfolio_returns.index[0]; hstart=str(hstart0.date())
    hend0=portfolio_returns.index[-1]; hend=str(hend0.date())

    #年均收益率
    mean_return=portfolio_returns['Portfolio'].mean(axis=0)
    annual_return = (1 + mean_return)**252 - 1
    
    #年均标准差
    std_return=portfolio_returns['Portfolio'].std(axis=0)
    import numpy as np
    annual_std = std_return*np.sqrt(252)
    
    print("\n  ======= 投资组合的收益与风险 =======\n")
    print("  投资组合:",pname)
    print("  数据日期:",str(thedate))
    print("  观察期间:",hstart+'至'+hend)
    print("  年化收益率:",round(annual_return,4))
    print("  年化标准差:",round(annual_std,4))
    print("\n  ***投资组合构造:")
    print_tickerlist_sharelist(tickerlist,sharelist,4)
    
    import datetime as dt; stoday=dt.date.today()    
    print("  *数据来源：新浪/EM/stooq，"+str(stoday))

    return 

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_expectation(pf_info)

#==============================================================================
def portfolio_expectation2(pname,member_returns,portfolio_weights):
    """
    功能：计算原始投资组合的年均收益率和标准差
    输入：投资组合名称，观察期的开始、结束日期，成分股历史收益率df，投资组合权重series
    输出：年化收益率和标准差
    用途：求出MSR、GMV等持仓策略后计算投资组合的年化收益率和标准差
    """
    #观察期
    hstart0=member_returns.index[0]; hstart=str(hstart0.date())
    hend0=member_returns.index[-1]; hend=str(hend0.date())
    tickerlist=list(member_returns)

    #合成投资组合的历史收益率，按行横向加权求和
    preturns=member_returns.copy() #避免改变输入的数据
    preturns['Portfolio']=preturns.mul(portfolio_weights,axis=1).sum(axis=1)

    #计算年化收益率：按列求均值
    mean_return=preturns['Portfolio'].mean(axis=0)
    annual_return = (1 + mean_return)**252 - 1
    
    #计算年化标准差
    std_return=preturns['Portfolio'].std(axis=0)
    import numpy as np
    annual_std = std_return*np.sqrt(252)
    
    print("\n  ======= 投资组合的收益与风险 =======")
    print("  投资组合:",pname)
    print("  数据日期:",str(hend))
    print("  观察期间:",hstart+'至'+hend)
    print("  年化收益率:",round(annual_return,4))
    print("  年化标准差:",round(annual_std,4))
    print("\n  ***投资组合构造:")
    print_tickerlist_sharelist(tickerlist,portfolio_weights,4)
   
    import datetime as dt; stoday=dt.date.today()    
    print("  *数据来源：新浪/EM/stooq，"+str(stoday))

    return 

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')

    [[portfolio,thedate,member_returns],[_,portfolio_weights,_,_]]=pf_info
    pname=portfolio_name(portfolio)
    
    portfolio_expectation2(pname,member_returns, portfolio_weights)

def portfolio_ranks(portfolio_returns):
    """
    功能：打印现有投资组合的收益率、标准差排名，收益率降序，标准差升序
    """
    #临时保存，避免影响原值
    pr=portfolio_returns.copy()
    
    import pandas as pd  
    import numpy as np
    prr=pd.DataFrame(columns=["名称","年化收益率","年化标准差"])    
    cols=list(pr)
    for c in cols:
        #计算年化收益率：按列求均值
        mean_return=pr[c].mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        #计算年化标准差
        std_return=pr[c].std(axis=0)
        annual_std = std_return*np.sqrt(252)
        
        row=pd.Series({"名称":c,"年化收益率":annual_return,"年化标准差":annual_std})
        prr=prr.append(row,ignore_index=True)          
    
    #先按风险降序排名，高者排前面
    prr.sort_values(by="年化标准差",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['风险排名']=prr.index+1
    
    #再按收益降序排名，高者排前面
    prr.sort_values(by="年化收益率",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['收益排名']=prr.index+1    
    
    prr2=prr[["名称","年化收益率","年化标准差","收益排名","风险排名"]]
    
    #打印
    print("\n===== 投资组合排名：收益与风险 =====\n")
    #打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    #print(prr2.to_string(index=False,header=False))
    print(prr2.to_string(index=False))

    return    

if __name__=='__main__':
    portfolio_ranks(portfolio_returns)
#==============================================================================
if __name__=='__main__':
    simulation=1000

def portfolio_es(pf_info,simulation=1000):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均收益率和标准差，绘制投资组合的可行集
    """
    [[portfolio,thedate,stock_return,_],_]=pf_info
    pname=pname=portfolio_name(portfolio)
    _,_,tickerlist,_=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.date())
    hend0=stock_return.index[-1]; hend=str(hend0.date())    
    
    #获得成分股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成分股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(123)

    # 循环模拟n次随机的投资组合
    print("\n  Calculating possible portfolio combinations, please wait ...")    
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_std
    
    # 将numpy数组转化成DataFrame数据框
    import pandas as pd
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Returns', 'Volatility']

    # 绘制散点图
    RandomPortfolios.plot('Volatility','Returns',kind='scatter',color='y',edgecolors='k')
    """
    plt.style.use('seaborn-dark')
    RandomPortfolios.plot.scatter(x='Volatility', y='Returns', c='Returns',
                cmap='RdYlGn', edgecolors='black')
    """
    plt.title("投资组合: 马科维茨可行集")
    plt.ylabel("年化收益率")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="年化收益率标准差-->"
    footnote2="\n\n基于"+pname+"之成分股构造"+str(simulation)+"个投资组合"
    footnote3="\n观察期间："+hstart+"至"+hend
    footnote4="\n数据来源: 新浪/EM/stooq, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3+footnote4)
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es=portfolio_es(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_sharpe(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury'):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均风险溢价及其标准差，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,_,tickerlist,_=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    import pandas as pd
    #获得期间内无风险利率
    #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
    if not (rf_df is None):
        stock_return1=pd.merge(stock_return0,rf_df,how='inner',left_index=True,right_index=True)
        for t in tickerlist:
            #计算风险溢价
            stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        
        stock_return=stock_return1[tickerlist]
    else:
        print("  #Error(portfolio_es_sharpe): failed to retrieve risk-free interest rate, please try again")
        return None
    
    #获得成分股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成分股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(123)

    # 循环模拟n次随机的投资组合
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_std
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'Risk premium volatility']

    # 绘制散点图
    RandomPortfolios.plot('Risk premium volatility','Risk premium',kind='scatter',color='y',edgecolors='k')
    """
    plt.style.use('seaborn-dark')
    RandomPortfolios.plot.scatter(x='Volatility', y='Returns', c='Returns',
                cmap='RdYlGn', edgecolors='black')
    """
    plt.title("投资组合的风险溢价: 马科维茨可行集")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="年化风险溢价标准差-->"
    footnote2="\n\n基于"+pname+"之成分股构造"+str(simulation)+"个投资组合"
    footnote3="\n观察期间："+hstart+"至"+hend
    footnote4="\n数据来源: 新浪/EM/stooq, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3+footnote4)
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_sharpe=portfolio_es_sharpe(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_sortino(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury'):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均风险溢价及其下偏标准差，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,_,tickerlist,_=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    import pandas as pd
    #获得期间内无风险利率
    #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
    if not (rf_df is None):
        stock_return1=pd.merge(stock_return0,rf_df,how='inner',left_index=True,right_index=True)
        for t in tickerlist:
            stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        
        stock_return=stock_return1[tickerlist]
    else:
        print("  #Error(portfolio_es_sortino): failed to retrieve risk-free interest rate, please try again")
        return None
    
    #获得成分股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成分股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(123)

    # 循环模拟n次随机的投资组合
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均下偏标准差
        sr_temp0=stock_return.copy()
        sr_temp0['Portfolio Ret']=sr_temp0.mul(random_weight,axis=1).sum(axis=1)
        sr_temp1=sr_temp0[sr_temp0['Portfolio Ret'] < mean_return]
        sr_temp2=sr_temp1[tickerlist]
        lpsd_return=sr_temp2.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_lpsd = lpsd_return*np.sqrt(252)

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_lpsd
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'Risk premium LPSD']

    # 绘制散点图
    RandomPortfolios.plot('Risk premium LPSD','Risk premium',kind='scatter',color='y',edgecolors='k')
    """
    plt.style.use('seaborn-dark')
    RandomPortfolios.plot.scatter(x='Volatility', y='Returns', c='Returns',
                cmap='RdYlGn', edgecolors='black')
    """
    plt.title("投资组合的风险溢价: 马科维茨可行集")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="年化风险溢价的下偏标准差(LPSD)-->"
    footnote2="\n\n基于"+pname+"之成分股构造，共"+str(simulation)+"个投资组合"
    footnote3="\n观察期间："+hstart+"至"+hend
    footnote4="\n数据来源: 新浪/EM/stooq, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3+footnote4)
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_sortino=portfolio_es_sortino(pf_info,simulation=50000)

#==============================================================================
#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_alpha(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury'):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年化标准差和阿尔法指数，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,mktidx,tickerlist,_=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    #计算市场指数的收益率
    import pandas as pd
    start1=date_adjust(hstart,adjust=-30)
    mkt=get_prices(mktidx,start1,hend)
    mkt['Mkt']=mkt['Close'].pct_change()
    mkt.dropna(inplace=True)
    mkt1=pd.DataFrame(mkt['Mkt'])

    stock_return0m=pd.merge(stock_return0,mkt1,how='left',left_index=True,right_index=True)
    #获得期间内无风险利率
    #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
    if not (rf_df is None):
        stock_return1=pd.merge(stock_return0m,rf_df,how='inner',left_index=True,right_index=True)
        for t in tickerlist:
            #计算风险溢价
            stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        stock_return1['Mkt']=stock_return1['Mkt']-stock_return1['rf_daily']
        stock_return=stock_return1[tickerlist+['Mkt']]
    else:
        print("  #Error(portfolio_es_alpha): failed to retrieve risk-free interest rate, please try again")
        return None
    
    #获得成分股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成分股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(123)

    # 循环模拟n次随机的投资组合
    from scipy import stats
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的历史收益率
        stock_return['pRet']=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1)
        
        #回归求截距项作为阿尔法指数
     
        (beta,alpha,_,_,_)=stats.linregress(stock_return['Mkt'],stock_return['pRet'])        
        """
        mean_return=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)
        """
        # 将上面生成的权重，和计算得到的阿尔法指数、贝塔系数存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为收益指标，再后为风险指标
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = alpha
        random_p[i][numstocks+1] = beta
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['alpha', 'beta']

    # 绘制散点图
    RandomPortfolios.plot('beta','alpha',kind='scatter',color='y',edgecolors='k')
    """
    plt.style.use('seaborn-dark')
    RandomPortfolios.plot.scatter(x='Volatility', y='Returns', c='Returns',
                cmap='RdYlGn', edgecolors='black')
    """
    plt.title("投资组合的阿尔法指数: 马科维茨可行集")
    plt.ylabel("阿尔法指数")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="贝塔系数-->"
    footnote2="\n\n基于"+pname+"之成分股构造"+str(simulation)+"个投资组合"
    footnote3="\n观察期间："+hstart+"至"+hend
    footnote4="\n数据来源: 新浪/EM/stooq, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3+footnote4)
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_alpha=portfolio_es_alpha(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_treynor(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury'):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的风险溢价和贝塔系数，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,mktidx,tickerlist,_=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    #计算市场指数的收益率
    import pandas as pd
    start1=date_adjust(hstart,adjust=-30)
    mkt=get_prices(mktidx,start1,hend)
    mkt['Mkt']=mkt['Close'].pct_change()
    mkt.dropna(inplace=True)
    mkt1=pd.DataFrame(mkt['Mkt'])

    stock_return0m=pd.merge(stock_return0,mkt1,how='left',left_index=True,right_index=True)
    #获得期间内无风险利率
    #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
    if not (rf_df is None):
        stock_return1=pd.merge(stock_return0m,rf_df,how='inner',left_index=True,right_index=True)
        #计算各个成分股的风险溢价，合成后即可得到投资组合的风险溢价
        for t in tickerlist:
            stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        #计算市场的风险溢价
        stock_return1['Mkt']=stock_return1['Mkt']-stock_return1['rf_daily']
        stock_return=stock_return1[tickerlist+['Mkt']]
    else:
        print("  #Error(portfolio_es_treynor): failed to retrieve risk-free interest rate, please try again")
        return None
    
    #获得成分股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成分股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(123)

    # 循环模拟n次随机的投资组合
    from scipy import stats
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的历史收益率
        stock_return['pRet']=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1)
        
        #回归求截距项作为阿尔法指数
        (beta,alpha,_,_,_)=stats.linregress(stock_return['Mkt'],stock_return['pRet'])        
        #计算年化风险溢价
        mean_return=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
        """
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)
        """
        # 将上面生成的权重，和计算得到的风险溢价、贝塔系数存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为收益指标，再后为风险指标
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = beta
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'beta']

    # 绘制散点图
    RandomPortfolios.plot('beta','Risk premium',kind='scatter',color='y',edgecolors='k')
    """
    plt.style.use('seaborn-dark')
    RandomPortfolios.plot.scatter(x='Volatility', y='Returns', c='Returns',
                cmap='RdYlGn', edgecolors='black')
    """
    plt.title("投资组合: 马科维茨可行集")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="贝塔系数-->"
    footnote2="\n\n基于"+pname+"之成分股构造"+str(simulation)+"个投资组合"
    footnote3="\n观察期间："+hstart+"至"+hend
    footnote4="\n数据来源: 新浪/EM/stooq, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3+footnote4)
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_treynor=portfolio_es_treynor(pf_info,simulation=50000)

#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================

def portfolio_optimize_sharpe(es_sharpe):
    """
    功能：计算投资组合的最高夏普比率组合，并绘图
    MSR: Maximium Sharpe Rate, 最高夏普指数方案
    GMV: Global Minimum Volatility, 全局最小波动方案
    """
    [[[portfolio,thedate,stock_return,_],[StockReturns,_,_,_]],RandomPortfolios]=es_sharpe
    _,_,tickerlist,_=decompose_portfolio(portfolio)
    numstocks=len(tickerlist)  
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=StockReturns.index[0]; hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]; hend=str(hend0.date())
    
    # 计算夏普比率
    RandomPortfolios['Sharpe'] = RandomPortfolios['Risk premium']   \
                            / RandomPortfolios['Risk premium volatility']

    # 绘制收益-标准差的散点图，并用颜色描绘夏普比率
    # 绘制散点图
    RandomPortfolios.plot('Risk premium volatility','Risk premium',kind='scatter',alpha=0.3)
    plt.scatter(RandomPortfolios['Risk premium volatility'], RandomPortfolios['Risk premium'], 
            c=RandomPortfolios['Sharpe'])
    plt.colorbar(label='基于夏普比率，颜色越淡数值越大')
    plt.title("投资组合: 马科维茨可行集，基于夏普比率")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    plt.xlabel("年化风险溢价标准差-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))     
    plt.show()

    #绘制有效集
    RandomPortfolios.plot('Risk premium volatility','Risk premium',kind='scatter',color='y',edgecolors='k')

    # 找到夏普比率最大数据对应的索引值
    max_index = RandomPortfolios.Sharpe.idxmax()
    # 在收益-风险散点图中突出夏普比率最大的点
    MSR_x = RandomPortfolios.loc[max_index,'Risk premium volatility']
    MSR_y = RandomPortfolios.loc[max_index,'Risk premium']
    plt.scatter(MSR_x, MSR_y, color='red',marker='*',s=150,label="MSR点")  
    # 提取最大夏普比率组合对应的权重，并转化为numpy数组
    import numpy as np    
    MSR_weights = np.array(RandomPortfolios.iloc[max_index, 0:numstocks])
    # 计算MSR组合的收益率
    StockReturns['Portfolio_MSR'] = stock_return.mul(MSR_weights, axis=1).sum(axis=1)
    
    # 找到标准差最小数据的索引值
    min_index = RandomPortfolios['Risk premium volatility'].idxmin()
    # 提取最小波动组合对应的权重, 并转换成Numpy数组
    # 在收益-风险散点图中突出风险最小的点
    GMV_x = RandomPortfolios.loc[min_index,'Risk premium volatility']
    GMV_y = RandomPortfolios.loc[min_index,'Risk premium']
    plt.scatter(GMV_x, GMV_y, color='m',marker='8',s=100,label="GMV点") 
    # 提取最小风险组合对应的权重，并转化为numpy数组
    GMV_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算GMV投资组合收益率
    StockReturns['Portfolio_GMV'] = stock_return.mul(GMV_weights, axis=1).sum(axis=1)

    plt.title("投资组合策略: 基于夏普比率")
    plt.ylabel("年化风险溢价")
    plt.xlabel("年化风险溢价标准差-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))    
    plt.legend(loc='best')
    plt.show()

    #返回数据，供进一步分析
    portfolio_returns=StockReturns.copy()
    pelist=['Portfolio','Portfolio_EW','Portfolio_LW','Portfolio_MSR','Portfolio_GMV', \
           'Portfolio_MSO','Portfolio_GML','Portfolio_MAR','Portfolio_GMB', \
            'Portfolio_MTR','Portfolio_GMB2']
    pclist=[pname,'等权重组合','流动性组合','MSR组合','GMV组合','MSO组合','GML组合', \
            'MAR组合','GMB组合', 'MTR组合','GMB2组合']
    pecols=list(portfolio_returns)
    for p in pecols:
        ppos=pelist.index(p)
        pc=pclist[ppos]
        portfolio_returns.rename(columns={p:pc},inplace=True)
    
    return MSR_weights,GMV_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_sharpe=portfolio_es_sharpe(pf_info,simulation=50000)
    
    MSR_weights,GMV_weights,portfolio_returns=portfolio_optimize_sharpe(es_sharpe)
    

#==============================================================================

def portfolio_optimize_sortino(es_sortino):
    """
    功能：计算投资组合的最高索替诺比率组合，并绘图
    MSO: Maximium Sortino ratio, 最高索替诺比率方案
    GML: Global Minimum LPSD volatility, 全局最小LPSD下偏标准差方案
    """
    [[[portfolio,thedate,stock_return,_],[StockReturns,_,_,_]],RandomPortfolios]=es_sortino
    _,_,tickerlist,_=decompose_portfolio(portfolio)
    numstocks=len(tickerlist)  
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=StockReturns.index[0]; hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]; hend=str(hend0.date())
    
    # 计算夏普比率
    RandomPortfolios['Sortino'] = RandomPortfolios['Risk premium']   \
                            / RandomPortfolios['Risk premium LPSD']

    # 绘制收益-标准差的散点图，并用颜色描绘夏普比率
    # 绘制散点图
    RandomPortfolios.plot('Risk premium LPSD','Risk premium',kind='scatter',alpha=0.3)
    plt.scatter(RandomPortfolios['Risk premium LPSD'], RandomPortfolios['Risk premium'], 
            c=RandomPortfolios['Sortino'])
    plt.colorbar(label='基于索替诺比率，颜色越淡数值越大')
    plt.title("投资组合: 马科维茨可行集，基于索替诺比率")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    plt.xlabel("年化风险溢价之下偏标准差-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))     
    plt.show()

    #绘制有效集
    RandomPortfolios.plot('Risk premium LPSD','Risk premium',kind='scatter',color='y',edgecolors='k')

    # 找到索替诺比率最大数据对应的索引值
    max_index = RandomPortfolios.Sortino.idxmax()
    # 在收益-风险散点图中突出夏普比率最大的点
    MSO_x = RandomPortfolios.loc[max_index,'Risk premium LPSD']
    MSO_y = RandomPortfolios.loc[max_index,'Risk premium']
    plt.scatter(MSO_x, MSO_y, color='red',marker='*',s=150,label="MSO点")  
    # 提取最大索替诺比率组合对应的权重，并转化为numpy数组
    import numpy as np    
    MSO_weights = np.array(RandomPortfolios.iloc[max_index, 0:numstocks])
    # 计算MSO组合的收益率
    StockReturns['Portfolio_MSO'] = stock_return.mul(MSO_weights, axis=1).sum(axis=1)
    
    # 找到下偏标准差最小数据的索引值
    min_index = RandomPortfolios['Risk premium LPSD'].idxmin()
    # 提取最小波动组合对应的权重, 并转换成Numpy数组
    # 在收益-风险散点图中突出风险最小的点
    GML_x = RandomPortfolios.loc[min_index,'Risk premium LPSD']
    GML_y = RandomPortfolios.loc[min_index,'Risk premium']
    plt.scatter(GML_x, GML_y, color='m',marker='8',s=100,label="GML点") 
    # 提取最小风险组合对应的权重，并转化为numpy数组
    GML_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算GML投资组合收益率
    StockReturns['Portfolio_GML'] = stock_return.mul(GML_weights, axis=1).sum(axis=1)

    plt.title("投资组合策略: 基于索替诺比率")
    plt.ylabel("年化风险溢价")
    plt.xlabel("年化风险溢价之下偏标准差-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))    
    plt.legend(loc='best')
    plt.show()

    #返回数据，供进一步分析
    portfolio_returns=StockReturns.copy()
    """
    list(portfolio_returns)
    """
    pelist=['Portfolio','Portfolio_EW','Portfolio_LW','Portfolio_MSR','Portfolio_GMV', \
           'Portfolio_MSO','Portfolio_GML','Portfolio_MAR','Portfolio_GMB', \
            'Portfolio_MTR','Portfolio_GMB2']
    pclist=[pname,'等权重组合','流动性组合','MSR组合','GMV组合','MSO组合','GML组合', \
            'MAR组合','GMB组合', 'MTR组合','GMB2组合']
    pecols=list(portfolio_returns)
    for p in pecols:
        ppos=pelist.index(p)
        pc=pclist[ppos]
        portfolio_returns.rename(columns={p:pc},inplace=True)
        
    return MSO_weights,GML_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_sortino=portfolio_es_sortino(pf_info,simulation=50000)
    
    MSO_weights,GML_weights,portfolio_returns=portfolio_optimize_sortino(es_Sortino)
    
    
#==============================================================================

def portfolio_optimize_alpha(es_alpha):
    """
    功能：计算投资组合的最高詹森阿尔法组合，并绘图
    MAR: Maximium Alpha Ratio, 最高阿尔法指数方案
    GMB: Global Minimum Beta, 全局最小贝塔系数方案
    """
    [[[portfolio,thedate,stock_return,_],[StockReturns,_,_,_]],RandomPortfolios]=es_alpha
    _,_,tickerlist,_=decompose_portfolio(portfolio)
    numstocks=len(tickerlist)  
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=StockReturns.index[0]; hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]; hend=str(hend0.date())
    
    # 方案1：直接使用阿尔法指数：因为阿尔法已经经过了贝塔系数的调整
    RandomPortfolios['alpha ratio'] = RandomPortfolios['alpha']
    """
    # 方案2：使用阿尔法-贝塔系数比值，可作为收益-风险性价比
    RandomPortfolios['alpha ratio'] = RandomPortfolios['alpha']   \
                            / RandomPortfolios['beta']
    """
    # 绘制收益-风险的散点图，并用颜色描绘
    # 绘制散点图
    RandomPortfolios.plot('beta','alpha',kind='scatter',alpha=0.3)
    plt.scatter(RandomPortfolios['beta'], RandomPortfolios['alpha'], 
            c=RandomPortfolios['alpha ratio'])
    plt.colorbar(label='基于阿尔法指数，颜色越淡数值越大')
    plt.title("投资组合: 马科维茨可行集，基于詹森阿尔法")
    plt.ylabel("阿尔法指数")
    
    import datetime as dt; stoday=dt.date.today()
    plt.xlabel("贝塔系数-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))     
    plt.show()

    #绘制有效集
    RandomPortfolios.plot('beta','alpha',kind='scatter',color='y',edgecolors='k')

    # 找到阿尔法指数最大数据对应的索引值
    max_index = RandomPortfolios['alpha ratio'].idxmax()
    # 在收益-风险散点图中突出阿尔法指数最大的点
    MAR_x = RandomPortfolios.loc[max_index,'beta']
    MAR_y = RandomPortfolios.loc[max_index,'alpha ratio']
    plt.scatter(MAR_x, MAR_y, color='red',marker='*',s=150,label="MAR点")  
    # 提取最大阿尔法指数组合对应的权重，并转化为numpy数组
    import numpy as np    
    MAR_weights = np.array(RandomPortfolios.iloc[max_index, 0:numstocks])
    # 计算MAR组合的收益率
    StockReturns['Portfolio_MAR'] = stock_return[tickerlist].mul(MAR_weights, axis=1).sum(axis=1)
    
    # 找到贝塔系数最小数据的索引值
    min_index = RandomPortfolios['beta'].idxmin()
    # 提取最小风险组合对应的权重, 并转换成Numpy数组
    # 在收益-风险散点图中突出风险最小的点
    GMB_x = RandomPortfolios.loc[min_index,'beta']
    GMB_y = RandomPortfolios.loc[min_index,'alpha ratio']
    plt.scatter(GMB_x, GMB_y, color='m',marker='8',s=100,label="GMB点") 
    # 提取最小风险组合对应的权重，并转化为numpy数组
    GMB_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算GMB投资组合收益率
    StockReturns['Portfolio_GMB'] = stock_return[tickerlist].mul(GMB_weights, axis=1).sum(axis=1)

    plt.title("投资组合策略: 基于詹森阿尔法")
    plt.ylabel("阿尔法指数")
    plt.xlabel("贝塔系数-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))    
    plt.legend(loc='best')
    plt.show()

    #返回数据，供进一步分析
    portfolio_returns=StockReturns.copy()
    pelist=['Portfolio','Portfolio_EW','Portfolio_LW','Portfolio_MSR','Portfolio_GMV', \
           'Portfolio_MSO','Portfolio_GML','Portfolio_MAR','Portfolio_GMB', \
            'Portfolio_MTR','Portfolio_GMB2']
    pclist=[pname,'等权重组合','流动性组合','MSR组合','GMV组合','MSO组合','GML组合', \
            'MAR组合','GMB组合', 'MTR组合','GMB2组合']
    pecols=list(portfolio_returns)
    for p in pecols:
        ppos=pelist.index(p)
        pc=pclist[ppos]
        portfolio_returns.rename(columns={p:pc},inplace=True)
    
    return MAR_weights,GMB_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_alpha=portfolio_es_alpha(pf_info,simulation=50000)
    
    MAR_weights,GMB_weights,portfolio_returns=portfolio_optimize_alpha(es_alpha)
    
#==============================================================================

def portfolio_optimize_treynor(es_treynor):
    """
    功能：计算投资组合的最高特雷诺比率组合，并绘图
    MTR: Maximium Treynor Ratio, 最高特雷诺指数方案
    GMB2: Global Minimum Beta, 全局最小贝塔系数方案
    """
    [[[portfolio,thedate,stock_return,_],[StockReturns,_,_,_]],RandomPortfolios]=es_treynor
    _,_,tickerlist,_=decompose_portfolio(portfolio)
    numstocks=len(tickerlist)  
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=StockReturns.index[0]; hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]; hend=str(hend0.date())
    
    # 方案1：直接使用阿尔法指数：因为阿尔法已经经过了贝塔系数的调整
    RandomPortfolios['Treynor'] = RandomPortfolios['Risk premium']   \
                            / RandomPortfolios['beta']
    # 绘制收益-风险的散点图，并用颜色描绘
    # 绘制散点图
    RandomPortfolios.plot('beta','Risk premium',kind='scatter',alpha=0.3)
    plt.scatter(RandomPortfolios['beta'], RandomPortfolios['Risk premium'], 
            c=RandomPortfolios['Treynor'])
    plt.colorbar(label='基于特雷诺指数，颜色越淡数值越大')
    plt.title("投资组合: 马科维茨可行集，基于特雷诺指数")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    plt.xlabel("贝塔系数-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))     
    plt.show()

    #绘制有效集
    RandomPortfolios.plot('beta','Risk premium',kind='scatter',color='y',edgecolors='k')

    # 找到特雷诺指数最大数据对应的索引值
    max_index = RandomPortfolios['Treynor'].idxmax()
    # 在收益-风险散点图中突出阿尔法指数最大的点
    MTR_x = RandomPortfolios.loc[max_index,'beta']
    MTR_y = RandomPortfolios.loc[max_index,'Treynor']
    plt.scatter(MTR_x, MTR_y, color='red',marker='*',s=150,label="MTR点")  
    # 提取最大特雷诺指数组合对应的权重，并转化为numpy数组
    import numpy as np    
    MTR_weights = np.array(RandomPortfolios.iloc[max_index, 0:numstocks])
    # 计算MTR组合的收益率
    StockReturns['Portfolio_MTR'] = stock_return[tickerlist].mul(MTR_weights, axis=1).sum(axis=1)
    
    # 找到贝塔系数最小数据的索引值
    min_index = RandomPortfolios['beta'].idxmin()
    # 提取最小风险组合对应的权重, 并转换成Numpy数组
    # 在收益-风险散点图中突出风险最小的点
    GMB2_x = RandomPortfolios.loc[min_index,'beta']
    GMB2_y = RandomPortfolios.loc[min_index,'Treynor']
    plt.scatter(GMB2_x, GMB2_y, color='m',marker='8',s=100,label="GMB2点") 
    # 提取最小风险组合对应的权重，并转化为numpy数组
    GMB2_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算GMB2投资组合收益率
    StockReturns['Portfolio_GMB2'] = stock_return[tickerlist].mul(GMB2_weights, axis=1).sum(axis=1)

    plt.title("投资组合策略: 基于特雷诺指数")
    plt.ylabel("年化风险溢价")
    plt.xlabel("贝塔系数-->"+ \
               "\n\n观察期间："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/EM/stooq, "+str(stoday))    
    plt.legend(loc='best')
    plt.show()

    #返回数据，供进一步分析
    portfolio_returns=StockReturns.copy()
    pelist=['Portfolio','Portfolio_EW','Portfolio_LW','Portfolio_MSR','Portfolio_GMV', \
           'Portfolio_MSO','Portfolio_GML','Portfolio_MAR','Portfolio_GMB', \
            'Portfolio_MTR','Portfolio_GMB2']
    pclist=[pname,'等权重组合','流动性组合','MSR组合','GMV组合','MSO组合','GML组合', \
            'MAR组合','GMB组合', 'MTR组合','GMB2组合']
    pecols=list(portfolio_returns)
    for p in pecols:
        ppos=pelist.index(p)
        pc=pclist[ppos]
        portfolio_returns.rename(columns={p:pc},inplace=True)
    
    return MTR_weights,GMB2_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_treynor=portfolio_es_treynor(pf_info,simulation=50000)
    
    MTR_weights,GMB2_weights,portfolio_returns=portfolio_optimize_treynor(es_treynor)

#==============================================================================
    
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================

def translate_tickerlist(tickerlist):
    newlist=[]
    for t in tickerlist:
        name=codetranslate(t)
        newlist=newlist+[name]
        
    return newlist
#==============================================================================
# 绘制马科维茨有效边界
#==============================================================================
def ret_monthly(ticker,prices): 
    """
    功能：
    """
    price=prices['Adj Close'][ticker]
    
    import numpy as np
    div=price.pct_change()+1
    logret=np.log(div)
    import pandas as pd
    lrdf=pd.DataFrame(logret)
    lrdf['ymd']=lrdf.index.astype("str")
    lrdf['ym']=lrdf['ymd'].apply(lambda x:x[0:7])
    lrdf.dropna(inplace=True)
    
    mret=lrdf.groupby(by=['ym'])[ticker].sum()
    
    return mret

if __name__=='__main__':
    ticker='MSFT'
    fromdate,todate='2019-1-1','2020-8-1'

#==============================================================================
def objFunction(W,R,target_ret):
    
    import numpy as np
    stock_mean=np.mean(R,axis=0)
    port_mean=np.dot(W,stock_mean) # portfolio mean
    
    cov=np.cov(R.T) # var-cov matrix
    port_var=np.dot(np.dot(W,cov),W.T) # portfolio variance
    penalty = 2000*abs(port_mean-target_ret)# penalty 4 deviation
    
    objfunc=np.sqrt(port_var) + penalty # objective function 
    
    return objfunc   

#==============================================================================
def portfolio_ef_0(stocks,fromdate,todate):
    """
    功能：绘制马科维茨有效前沿，不区分上半沿和下半沿
    问题：很可能出现上下边界折叠的情况，难以解释，弃用
    """
    #Code for getting stock prices
    prices=get_prices(stocks,fromdate,todate)
    
    #Code for generating a return matrix R
    R0=ret_monthly(stocks[0],prices) # starting from 1st stock
    n_stock=len(stocks) # number of stocks
    import pandas as pd
    import numpy as np
    for i in range(1,n_stock): # merge with other stocks
        x=ret_monthly(stocks[i],prices)
        R0=pd.merge(R0,x,left_index=True,right_index=True)
        R=np.array(R0)    

    #Code for estimating optimal portfolios for a given return
    out_mean,out_std,out_weight=[],[],[]
    import numpy as np
    stockMean=np.mean(R,axis=0)
    
    from scipy.optimize import minimize
    for r in np.linspace(np.min(stockMean),np.max(stockMean),num=100):
        W = np.ones([n_stock])/n_stock # starting from equal weights
        b_ = [(0,1) for i in range(n_stock)] # bounds, here no short
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. }) #constraint
        result=minimize(objFunction,W,(R,r),method='SLSQP'
                                    ,constraints=c_, bounds=b_)
        if not result.success: # handle error raise    
            BaseException(result.message)
        
        out_mean.append(round(r,4)) # 4 decimal places
        std_=round(np.std(np.sum(R*result.x,axis=1)),6)
        out_std.append(std_)
        out_weight.append(result.x)

    #Code for plotting the efficient frontier
    
    plt.title('Efficient Frontier of Portfolio')
    plt.xlabel('Standard Deviation of portfolio (Risk))')
    plt.ylabel('Return of portfolio')
    
    out_std_min=min(out_std)
    pos=out_std.index(out_std_min)
    out_mean_min=out_mean[pos]
    x_left=out_std_min+0.25
    y_left=out_mean_min+0.5
    
    #plt.figtext(x_left,y_left,str(n_stock)+' stock are used: ')
    plt.figtext(x_left,y_left,"投资组合由"+str(n_stock)+'种证券构成: ')
    plt.figtext(x_left,y_left-0.05,' '+str(stocks))
    plt.figtext(x_left,y_left-0.1,'观察期间：'+str(fromdate)+'至'+str(todate))
    plt.plot(out_std,out_mean,color='r',ls=':',lw=4)
    plt.show()    
    
    return

if __name__=='__main__':
    stocks=['IBM','WMT','AAPL','C','MSFT']
    fromdate,todate='2019-1-1','2020-8-1'   
    portfolio_ef_0(stocks,fromdate,todate)

#==============================================================================
def portfolio_ef(stocks,fromdate,todate):
    """
    功能：多只股票的马科维茨有效边界，区分上半沿和下半沿，标记风险极小点
    问题：很可能出现上下边界折叠的情况，难以解释，弃用
    """
    print("\n  Searching for portfolio information, please wait...")
    #Code for getting stock prices
    prices=get_prices(stocks,fromdate,todate)
    
    #Code for generating a return matrix R
    R0=ret_monthly(stocks[0],prices) # starting from 1st stock
    n_stock=len(stocks) # number of stocks
    
    import pandas as pd
    import numpy as np
    for i in range(1,n_stock): # merge with other stocks
        x=ret_monthly(stocks[i],prices)
        R0=pd.merge(R0,x,left_index=True,right_index=True)
        R=np.array(R0)    

    #Code for estimating optimal portfolios for a given return
    out_mean,out_std,out_weight=[],[],[]
    stockMean=np.mean(R,axis=0)
    
    from scipy.optimize import minimize
    for r in np.linspace(np.min(stockMean),np.max(stockMean),num=100):
        W = np.ones([n_stock])/n_stock # starting from equal weights
        b_ = [(0,1) for i in range(n_stock)] # bounds, here no short
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. }) #constraint
        result=minimize(objFunction,W,(R,r),method='SLSQP'
                                    ,constraints=c_, bounds=b_)
        if not result.success: # handle error raise    
            BaseException(result.message)
        
        out_mean.append(round(r,4)) # 4 decimal places
        std_=round(np.std(np.sum(R*result.x,axis=1)),6)
        out_std.append(std_)
        out_weight.append(result.x)

    #Code for positioning
    out_std_min=min(out_std)
    pos=out_std.index(out_std_min)
    out_mean_min=out_mean[pos]
    x_left=out_std_min+0.25
    y_left=out_mean_min+0.5
    
    import pandas as pd
    out_df=pd.DataFrame(out_mean,out_std,columns=['mean'])
    out_df_ef=out_df[out_df['mean']>=out_mean_min]
    out_df_ief=out_df[out_df['mean']<out_mean_min]

    #Code for plotting the efficient frontier
    
    plt.title('投资组合：马科维茨有效边界（理想图）')
    
    import datetime as dt; stoday=dt.date.today()    
    plt.xlabel('收益率标准差-->'+"\n数据来源：新浪/EM/stooq, "+str(stoday))
    plt.ylabel('收益率')
    
    plt.figtext(x_left,y_left,"投资组合由"+str(n_stock)+'种证券构成: ')
    plt.figtext(x_left,y_left-0.05,' '+str(stocks))
    plt.figtext(x_left,y_left-0.1,'观察期间：'+str(fromdate)+'至'+str(todate))
    plt.plot(out_df_ef.index,out_df_ef['mean'],color='r',ls='--',lw=2,label='有效边界')
    plt.plot(out_df_ief.index,out_df_ief['mean'],color='k',ls=':',lw=2,label='无效边界')
    plt.plot(out_std_min,out_mean_min,'g*-',markersize=16,label='风险最低点')
    
    plt.legend(loc='best')
    plt.show()    
    
    return

if __name__=='__main__':
    stocks=['IBM','WMT','AAPL','C','MSFT']
    fromdate,todate='2019-1-1','2020-8-1' 
    df=portfolio_ef(stocks,fromdate,todate)


































