# -*- coding: utf-8 -*-

from .api import (
    OPEN, HIGH, LOW, CLOSE, VOLUME, VOL,
    ABS, MAX, HHV, LLV,
    REF, IF, SUM, STD, AVEDEV,
    MA, EMA, SMA,
    CROSS,
)

import numpy as np
import math
from enum import Enum

# 定义买卖信号关键字
SIGN_BUY    = -1
SIGN_SELL   = 1
SIGN_WAIT   = 0

def KDJ(N=9, M1=3, M2=3):
    """
    KDJ 随机指标
    """
    RSV = (CLOSE - LLV(LOW, N)) / (HHV(HIGH, N) - LLV(LOW, N)) * 100
    K = EMA(RSV, (M1 * 2 - 1))
    D = EMA(K, (M2 * 2 - 1))
    J = K * 3 - D * 2

    return K, D, J

def DMI(M1=14, M2=6):
    """
    DMI 趋向指标
    """
    TR = SUM(MAX(MAX(HIGH - LOW, ABS(HIGH - REF(CLOSE, 1))), ABS(LOW - REF(CLOSE, 1))), M1)
    HD = HIGH - REF(HIGH, 1)
    LD = REF(LOW, 1) - LOW

    DMP = SUM(IF((HD > 0) & (HD > LD), HD, 0), M1)
    DMM = SUM(IF((LD > 0) & (LD > HD), LD, 0), M1)
    DI1 = DMP * 100 / TR
    DI2 = DMM * 100 / TR
    ADX = MA(ABS(DI2 - DI1) / (DI1 + DI2) * 100, M2)
    ADXR = (ADX + REF(ADX, M2)) / 2

    return DI1, DI2, ADX, ADXR

def DMI_SYS(N=7):
    """
        同花顺- 趋向指标(系统)
    """
    TR = SUM(MAX(MAX(HIGH - LOW, ABS(HIGH - REF(CLOSE, 1))), ABS(LOW - REF(CLOSE, 1))), N)
    HD = HIGH - REF(HIGH, 1)
    LD = REF(LOW, 1) - LOW
    
    DMP= SUM(IF((HD > 0) & (HD > LD), HD, 0), N)
    DMM= SUM(IF((LD > 0) & (LD > HD), LD, 0), N)
    
    PDI= DMP * 100 / TR
    MDI= DMM * 100 / TR
    
    # BUY
    b = CROSS(PDI,MDI)
    # SELL
    s = CROSS(MDI,PDI)
    
    if b:
        return SIGN_BUY
    if s:
        return SIGN_SELL
    return SIGN_WAIT

def MACD(SHORT=12, LONG=26, M=9):
    """
    MACD 指数平滑移动平均线
    """
    DIFF = EMA(CLOSE, SHORT) - EMA(CLOSE, LONG)
    DEA = EMA(DIFF, M)
    MACD = (DIFF - DEA) * 2

    return MACD

def MACD_SYS(SHORT=12, LONG=26, M=9):
    """
    MACD 
    
    MACD指标说明
    
    DIFF 与 DEA 形成全叉,为买入条件
    
    MACD指数平滑异同移动平均线为两条长、短的平滑平均线。
    其买卖原则为：
    1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号参考。
    2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号参考。
    3.DEA线与K线发生背离，行情可能出现反转信号。
    4.分析MACD柱状线，由红变绿(正变负)，卖出信号参考；由绿变红，买入信号参考。

    同花顺公式
    
    DIFF= EMA(CLOSE,SHORT) - EMA(CLOSE,LONG);
    DEA = EMA(DIFF,m);
    IF(Long>short)
        {
            IF (CROSS(diff,dea))
            BUY;
            IF (CROSS(dea,diff))
            SELL;
        }
    """
    DIFF = EMA(CLOSE, SHORT) - EMA(CLOSE, LONG)
    DEA  = EMA(DIFF, M)
    if LONG > SHORT:
        b = (CROSS(DIFF, DEA))
        if b:
            return SIGN_BUY
        s = (CROSS(DEA, DIFF))
        if s:
            return SIGN_SELL
    return SIGN_WAIT

