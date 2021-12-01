# -*- encoding: utf-8 -*-
'''
@文件    :__init__.py
@说明    :
@时间    :2020/09/02 16:27:09
@作者    :caimmy@hotmail.com
@版本    :0.1
'''


from .flowapp import KaruoFlow
from .db.tables import InitKaruoflowTables
from .datadef import DbConfig

'''
@version 0.6 [2021-05-26] 增加会签、加签(InsertSign)、转签(AddSign)等功能
@version 0.7 [2021-06-10] 增加直接转入下一阶段的功能，供业务层决定阶段变更
@version 0.8 [2021-06-15] 审批接口 AgreeJobFlow_V2 增加手写签名参数
@version 0.9 [2021-08-26] 支持同一个审核人的连续审批
@version 0.91 [2021-09-25] 修复连续审批过程中的一个bug，当连续审批遇到会签阶段时，需要跳出循环，避免循环死锁
@version 0.92, 0.93 [2021-09-25] 优化报错信息
@version 1.0 [2021-09-25] 支持查询指定流程指定阶段的决策记录
@version 1.1 [2021-09-28] 修正会签处理bug(避免会签阶段审核人反复审签)
@version 1.2 [2021-09-30] 增加接口，修改审批任务当前审批人列表
@version 1.21 [2021-10-12] 修复根据yml模板初始话流程的bug
@version 1.22 [2021-10-18] 增加 QueryJobViaRelationPrimaryKey 接口，已审核数据增加除重
@version 1.23 [2021-10-18] 增加 QueryJobViaRelationPrimaryKey 接口，已审核数据增加除重
@version 1.24 [2021-12-01] 修复bug，获取待审核列表时，排序未生效
'''

__version__ = 1.24