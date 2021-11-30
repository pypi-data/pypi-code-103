# -*- coding: utf-8 -*-
#  数据库相关包,用于安全模式下混淆SQL(比如将敏感的参数信息匿名化,以便保护敏感信息),SQL执行计划

import logging
import re
import weakref

import fast_tracker.packages.six as six
from fast_tracker.core.config import global_settings

_logger = logging.getLogger(__name__)

# 模糊化SQL,以便保护敏感信息,模糊化的地方包括:带引号的字符串,整数,浮点数,带?的文字

_single_quotes_p = r"'(?:[^']|'')*?(?:\\'.*|'(?!'))"  # 单引号正则
_double_quotes_p = r'"(?:[^"]|"")*?(?:\\".*|"(?!"))'  # 双引号正则
_dollar_quotes_p = r'(\$(?!\d)[^$]*?\$).*?(?:\1|$)'  # 带$的
_oracle_quotes_p = r"q'\[.*?(?:\]'|$)|q'\{.*?(?:\}'|$)| q'\<.*?(?:\>'|$)|q'\(.*?(?:\)'|$)"
_any_quotes_p = _single_quotes_p + '|' + _double_quotes_p
_single_dollar_p = _single_quotes_p + '|' + _dollar_quotes_p
_single_oracle_p = _single_quotes_p + '|' + _oracle_quotes_p

_single_quotes_re = re.compile(_single_quotes_p)
_any_quotes_re = re.compile(_any_quotes_p)
_single_dollar_re = re.compile(_single_dollar_p)
_single_oracle_re = re.compile(_single_oracle_p)

_single_quotes_cleanup_p = r"'"
_any_quotes_cleanup_p = r'\'|"'
_single_dollar_cleanup_p = r"'|\$(?!\?)"

_any_quotes_cleanup_re = re.compile(_any_quotes_cleanup_p)
_single_quotes_cleanup_re = re.compile(_single_quotes_cleanup_p)
_single_dollar_cleanup_re = re.compile(_single_dollar_cleanup_p)

_uuid_p = r'\{?(?:[0-9a-f]\-?){32}\}?'  # UUID 正则
_int_p = r'(?<!:)-?\b(?:[0-9]+\.)?[0-9]+(e[+-]?[0-9]+)?'  # 整数正则
_hex_p = r'0x[0-9a-f]+'  # 16进制正则
_bool_p = r'\b(?:true|false|null)\b'  # bool 正则

_all_literals_p = '(' + ')|('.join([_uuid_p, _hex_p, _int_p, _bool_p]) + ')'
_all_literals_re = re.compile(_all_literals_p, re.IGNORECASE)

_quotes_table = {
    'single': (_single_quotes_re, _single_quotes_cleanup_re),
    'single+double': (_any_quotes_re, _any_quotes_cleanup_re),
    'single+dollar': (_single_dollar_re, _single_dollar_cleanup_re),
    'single+oracle': (_single_oracle_re, _single_quotes_cleanup_re),
}


def _obfuscate_sql(sql, database):
    """

    :param sql:
    :param SQLDatabase database :
    :return:
    """
    quotes_re, quotes_cleanup_re = _quotes_table.get(database.quoting_style,
                                                     (_single_quotes_re, _single_quotes_cleanup_re))
    sql = quotes_re.sub('?', sql)  # 正则替换成问号
    sql = _all_literals_re.sub('?', sql)
    if quotes_cleanup_re.search(sql):
        sql = '?'
    return sql


#  完成SQL的规范化,对应两个仅参数值不同的SQL,规范化后,他们的哈希值应该是一样的
#  我们需要解决的问题
#  1. 哪里的值是可变参数值 2. 找出所有空格并规范化

# 这块就是匹配Python字符串拼接的集中方式的写法
_normalize_params_1_p = r'%\([^)]*\)s'  # 对于参数化的SQL,正则匹配出命名参数
_normalize_params_1_re = re.compile(_normalize_params_1_p)
_normalize_params_2_p = r'%s'  # 对于参数化的SQL,正则匹配出顺序参数
_normalize_params_2_re = re.compile(_normalize_params_2_p)
_normalize_params_3_p = r':\w+'  # 对于参数化的SQL,正则匹配出
_normalize_params_3_re = re.compile(_normalize_params_3_p)
_normalize_values_p = r'\([^)]+\)'  # 正则匹配出具体值
_normalize_values_re = re.compile(_normalize_values_p)
_normalize_whitespace_1_p = r'\s+'  # 正则匹配出空格
_normalize_whitespace_1_re = re.compile(_normalize_whitespace_1_p)
_normalize_whitespace_2_p = r'\s+(?!\w)'
_normalize_whitespace_2_re = re.compile(_normalize_whitespace_2_p)
_normalize_whitespace_3_p = r'(?<!\w)\s+'
_normalize_whitespace_3_re = re.compile(_normalize_whitespace_3_p)