def RSI(N1=6, N2=12, N3=24):
    """
    RSI 相对强弱指标
    """
    LC = REF(CLOSE, 1)
    RSI1 = SMA(MAX(CLOSE - LC, 0), N1, 1) / SMA(ABS(CLOSE - LC), N1, 1) * 100
    RSI2 = SMA(MAX(CLOSE - LC, 0), N2, 1) / SMA(ABS(CLOSE - LC), N2, 1) * 100
    RSI3 = SMA(MAX(CLOSE - LC, 0), N3, 1) / SMA(ABS(CLOSE - LC), N3, 1) * 100

    return RSI1, RSI2, RSI3

def BOLL(N=20, P=2):
    """
    BOLL 布林带
    """
    MID = MA(CLOSE, N)
    UPPER = MID + STD(CLOSE, N) * P
    LOWER = MID - STD(CLOSE, N) * P

    return UPPER, MID, LOWER

def WR(N=10, N1=6):
    """
    W&R 威廉指标
    """
    WR1 = (HHV(HIGH, N) - CLOSE) / (HHV(HIGH, N) - LLV(LOW, N)) * 100
    WR2 = (HHV(HIGH, N1) - CLOSE) / (HHV(HIGH, N1) - LLV(LOW, N1)) * 100

    return WR1, WR2

def BIAS(L1=6, L4=12, L5=24):
    """
    BIAS 乖离率
    """
    BIAS  = (CLOSE - MA(CLOSE, L1)) / MA(CLOSE, L1) * 100
    BIAS2 = (CLOSE - MA(CLOSE, L4)) / MA(CLOSE, L4) * 100
    BIAS3 = (CLOSE - MA(CLOSE, L5)) / MA(CLOSE, L5) * 100

    return BIAS, BIAS2, BIAS3

def BIAS_SYS(M1=6, M2=-3, M3=3, M4=12, M5=24):
    """
    BIAS 乖离率(系统)
    
    乖离率的值围绕零上下波动
    
    1.负的乖离率越小，空头回补的可能性越大，因此，负的乖离率向下跌破买入线，为买入时机．
    2.正的乖离率越大，表示短期获利越大，获利回吐的可能性越高，因此正的乖离率向上突破卖出线，为卖出时机．
    参数：
    N 天数，计算乖离率时用　一般12天
    LL  买入线，一般-6；LH　卖出线，一般6
    
    信号:
    
    低于 -3 买入
    高于  3 卖出
    
    参数默认值: M1 -> 6, M2 -> -3, M3 -> 3, M4 -> 12, M5 -> 24

    同花顺公式:
    
    BIAS:=(CLOSE-MA(CLOSE,M1))/MA(CLOSE,M1)*100;
    BIAS2:=(CLOSE-MA(CLOSE,M4))/MA(CLOSE,M4)*100;
    BIAS3:=(CLOSE-MA(CLOSE,M5))/MA(CLOSE,M5)*100;
    b:=(CROSS(BIAS,M2));
    s:=(CROSS(M2,BIAS)) OR (CROSS(M3,BIAS));
    bm:=BARSLAST(b);
    sm:=BARSLAST(s);
    bm1:=IF(bm[1]=-1 AND b,1,IF(bm[1]!=-1  AND sm[1]!=-1 AND bm[1]>sm[1] AND b AND b[1]=0,1,0));
    sm1:=IF(sm[1]=-1 AND bm[1]!=-1 AND s,1,IF( sm[1]!=-1 AND bm[1]!=-1 AND sm[1]>bm[1] AND s AND s[1]=0,1,0));
    IF(bm1>0)
    BUY;
    IF(sm1>0)
    SELL;
    """
    BIAS = (CLOSE - MA(CLOSE, M1)) / MA(CLOSE, M1) * 100
    BIAS2= (CLOSE - MA(CLOSE, M4)) / MA(CLOSE, M4) * 100
    BIAS3= (CLOSE - MA(CLOSE, M5)) / MA(CLOSE, M5) * 100
    
    # 买入
    b = (CROSS(BIAS, M2))
    # 卖出
    s = (CROSS(M2, BIAS)) | (CROSS(M3, BIAS))
    
    # b[1]=0 的意思是当天交叉
    # bm[1]=-1 的意思是 从未出现过买入信号
    # sm[1]!=-1 的意思是 一天之内出现了卖出信号
    
    # IF(bm[1]=-1 AND b,1,IF(bm[1]!=-1  AND sm[1]!=-1 AND bm[1]>sm[1] AND b AND b[1]=0,1,0));
    # 这句的意思是, 如果从未出现过买入信号并且本次出现了, 则抛出买入信号
    # 如果出现过买入信号, 并且出现过卖出信号, 并且买入信号的出现时间远于卖出信号的出现时间, 并且今天出现交叉, 则抛出买入信号, 否则不抛出.
    # IF(sm[1]=-1 AND bm[1]!=-1 AND s,1,IF( sm[1]!=-1 AND bm[1]!=-1 AND sm[1]>bm[1] AND s AND s[1]=0,1,0));
    # 这句的意思是, 如果未出现过卖出,但出现过买入信号,并且当前出现买入信号, 则抛出买入信号
    # 如果出现过买入信号, 并且出现过卖出信号, 并且卖出信号出现时间远于买入信号,并且当前交叉, 则抛出卖出信号
    # 以上条件依赖于一个 一个未实现的函数 BARSLAST
    # 因此这里只对信号本身做抛出, 是否实现, 要暂时交给外部做判断
    return b, s

