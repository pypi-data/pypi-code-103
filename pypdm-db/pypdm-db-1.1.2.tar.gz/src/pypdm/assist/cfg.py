#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# @Time   : 2020/4/28 21:56
# @File   : env.py
# -----------------------------------------------

import os
PRJ_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

CHARSET = 'utf-8'
ENCODING = 'utf8'
MYSQL = 'mysql'
SQLITE = 'sqlite'


BEAN_TPL = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# PDM: @{table_name}
# -------------------------------

class @{TableName} :
    table_name = '@{table_name}'
@{columns}


    def __init__(self) :
@{variables}


    def params(self) :
        return (
@{params}
        )


    def __repr__(self) :
        return '\\n'.join(
            (
                '%s: {' % self.table_name,
@{kvs}
                '}\\n'
            )
        )
'''


DAO_TPL = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# DAO: @{table_name}
# -------------------------------

from ..bean.@{table_name} import @{TableName}
from pypdm.dao._base import BaseDao


class @{TableName}Dao(BaseDao) :
    TABLE_NAME = '@{table_name}'
    SQL_COUNT = 'select count(1) from @{table_name}'
    SQL_TRUNCATE = 'truncate table @{table_name}'
    SQL_INSERT = '@{insert}'
    SQL_DELETE = 'delete from @{table_name} where 1 = 1 '
    SQL_UPDATE = '@{update}'
    SQL_SELECT = '@{select}'

    def __init__(self) :
        BaseDao.__init__(self)

    def _to_bean(self, row) :
        bean = None
        if row:
            bean = @{TableName}()
@{set_values}
        return bean
'''