def _normalize_sql(sql):
    #  规范化SQL,用于求SQL的标识符
    sql = _normalize_params_1_re.sub('?', sql)
    sql = _normalize_values_re.sub('(?)', sql)
    sql = _normalize_params_2_re.sub('?', sql)
    sql = _normalize_params_3_re.sub('?', sql)
    sql = sql.strip()
    sql = _normalize_whitespace_1_re.sub(' ', sql)
    sql = _normalize_whitespace_2_re.sub('', sql)
    sql = _normalize_whitespace_3_re.sub('', sql)

    return sql


_identifier_re = re.compile(r'[\',"`\[\]\(\)]*')  # 标识符的正则匹配格式


def _extract_identifier(token):
    return _identifier_re.sub('', token).strip().lower()


_uncomment_sql_p = r'(?:#|--).*?(?=\r|\n|$)'
_uncomment_sql_q = r'\/\*(?:[^\/]|\/[^*])*?(?:\*\/|\/\*.*)'
_uncomment_sql_x = r'(%s)|(%s)' % (_uncomment_sql_p, _uncomment_sql_q)
_uncomment_sql_re = re.compile(_uncomment_sql_x, re.DOTALL)


def _uncomment_sql(sql):
    #  替换掉SQL中的注释
    return _uncomment_sql_re.sub('', sql)


def _parse_default(sql, regex):
    match = regex.search(sql)
    return match and _extract_identifier(match.group(1)) or ''


#  各种可能影响到标识符计算的正则规则
_parse_identifier_1_p = r'"((?:[^"]|"")+)"(?:\."((?:[^"]|"")+)")?'
_parse_identifier_2_p = r"'((?:[^']|'')+)'(?:\.'((?:[^']|'')+)')?"
_parse_identifier_3_p = r'`((?:[^`]|``)+)`(?:\.`((?:[^`]|``)+)`)?'
_parse_identifier_4_p = r'\[\s*(\S+)\s*\]'
_parse_identifier_5_p = r'\(\s*(\S+)\s*\)'
_parse_identifier_6_p = r'\{\s*(\S+)\s*\}'
_parse_identifier_7_p = r'([^\s\(\)\[\],]+)'

_parse_identifier_p = ''.join(('(', _parse_identifier_1_p, '|',
                               _parse_identifier_2_p, '|', _parse_identifier_3_p, '|',
                               _parse_identifier_4_p, '|', _parse_identifier_5_p, '|',
                               _parse_identifier_6_p, '|', _parse_identifier_7_p, ')'))

_parse_from_p = r'\s+FROM\s+' + _parse_identifier_p  # 解析出FROM 后面的表名
_parse_from_re = re.compile(_parse_from_p, re.IGNORECASE)


def _join_identifier(m):
    """

    :param re.Pattern m:
    :return:
    """
    return m and '.'.join([s for s in m.groups()[1:] if s]).lower() or ''


def _parse_select(sql):
    # 解析出FROM 后面的表面,对于子查询忽略
    return _join_identifier(_parse_from_re.search(sql))


def _parse_delete(sql):
    return _join_identifier(_parse_from_re.search(sql))


_parse_into_p = r'\s+INTO\s+' + _parse_identifier_p  # 解析INTO后面的表名
_parse_into_re = re.compile(_parse_into_p, re.IGNORECASE)


def _parse_insert(sql):
    """
    解析出INTO 后面的表名
    """
    return _join_identifier(_parse_into_re.search(sql))


_parse_update_p = r'\s*UPDATE\s+' + _parse_identifier_p  #  解析出Update
_parse_update_re = re.compile(_parse_update_p, re.IGNORECASE)


def _parse_update(sql):
    return _join_identifier(_parse_update_re.search(sql))


_parse_table_p = r'\s+TABLE\s+' + _parse_identifier_p
_parse_table_re = re.compile(_parse_table_p, re.IGNORECASE)


def _parse_create(sql):
    return _join_identifier(_parse_table_re.search(sql))


def _parse_drop(sql):
    return _join_identifier(_parse_table_re.search(sql))


_parse_call_p = r'\s*CALL\s+(?!\()(\w+(\.\w+)*)'
_parse_call_re = re.compile(_parse_call_p, re.IGNORECASE)