def ASI(M1=26, M2=10):
    """
    ASI 震动升降指标
    """
    LC = REF(CLOSE, 1)
    AA = ABS(HIGH - LC)
    BB = ABS(LOW - LC)
    CC = ABS(HIGH - REF(LOW, 1))
    DD = ABS(LC - REF(OPEN, 1))
    R = IF((AA > BB) & (AA > CC), AA + BB / 2 + DD / 4, IF((BB > CC) & (BB > AA), BB + AA / 2 + DD / 4, CC + DD / 4))
    X = (CLOSE - LC + (CLOSE - OPEN) / 2 + LC - REF(OPEN, 1))
    SI = X * 16 / R * MAX(AA, BB)
    ASI = SUM(SI, M1)
    ASIT = MA(ASI, M2)

    return ASI, ASIT

def VR(M1=26):
    """
    VR容量比率
    """
    LC = REF(CLOSE, 1)
    VR = SUM(IF(CLOSE > LC, VOL, 0), M1) / SUM(IF(CLOSE <= LC, VOL, 0), M1) * 100

    return VR

def ARBR(M1=26):
    """
    ARBR人气意愿指标
    """
    AR = SUM(HIGH - OPEN, M1) / SUM(OPEN - LOW, M1) * 100
    BR = SUM(MAX(0, HIGH - REF(CLOSE, 1)), M1) / SUM(MAX(0, REF(CLOSE, 1) - LOW), M1) * 100

    return AR, BR

def DPO(M1=20, M2=10, M3=6):
    DPO = CLOSE - REF(MA(CLOSE, M1), M2)
    MADPO = MA(DPO, M3)

    return DPO, MADPO

def TRIX(M1=12, M2=20):
    TR = EMA(EMA(EMA(CLOSE, M1), M1), M1)
    TRIX = (TR - REF(TR, 1)) / REF(TR, 1) * 100
    TRMA = MA(TRIX, M2)

    return TRIX, TRMA

def MTM(M1=12, M2=6):
    '''
        动量线指标
        
        参数 
        M1 12 日动量线
        M2 6  日移动平均
        
        说明:

        动量线:收盘价-N日前的收盘价
        MAMTM:MTM的M日简单移动平均
        MTM线　:当日收盘价与N日前的收盘价的差；
        MTMMA线:对上面的差值求N日移动平均；

        参数：N 间隔天数，也是求移动平均的天数，一般取6
        用法：
        1.MTM从下向上突破MTMMA，买入参考信号；
        2.MTM从上向下跌破MTMMA，卖出参考信号；
        
        强弱判断
        1.股价续创新高，而MTM未配合上升，意味上涨动力减弱；
        2.股价续创新低，而MTM未配合下降，意味下跌动力减弱；
        3.股价与MTM在低位同步上升，将有反弹行情；反之，从高位同步下降，将有回落走势。

        同花顺公式:
        MTM:CLOSE-REF(CLOSE,M1);
        MAMTM:MA(MTM,M2);
    '''
    # 当前线
    MTM = CLOSE - REF(CLOSE, M1)
    # 均线
    MAMTM = MA(MTM, M2)
    
    return MTM, MAMTM

