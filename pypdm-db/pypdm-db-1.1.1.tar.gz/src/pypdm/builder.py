#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# @Time   : 2020/8/30 15:13
# @File   : pypdm.py
# -----------------------------------------------


from .dbc._mysql import MysqlDBC
from .dbc._sqlite import SqliteDBC
from ._pdm import *



def build_deprecated(
        dbtype = 'sqlite',
        host = '127.0.0.1',
        port = 3306,
        username = 'root',
        password = '123456',
        dbname = 'test',
        charset = CHARSET,
        pdm_pkg = 'src.pdm',
        table_whitelist = [],
        table_blacklist = [],
        to_log = False
    ) :
    '''
    构造指定数据库的 PDM 对象文件（不再推荐使用）
    :param dbtype: 数据库类型，只支持 sqlite 或 mysql
    :param host: 数据库 IP
    :param port: 数据库端口
    :param username: 登陆账号
    :param password: 登陆密码
    :param dbname: 数据库名称 / 数据库路径
    :param charset: 数据库编码
    :param pdm_pkg: 期望生成 PDM 文件的包路径
    :param table_whitelist: 要生成哪些表的 PDM 文件（默认所有表）
    :param table_blacklist: 不生成哪些表的 PDM 文件
    :param to_log: 是否启用内部日志
    :return:
    '''
    dbc = _connect_to_db(dbtype, host, port, username, password, dbname, charset)
    return build(dbc, pdm_pkg, table_whitelist, table_blacklist, to_log)



def build(
        dbc = None, 
        pdm_pkg = 'src.pdm',
        table_whitelist = [],
        table_blacklist = [],
        to_log = False
    ) :
    '''
    构造指定数据库的 PDM 对象文件
    :param dbc: 数据库连接对象
    :param pdm_pkg: 期望生成 PDM 文件的包路径
    :param table_whitelist: 要生成哪些表的 PDM 文件（默认所有表）
    :param table_blacklist: 不生成哪些表的 PDM 文件
    :param to_log: 是否启用内部日志
    :return:
    '''
    if to_log :
        log.init()

    paths = []
    if dbc :
        log.info('正在构造数据表 PDM ...')
        pdm = PDM(dbc, pdm_pkg)
        paths.extend(pdm.to_pdm(table_whitelist, table_blacklist))
        log.info('构造 PDM 完成，生成文件路径如下：{\n\t%s\n}' % '\n\t'.join(paths))
    return paths



def _connect_to_db(dbtype, host, port, username, password, dbname, charset) :
    '''
    根据数据库类型获取数据库连接对象
    :param dbtype: 数据库类型，只支持 sqlite 或 mysql
    :param host: 数据库 IP
    :param port: 数据库端口
    :param username: 登陆账号
    :param password: 登陆密码
    :param dbname: 数据库名称 / 数据库路径
    :param charset: 数据库编码
    :return: 数据库连接对象
    '''
    if dbtype.lower() == SQLITE :
        log.info('已构造连接对象： [sqlite://%s]' % dbname)
        dbc = SqliteDBC(dbname)

    elif dbtype.lower() == MYSQL :
        log.info('已构造连接对象： [mysql://%s:%s@%s:%i/%s?charset=%s]' %
                 (username, password, host, port, dbname, charset))
        dbc = MysqlDBC(host, port, username, password, dbname, charset)

    else :
        dbc = None
        log.info('无效的数据库类型： [%s]' % dbtype)
    return dbc