def _parse_call(sql):
    return _parse_default(sql, _parse_call_re)


_parse_show_p = r'\s*SHOW\s+(.*)'
_parse_show_re = re.compile(_parse_show_p, re.IGNORECASE | re.DOTALL)


def _parse_show(sql):
    return _parse_default(sql, _parse_show_re)


_parse_set_p = r'\s*SET\s+(.*?)\W+.*'
_parse_set_re = re.compile(_parse_set_p, re.IGNORECASE | re.DOTALL)


def _parse_set(sql):
    return _parse_default(sql, _parse_set_re)


_parse_exec_p = r'\s*EXEC\s+(?!\()(\w+)'
_parse_exec_re = re.compile(_parse_exec_p, re.IGNORECASE)


def _parse_exec(sql):
    return _parse_default(sql, _parse_exec_re)


_parse_execute_p = r'\s*EXECUTE\s+(?!\()(\w+)'
_parse_execute_re = re.compile(_parse_execute_p, re.IGNORECASE)


def _parse_execute(sql):
    return _parse_default(sql, _parse_execute_re)


_parse_alter_p = r'\s*ALTER\s+(?!\()(\w+)'
_parse_alter_re = re.compile(_parse_alter_p, re.IGNORECASE)


def _parse_alter(sql):
    return _parse_default(sql, _parse_alter_re)


#  SQL的操作类型,这个SQL语句是查询操作,是插入操作还是其它
_operation_table = {
    'select': _parse_select,
    'delete': _parse_delete,
    'insert': _parse_insert,
    'update': _parse_update,
    'create': None,
    'drop': None,
    'call': _parse_call,
    'show': None,
    'set': None,
    'exec': None,
    'execute': None,
    'alter': None,
    'commit': None,
    'rollback': None,
}

_parse_operation_p = r'(\w+)'
_parse_operation_re = re.compile(_parse_operation_p)


def _parse_operation(sql):
    #  解析SQL操作类型
    match = _parse_operation_re.search(sql)
    operation = match and match.group(1).lower() or ''
    return operation if operation in _operation_table else ''


def _parse_target(sql, operation):
    #  获得操作的目标(表)
    sql = sql.rstrip(';')
    parse = _operation_table.get(operation, None)
    return parse and parse(sql) or ''


_explain_plan_postgresql_re_1_mask_false = re.compile(
    r"""((?P<double_quotes>"[^"]*")|"""
    r"""(?P<single_quotes>'([^']|'')*')|"""
    r"""(?P<cost_analysis>\(cost=[^)]*\))|"""
    r"""(?P<sub_plan_ref>\bSubPlan\s+\d+\b)|"""
    r"""(?P<init_plan_ref>\bInitPlan\s+\d+\b)|"""
    r"""(?P<dollar_var_ref>\$\d+\b)|"""
    r"""(?P<numeric_value>(?<![\w])[-+]?\d*\.?\d+([eE][-+]?\d+)?\b))""")

_explain_plan_postgresql_re_1_mask_true = re.compile(
    r"""((?P<double_quotes>"[^"]*")|"""
    r"""(?P<single_quotes>'([^']|'')*'))""")

_explain_plan_postgresql_re_2 = re.compile(
    r"""^(?P<label>[^:]*:\s+).*$""", re.MULTILINE)


def _obfuscate_explain_plan_postgresql_substitute(text, mask):
    # 用替换的方式模糊化postgrepsql的执行计划

    def replacement(matchobj):
        for name, value in list(matchobj.groupdict().items()):
            if value is not None:
                if name in ('numeric_value', 'single_quotes'):
                    return '?'
                return value

    if mask:
        return _explain_plan_postgresql_re_1_mask_true.sub(replacement, text)
    else:
        return _explain_plan_postgresql_re_1_mask_false.sub(replacement, text)


def _obfuscate_explain_plan_postgresql(columns, rows, mask=None):
    settings = global_settings()

    if mask is None:
        mask = (settings.debug.explain_plan_obfuscation == 'simple')

    if len(columns) != 1:
        return None

    text = '\n'.join(item[0] for item in rows)
    text = _obfuscate_explain_plan_postgresql_substitute(text, mask)
    if mask:
        text = _explain_plan_postgresql_re_2.sub(r'\g<label>?', text)

    rows = [(_,) for _ in text.split('\n')]

    return columns, rows


_obfuscate_explain_plan_table = {
    'Postgres': _obfuscate_explain_plan_postgresql
}


