#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# @Time   : 2020/8/31 10:10
# @File   : _pdm.py
# -----------------------------------------------

import re
import string
from .assist.cfg import *
from .assist.num import *
from .assist import log


class PDM :

    def __init__(self, dbc, pdm_pkg) :
        self.dbc = dbc
        self.pdm_pkg = pdm_pkg
        pdm_path = pdm_pkg.replace('.', '/')
        self.bean_pkg_path = '%s/bean/' % pdm_path
        self.dao_pkg_path = '%s/dao/' % pdm_path
        self.is_mysql = (self.dbc.dbtype() == MYSQL)


    def to_pdm(self, table_whitelist, table_blacklist) :
        conn = self.dbc.conn()
        if not table_whitelist :
            table_whitelist = self._get_all_tables(conn)
        if not table_blacklist :
            table_blacklist = []
        log.info('目标数据表清单：{\n\t%s\n}' % '\n\t'.join(table_whitelist))

        paths = []
        for table_name in table_whitelist :
            if table_name in table_blacklist :
                continue

            columns = self._get_columns(conn, table_name)
            bean_file_content = self._to_beans(table_name, columns)
            path = self._save(bean_file_content, self.bean_pkg_path, table_name, '.py')
            paths.append(path)

            dao_file_content = self._to_daos(table_name, columns)
            path = self._save(dao_file_content, self.dao_pkg_path, table_name, '.py')
            paths.append(path)

        self.dbc.close()
        return paths


    def _get_all_tables(self, conn) :
        tables = []
        try:
            sql = 'show tables' if self.is_mysql else \
                'select name from sqlite_master where type="table" order by name'
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                if self.is_mysql :
                    table_name = row[0].encode(CHARSET)
                else :
                    table_name = row[0]
                    if table_name == 'sqlite_sequence' :    # sqlite 内置自增序列表
                        continue
                tables.append(byte_to_str(table_name))
            cursor.close()
        except:
            log.error("查询 table 列表失败")
        return tables


    def _get_columns(self, conn, table_name) :
        cursor = conn.cursor()
        cursor.execute('select * from %s limit 0' % table_name)
        columns = [tuple[0] for tuple in cursor.description]
        log.debug('已获取数据表 [%s] 的列名集： %s' % (table_name, columns))
        cursor.close()
        return columns


    def _to_beans(self, table_name, columns) :
        log.debug('正在构造数据表 [%s] 的 Bean 文件' % table_name)
        tpl = DBTemplate(BEAN_TPL)
        variables = list(map(self._to_var, columns))
        placeholders = {
            '{table_name}': table_name,
            '{TableName}': self._to_camel(table_name),
            '{columns}': '\n'.join(list(map((lambda col: '\t%s = "%s"' % (col, col)), columns))),
            '{variables}': '\n'.join(list(map((lambda col: '\t\tself.%s = None' % col), variables))),
            '{params}': '\n'.join(list(('\t\t\tself.%s,' % col) for col in variables[1:])),
            '{kvs}': '\n'.join(list(map(self._to_kv, columns)))
        }
        return tpl.safe_substitute(placeholders).replace('\t', '    ')


    def _to_camel(self, underline) :
        camel = ''
        if isinstance(underline, str) :
            for word in underline.split('_') :
                camel += word.capitalize()
        return camel


    def _to_var(self, col) :
        return re.sub(r'^[a-zA-Z]_', '', col)


    def _to_kv(self, col) :
        return '\t\t\t\t"\t%s = %s" % (self.' + col + ', self.' + self._to_var(col) + '),'


    def _to_daos(self, table_name, columns) :
        log.debug('正在构造数据表 [%s] 的 DAO 文件' % table_name)
        tpl = DBTemplate(DAO_TPL)
        placeholders = {
            # '{pkg_path}': self.pdm_pkg,
            '{table_name}': table_name,
            '{TableName}': self._to_camel(table_name),
            '{insert}': self._to_insert(table_name, columns),
            '{update}': self._to_update(table_name, columns),
            '{select}': self._to_select(table_name, columns),
            '{set_values}': '\n'.join(('\t\t\tbean.%s = self._to_val(row, %i)' % (self._to_var(col), idx)) for idx, col in enumerate(columns))
        }
        return tpl.safe_substitute(placeholders).replace('\t', '    ')


    def _to_insert(self, table_name, columns) :
        cols = ', '.join(columns[1:])
        if self.is_mysql :
            vars = 's, %' * (len(columns) - 2)
            sql = 'insert into ' + table_name + '(' + cols + ') values(%' + vars + 's)'
        else :
            vars = ', ?' * (len(columns) - 2)
            sql = 'insert into ' + table_name + '(' + cols + ') values(?' + vars + ')'
        return sql


    def _to_update(self, table_name, columns) :
        cols = ', '.join(list(map(
            (lambda col: col + ' = ' + ('%s' if self.is_mysql else '?')),
            columns[1:]
        )))
        return 'update ' + table_name + ' set ' + cols + ' where 1 = 1 '


    def _to_select(self, table_name, columns) :
        sql = 'select %s from ' + table_name + ' where 1 = 1 '
        return sql % (', '.join(columns))


    def _save(self, content, filedir, filename, suffix) :
        '''
        写入 PDM 文件
        :param content: 文件内容
        :param filedir: 存储目录
        :param filename: 文件名
        :param suffix: 文件后缀
        :return: PDM 文件路径
        '''
        if not os.path.exists(filedir) :
            os.makedirs(filedir)
            self._create_init_py(filedir)

        path = '%s%s%s' % (filedir, filename, suffix)
        with open(path, 'w+', encoding=CHARSET) as file :
            file.write(content)
        return path


    def _create_init_py(self, pkg_dir) :
        '''
        在包目录的每一层创建 __init__.py 文件
        :param pkg_dir: 包目录
        '''
        dir = pkg_dir
        while dir :
            initpy_path = '%s/__init__.py' % dir
            with open(initpy_path, 'w+', encoding=CHARSET) as file : file.write('')
            dir = os.path.dirname(dir)



class DBTemplate(string.Template) :
    delimiter = '@'
    idpattern = r'\{\w+\}'