def MTM_SYS(N=12, M=6):
    '''
        动量线(系统)指标
        说明:

        动量线:收盘价-N日前的收盘价
        
        MAMTM   : MTM的M日简单移动平均
        MTM线   : 当日收盘价与N日前的收盘价的差；
        MTMMA线 : 对上面的差值求N日移动平均；
        
        参数：N 间隔天数，也是求移动平均的天数，一般取6
        用法：
        1.MTM从下向上突破MTMMA，买入信号；
        2.MTM从上向下跌破MTMMA，卖出信号；
        3.股价续创新高，而MTM未配合上升，意味上涨动力减弱；
        4.股价续创新低，而MTM未配合下降，意味下跌动力减弱；
        5.股价与MTM在低位同步上升，将有反弹行情；反之，从高位同步下降，将有回落走势。
        
        参数 
        N 12 日动量线
        M 6  日移动平均
        
        WMTM=CLOSE-REF(CLOSE,N);
        MAMTM=MA(wMTM,M);
        IF (CROSS(WMTM,MAMTM))
        BUY;
        IF (CROSS(MAMTM,WMTM))
        SELL;
    '''
    WMTM = CLOSE - REF(CLOSE, N)
    MAMTM= MA(WMTM, M)
    
    b = CROSS(WMTM, MAMTM)
    s = CROSS(MAMTM, WMTM)
    
    if b:
        return SIGN_BUY
    if s:
        return SIGN_SELL
    
    return SIGN_WAIT

def MI(N=12):
    '''
        引入两个感知上升强度的指数 MI 和 MICD 用来弥补策略对交易频率和紧张程度的把控
        
        动量指标 MI
        
        表示的是股票价格的涨跌速度，
        如果股票价格能始终不渝地上升则动力指数继续向上发展，就说明股票几个上升的速度在加快。
        反之，如果股票价格始终在下降,则动力指数始终保持在0线的下方。
        如果动力指数继续向下发展，就说明股票价格下降的速度在加快。
        由动力指数的构造特点所决定，它们总能超前于股价的变动而变动，
        当一个即定的趋势尚在持续时，它已经变得平缓了。
        而当现行趋势有所缓和时，它已经开始下降了。
        若趋势了结开始盘整行情时，它便开始在0线附近徘徊了。
        
        A:CLOSE-REF(CLOSE,N);
        MI:SMA(A,N,1);
    '''
    A  = CLOSE - REF(CLOSE, N)
    MI1= SMA(A, N, 1)
    
    return MI1

def MICD(N=3, N1=10, N2=20):
    '''
    
        异同离差动力指数(系统)
        
        公式用法参照 MI 动力指数
        
        如果股票价格能始终向上攀升则该指数就能不断向上发展；
        反之如果股票价格始终在向下，则该指数始终保持在0线的下方。
    　　
        参数自述：
        MI:今收-昨收;
    　　AMI:MI的Param#1日指数移动平均;
    　　DIF:昨日AMI的Param#2日移动平均-昨日AMI的Param#3日移动平均;
      
    　　异同离差动力指数
      
    　　原理：
    　　计算MI动力指数的离差得DIF，再做它的10日移动平均线得MICD。
      
    　　用法：
    　　参考MI动力指数
    　　MI:=CLOSE-REF(CLOSE,1);
    　　AMI:=SMA(MI,N,1);
    　　DIF:MA(REF(AMI,1),N1)-MA(REF(AMI,1),N2),COLORWHITE;
    　　MICD:SMA(DIF,10,1),COLORYELLOW;        
        
        MI1:CLOSE-REF(CLOSE,1);
        AMI:=SMA(MI1,N,1);
        DIF:MA(REF(AMI,1),N1)-MA(REF(AMI,1),N2);
        MICD1:SMA(DIF,10,1)

    '''
    MI1 = CLOSE - REF(CLOSE, 1)
    AMI = SMA(MI1, N, 1)
    DIF = MA(REF(AMI, 1), N1) - MA(REF(AMI, 1), N2)
    MICD1 = SMA(DIF, 10, 1)
    
    return MICD1