def _obfuscate_explain_plan(database, columns, rows):
    """

    :param SQLDatabase database:
    :param columns:
    :param rows:
    :return:
    """
    # 根据不同的数据库,获取对应的SQL执行计划
    obfuscator = _obfuscate_explain_plan_table.get(database.product)
    if obfuscator:
        return obfuscator(columns, rows)
    return columns, rows


class SQLConnection(object):

    def __init__(self, database, connection):
        self.database = database
        self.connection = connection
        self.cursors = {}

    def cursor(self, args=(), kwargs={}):
        key = (args, frozenset(kwargs.items()))

        cursor = self.cursors.get(key)

        if cursor is None:
            settings = global_settings()

            if settings.debug.log_explain_plan_queries:
                _logger.debug('为%r创建数据库连接游标.',
                              self.database.client)

            cursor = self.connection.cursor(*args, **kwargs)
            self.cursors[key] = cursor

        return cursor

    def cleanup(self):
        settings = global_settings()

        if settings.debug.log_explain_plan_queries:
            _logger.debug('为%r清空数据库连接.',
                          self.database)

        try:
            self.connection.rollback()
            pass
        except (AttributeError, self.database.NotSupportedError):
            pass

        self.connection.close()


class SQLConnections(object):

    def __init__(self, maximum=4):
        self.connections = []
        self.maximum = maximum

        settings = global_settings()

        if settings.debug.log_explain_plan_queries:
            _logger.debug('创建连接缓存%r.', self)

    def connection(self, database, args, kwargs):
        """
        :param SQLDatabase database:
        :param args:
        :param kwargs:
        :return:
        """
        key = (database.client, args, kwargs)

        connection = None

        settings = global_settings()

        for i, item in enumerate(self.connections):
            if item[0] == key:
                connection = item[1]
                item = self.connections.pop(i)
                self.connections.append(item)

                break

        if connection is None:

            if len(self.connections) == self.maximum:
                connection = self.connections.pop(0)[1]
                if settings.debug.log_explain_plan_queries:
                    _logger.debug('为%r删除数据库连接,因为已经达到连接最大值%r.', connection.database.client, self.maximum)
                connection.cleanup()
            connection = SQLConnection(database, database.connect(*args, **kwargs))
            self.connections.append((key, connection))
            if settings.debug.log_explain_plan_queries:
                _logger.debug('为%r创建数据库连接.', database.client)

        return connection

    def cleanup(self):
        settings = global_settings()

        if settings.debug.log_explain_plan_queries:
            _logger.debug('清空数据库连接缓存%r.', self)

        for key, connection in self.connections:
            connection.cleanup()

        self.connections = []

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        self.cleanup()


def _query_result_dicts_to_tuples(columns, rows):
    if not columns or not rows:
        return None

    return [tuple([row[col] for col in columns]) for row in rows]


def _could_be_multi_query(sql):
    #  判断是不是多条查询语句
    return sql.rstrip().rstrip(';').count(';') > 0


def _explain_plan(connections, sql, database, connect_params, cursor_params,
                  sql_parameters, execute_params):
    """
    # 获取执行计划
    :param connections: 连接池
    :param sql:   用户的查询SQL
    :param database:  SQLDatabase对象,用户使用的数据库信息
    :param connect_params:  连接参数
    :param cursor_params:
    :param sql_parameters:
    :param execute_params:
    :return:

    """

    settings = global_settings()

    if _could_be_multi_query(sql):
        if settings.debug.log_explain_plan_queries:
            _logger.debug('SQL语句:%r  在%r上不执行查询计划,因为查询语句有分号.', sql, database.client)
        else:
            _logger.debug('在%r上不执行查询计划,因为查询语句有分号.', database.client)
        return None
    query = '%s %s' % (database.explain_query, sql)  # 拼接执行查询语句计划SQL
    if settings.debug.log_explain_plan_queries:
        _logger.debug('正在提交查询计划 %r在%r上.', query, database.client)
    try:
        args, kwargs = connect_params
        connection = connections.connection(database, args, kwargs)

        if cursor_params is not None:
            args, kwargs = cursor_params
            cursor = connection.cursor(args, kwargs)
        else:
            cursor = connection.cursor()

        if execute_params is not None:
            args, kwargs = execute_params
        else:
            args, kwargs = ((), {})

        if sql_parameters is not None:
            cursor.execute(query, sql_parameters, *args, **kwargs)
        else:
            cursor.execute(query, **kwargs)

        columns = []

        if cursor.description:
            for column in cursor.description:
                columns.append(column[0])
        rows = cursor.fetchall()
        if settings.debug.log_explain_plan_queries:
            _logger.debug('执行计划行数据类型: %r',
                          rows and type(rows[0]))

        if rows and isinstance(rows[0], dict):
            rows = _query_result_dicts_to_tuples(columns, rows)

        if not columns and not rows:
            return None
        return columns, rows
    except Exception:
        if settings.debug.log_explain_plan_queries:
            _logger.exception('SQL语句: %r 在 %r 上执行查询计划时失败,参数如下:cursor_params=%r and '
                              'execute_params=%r.', query, database.client,
                              cursor_params, execute_params)
    return None


