# -*- coding: utf-8 -*-

# 绝对引用指定目录中的模块
import sys
sys.path.insert(0,r'S:\siat\siat')
from fund_china import *

df=security_price("180801.SZ",'2021-7-1','2021-10-15')


df1=fund_stock_holding_compare_china('005827','2021Q1','2021Q2')
df2=fund_stock_holding_rank_china('005827')


df=reits_profile_china()
df=reits_profile_china(top = 3)
df=reits_profile_china(top = -3)
df=reits_profile_china('508056')


#==============================================================================
from siat.translate import *

#==============================================================================
from siat import *
df=oef_rank_china('单位净值','全部类型')
set(list(df['基金类型'])) #基金类别列表
set(list(df['基金代码'])) #基金个数
df=oef_trend_china('180801','2020-1-1','2021-9-30',"收益率")

import akshare as ak
df = ak.fund_em_open_fund_info(fund="710001", indicator="累计收益率走势")
df=oef_trend_china('710001','2020-1-1','2021-9-30',"收益率")
#==============================================================================
df=oef_trend_china('000592','2021-1-1','2021-3-31',trend_type='收益率',power=5)

df=mmf_trend_china('320019','2020-7-1','2020-9-30',power=1)

df=oef_trend_china('000595','2019-1-1','2020-12-31',trend_type='净值')
df=oef_trend_china('000592','2021-1-1','2021-3-31',trend_type='收益率',power=5)
df=oef_trend_china('050111','2020-9-1','2020-9-30',trend_type='排名')
df=mmf_trend_china('320019','2020-7-1','2020-9-30',power=3)
df=etf_trend_china('510580','2019-1-1','2020-9-30')

#==============================================================================

df=oef_rank_china('单位净值','全部类型')


df=pof_list_china()


df=oef_rank_china('单位净值','全部类型')
df=oef_rank_china('累计净值','全部类型')
df=oef_rank_china('手续费','全部类型')


df=oef_rank_china('单位净值','股票型')
df=oef_rank_china('累计净值','股票型')


df=oef_rank_china('单位净值','债券型')
df=oef_rank_china('累计净值','债券型')

df=oef_trend_china('519035','2019-1-1','2020-10-16',trend_type='净值')

df=oef_trend_china('519035','2020-5-1','2020-10-16',trend_type='收益率',power=5)

df=oef_trend_china('519035','2020-9-1','2020-9-30',trend_type='排名')


df=oef_trend_china('000595','2019-1-1','2020-10-16',trend_type='净值')
df=oef_trend_china('000592','2020-7-1','2020-9-30',trend_type='收益率',power=5)
df=oef_trend_china('050111','2020-9-1','2020-9-30',trend_type='排名')

df = ak.fund_em_money_fund_daily()
df = mmf_rank_china()

df=mmf_trend_china('320019','2020-7-1','2020-9-30',power=1)

amac_member_list=list(set(list(amac_member_info_df['机构类型'])))

df=etf_rank_china(info_type='单位净值',fund_type='全部类型')
df=etf_rank_china(info_type='累计净值')
df=etf_trend_china('510580','2019-1-1','2020-9-30')


from siat.fund_china import *
df=fund_summary_china()

df=pef_manager_china()
df=pef_manager_china("广东省")
df=pef_manager_china("上海市")
df=pef_manager_china("北京市")
df=pef_product_china()