def OBV():
    '''
        能量潮指标
        
        该指标通过统计成交量变动的趋势来推测股价趋势。OBV以“N”
        字型为波动单位，并且由许许多多“N”型波构成了OBV的曲线
        图，我们对一浪高于一浪的“N”型波，称其为“上升潮”，至
        于上升潮中的下跌回落则称为“跌潮”（DOWN FIELD）。OBV线
        下降，股价上升，表示买盘无力为卖出信号参考，OBV线上升，股价
        下降时，表示有买盘逢低介入，为买进信号参考，当OBV横向走平超
        过三个月时，需注意随时有大行情出现。
        
        同花顺公式
        
        SUM(IF(CLOSE>REF(CLOSE,1),VOL,IF(CLOSE<REF(CLOSE,1),-VOL,0)),0)/10000
    '''
    # obv = SUM(IF(CLOSE > REF(CLOSE, 1), VOL, IF(CLOSE < REF(CLOSE, 1), -1 * VOL, 0)), 0) / 10000
    a = IF(CLOSE > REF(CLOSE, 1), True, False)
    b = IF(CLOSE < REF(CLOSE, 1), True, False)
    if a:
        obv = SUM(VOL, 1) / 10000
    elif b:
        obv = SUM(VOL, 1) / 10000
    else:
        obv = 0
    return obv

def CCI_SYS(N=14):
    '''
        顺势指标
        
        说明:
        1.CCI 为正值时，视为多头市场；为负值时，视为空头市场；
        2.常态行情时，CCI 波动于±100 的间；强势行情，CCI 会超出±100 ；
        3.CCI>100 时，买进，直到CCI<100 时，卖出；
        4.CCI<-100 时，放空，直到CCI>-100 时，回补。
        
        同花顺公式:
        
        TYP = (IF(ISNULL(HIGH),CLOSE,HIGH) + IF(ISNULL(LOW),CLOSE,LOW) + CLOSE)/3;
        index=(TYP-MA(TYP,N))/(0.015*AVEDEV(TYP,N));
        IF (CROSS(INDEX,N))
        BUY;
        IF (CROSS(N,INDEX))
        SELL;
        
    '''
    TYP = (HIGH + LOW + CLOSE) / 3
    # 此处AVEDEV可能为0值  因此导致出错 +0.0000000000001
    index = (TYP - MA(TYP, N) / (0.015 * AVEDEV(TYP, N) +0.00000001))
    
    b = CROSS(index, N)
    s = CROSS(index, N)
    
    if b:
        return SIGN_BUY
    if s:
        return SIGN_SELL
    return SIGN_WAIT

def ROC_SYS(N=12):
    '''
        变动速率指标
        
        说明:
        当ROC向下跌破零，卖出信号；ROC向上突破零，买入参考信号。股价
        创新高，ROC未配合上升，显示上涨动力减弱。股价创新低，ROC
        未配合下降，显示下跌动力减弱。股价与ROC从低位同时上升，
        短期反弹有望。股价与ROC从高位同时下降，警惕回落。
        
        同花顺 公式
        WROC=(CLOSE-REF(CLOSE,N))/REF(CLOSE,N)*100;
        IF (CROSS(WROC,0))
        BUY;
        IF (CROSS(0,WROC))
        SELL;
    '''
    WROC = (CLOSE - REF(CLOSE, N)) / REF(CLOSE, N) * 100
    b = CROSS(WROC, 0)
    s = CROSS(0, WROC)
    if b:
        return SIGN_BUY
    if s:
        return SIGN_SELL
    return SIGN_WAIT

class BIAS_SYS_Trigger:
    # 乖离率信号触发器 - 代替 BIAS_SYS
    def __init__(self):
        # 间隔日期
        self.d = 30
        self.l = SIGN_WAIT
    # 
    def Trigger(self, M1=6, M2=-3, M3=3, M4=12, M5=24):
        self.d += 1
        b, s = BIAS_SYS(M1=6, M2=-3, M3=3, M4=12, M5=24)
        if b:
            # 如果触发买入信号
            if 1 == self.d and self.l == SIGN_BUY:
                return SIGN_WAIT

            self.d = 0
            self.l = SIGN_BUY
            
            return SIGN_BUY
        if s: 
            if 1 == self.d and self.l == SIGN_SELL:
                return SIGN_WAIT
            
            self.d = 0
            self.l = SIGN_SELL
            
            return SIGN_SELL
        
        if self.d > 45 and self.l == SIGN_BUY:
            # 超期视为无效了
            self.d = 0
            self.l = SIGN_SELL
            return SIGN_SELL
            
        return SIGN_WAIT
    