def explain_plan(connections, sql_statement, connect_params, cursor_params,
                 sql_parameters, execute_params, sql_format):
    if connect_params is None:
        return

    database = sql_statement.database

    if sql_statement.operation not in database.explain_stmts:
        # 如果SQL的执行操作不在范围呢,不执行计查询划任务
        return

    details = _explain_plan(connections, sql_statement.sql, database,
                            connect_params, cursor_params, sql_parameters, execute_params)
    if details is not None and sql_format != 'raw':
        return _obfuscate_explain_plan(database, *details)

    return details


class SQLDatabase(object):

    def __init__(self, dbapi2_module):
        self.dbapi2_module = dbapi2_module

    def __getattr__(self, name):
        return getattr(self.dbapi2_module, name)

    @property
    def product(self):
        return getattr(self.dbapi2_module, '_nr_database_product', None)

    @property
    def client(self):
        #  获取模块名称
        name = getattr(self.dbapi2_module, '__name__', None)
        if name is None:
            name = getattr(self.dbapi2_module, '__file__', None)
        if name is None:
            name = str(self.dbapi2_module)
        return name

    @property
    def quoting_style(self):
        # 是单引号风格还是双引号风格还是都有
        result = getattr(self.dbapi2_module, '_nr_quoting_style', None)

        if result is None:
            result = 'single'

        return result

    @property
    def explain_query(self):
        # 执行计划的语句,比如EXPLAIN,每种数据库的执行查询计划的关键字不同
        return getattr(self.dbapi2_module, '_nr_explain_query', None)

    @property
    def explain_stmts(self):
        result = getattr(self.dbapi2_module, '_nr_explain_stmts', None)

        if result is None:
            result = ()

        return result


class SQLStatement(object):
    """
     SQL报告,根据用户使用的sql查询语句及数据库类型,经过一系列操作后得到的SQL报告,包括用什么类型的数据库,原始SQL,模糊化后的SQL,统一后的SQL,
    唯一标识符,执行的操作(是SELECT,DELETE,update等等)
    """

    def __init__(self, sql, database=None):
        self._operation = None
        self._target = None
        self._uncommented = None
        self._obfuscated = None
        self._normalized = None
        self._identifier = None  # SQL 唯一标识符

        if isinstance(sql, six.binary_type):
            try:
                sql = sql.decode('utf-8')
            except UnicodeError as e:
                settings = global_settings()
                if settings.debug.log_explain_plan_queries:
                    _logger.debug('解码SQL时发生错误,SQL语句: %s' % e.reason)

                self._operation = ''
                self._target = ''
                self._uncommented = ''
                self._obfuscated = ''
                self._normalized = ''

        self.sql = sql
        self.database = database

    @property
    def operation(self):
        if self._operation is None:
            self._operation = _parse_operation(self.uncommented)
        return self._operation

    @property
    def target(self):
        if self._target is None:
            self._target = _parse_target(self.uncommented, self.operation)
        return self._target

    @property
    def uncommented(self):
        if self._uncommented is None:
            self._uncommented = _uncomment_sql(self.sql)
        return self._uncommented

    @property
    def obfuscated(self):
        if self._obfuscated is None:
            self._obfuscated = _uncomment_sql(_obfuscate_sql(self.sql,
                                                             self.database))
        return self._obfuscated

    @property
    def normalized(self):
        if self._normalized is None:
            self._normalized = _normalize_sql(self.obfuscated)
        return self._normalized

    @property
    def identifier(self):
        if self._identifier is None:
            self._identifier = hash(self.normalized)
        return self._identifier

    def formatted(self, sql_format):
        # 格式化后的SQL,根据安全等级来
        if sql_format == 'off':
            return ''

        elif sql_format == 'raw':
            return self.sql

        else:
            return self.obfuscated


_sql_statements = weakref.WeakValueDictionary()


def sql_statement(sql, dbapi2_module):

    key = (sql, dbapi2_module)

    result = _sql_statements.get(key, None)

    if result is not None:
        return result

    database = SQLDatabase(dbapi2_module)
    result = SQLStatement(sql, database)

    _sql_statements[key] = result

    return result