class MI_DIR(Enum):
    Z       = 1
    F       = 2
    ADD     = 3
    SUB     = 4    
    STRONG  = 5
    WEAK    = 6
    MID     = 7

class MI_3:
    # MI 3 日综合强度评估
    def __init__(self):
        self.mis : np.ndarray = np.zeros(4)
        self.tot = 0
        self.bak_mis :np.ndarray = np.zeros(4)
        self.bak_tot = 0
    
    # 
    def Bak(self):
        self.bak_mis = self.mis.copy()
        self.bak_tot = self.tot
        pass
    
    # 
    def Recover(self):
        self.mis = self.bak_mis.copy()
        self.tot = self.bak_tot
        pass
    
    # 
    def Get(self, mi):
        
        if mi == 0:
            mi = 0.0000001
            
        self.mis[:-1] = self.mis[1:]
        
        self.mis[-1] = mi
        
        self.tot += 1
        
        m1 = self.mis[-1]
        m2 = self.mis[-2]
        m3 = self.mis[-3]
        m4 = self.mis[-4]
        
        if m1 > 0:
            dir = MI_DIR.Z
        else:
            dir = MI_DIR.F
        
        # 各个等级的强度权值为  2, 1,

        # 强度这里用近似 100% 的形式计算
        # 在数学上有待优化
        r1 = 0
        r2 = 0
        r3 = 0
        
        r11 = 0
        r12 = 0
        r13 = 0
        
        if self.tot > 1:
            r1 = ((m1 - m2) / math.fabs(m2)) * 100
            r11= ((m1 - m2) / math.fabs(m2)) * 100
            
        if self.tot > 2:
            r2 = ((m2 - m3) / math.fabs(m3)) * 100
            r12= ((m1 - m3) / math.fabs(m3)) * 100
            
        if self.tot > 3:
            r3 = ((m3 - m4) / math.fabs(m4)) * 100
            r13= ((m1 - m4) / math.fabs(m4)) * 100
        
        if dir == MI_DIR.Z:
            # 正方向
            if m1 >= m2:
                dir2 = MI_DIR.ADD
            else:
                dir2 = MI_DIR.SUB
                
            if r1 >= r2:
                if r1 >= r3:
                    # 加强
                    rank = MI_DIR.STRONG
                else:
                    # 中度
                    rank = MI_DIR.MID
            else:
                if r1 < r3:
                    # 减弱
                    rank = MI_DIR.WEAK
                else:
                    # 中度
                    rank = MI_DIR.MID
        else:
            # 负方向
            if m1 <= m2:
                dir2 = MI_DIR.ADD
            else:
                dir2 = MI_DIR.SUB
                
            if self.tot > 1:
                r1 = ((-m1 - -m2) / math.fabs(m2)) * 100
                r11= ((-m1 - -m2) / math.fabs(m2)) * 100
                
            if self.tot > 2:
                r2 = ((-m2 - -m3) / math.fabs(m3)) * 100
                r12= ((-m1 - -m3) / math.fabs(m3)) * 100
                
            if self.tot > 3:
                r3 = ((-m3 - -m4) / math.fabs(m4)) * 100
                r13= ((-m1 - -m4) / math.fabs(m4)) * 100                
                
            # r1 = -r1
            # r2 = -r2
            # r3 = -r3
            
            # r11 = -r11
            # r12 = -r12
            # r13 = -r13

            if r1 >= r2:
                if r1 >= r3:
                    # 加强
                    rank = MI_DIR.STRONG
                else:
                    # 中度
                    rank = MI_DIR.MID
            else:
                if r1 < r3:
                    # 减弱
                    rank = MI_DIR.WEAK
                else:
                    # 中度
                    rank = MI_DIR.MID
                    
        avg = (r1 + r2 + r3) / 3
        
        lev = (r11 + r12 + r13) / 3
            
        return dir, dir2, rank, r1, r2, r3, lev, avg