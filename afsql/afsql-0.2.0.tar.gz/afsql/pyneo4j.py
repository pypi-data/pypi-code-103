# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     db_pyneo4j
   Description :
   Author :       jpl
   date：          2021/10/11
-------------------------------------------------
   Change Activity:
                   2021/10/11:
-------------------------------------------------
"""
__author__ = 'Asdil'
import uuid
from py2neo import Graph, Relationship, Node
from neo4j import GraphDatabase


class Pyneo4j:
    """
    Neo4j类用于
    """

    def __init__(self, url, user, password, database=None):
        """__init__(self):方法用于

        Parameters
        ----------
        url: str
            neo4j服务器地址
        user: str
            用户名
        password: str
            密码
        database : str or None
            数据了名称
        Returns
        ----------
        """
        # neo4j官方库
        self._driver = GraphDatabase.driver(url, auth=(user, password))
        # py2neo库
        self._driver2 = Graph(url, auth=(user, password), name=database)
        self.database = database

    def create_node(self, labels, parameters, add_tag=False, add_uid=False):
        """create_node方法用于

        Parameters
        ----------
        labels: list
            标签列表
        parameters: dict
            参数字典
        add_tag: bool
            是否添加tag
        add_uid: bool
            是否添加uid
        Returns
        ----------
        """
        if add_tag:
            parameters['tag'] = uuid.uuid1()
        node = Node(*labels, **parameters)
        self._driver2.create(node)
        if add_uid:
            uid = node.identity
            parameters['uid'] = uid
            node.update(**parameters)
            self._driver2.push(node)
        return node

    def link(self, nodes, relations=None):
        """link方法用于

        Parameters
        ----------
        nodes : py2neo node list
            py2neo node列表
        relations: list or None
            属性列表

        Returns
        ----------
        """

        for i in range(len(nodes) - 1):
            try:
                r = relations.pop(0)
            except:
                r = ' '
            self._driver2.create(Relationship(nodes[i], r, nodes[i + 1]))

    def is_node(self, node):
        """is_node方法用于

        Parameters
        ----------
        node : object
            节点对象或者是其它的

        Returns
        ----------
        """
        if node is Node:
            return True
        return False

    def close(self):
        """close方法用于关闭连接
        """
        self._driver.close()

    def _cypher_run(self, session, cypher, rtype='data'):
        """_cypher_run方法用于执行命令

        Parameters
        ----------
        session : neo4j session
            neo4j 会话 不用显示传递
        cypher : str
            Cypher 语句, neo4j 专用的sql语句
        rtype : str
            返回值种类 data 或者 graph
            如果选择graph
                可使用 graph._nodes.values() 或者 graph._relationships.values()
                将相关信息取出来
        Returns
        ----------
        """
        result = session.run(cypher)

        if rtype == 'data':  # 返回数据
            result = result.data()
        elif rtype == 'graph':  # 返回图
            result = result.graph()
        else:
            result = None
        return result

    def run(self, cypher, rtype='data'):
        """run方法用于

        Parameters
        ----------
        cypher : str
            Cypher 语句, neo4j 专用的sql语句
        rtype : str
            返回值种类 data 或者 graph
            如果选择graph
                可使用 graph._nodes.values() 或者 graph._relationships.values()
                将相关信息取出来 提取时需要使用list()函数
        Returns
        ----------
        """
        result = None
        if self.database:
            with self._driver.session(database=self.database) as session:
                if ' return ' in cypher.lower() or ' RETURN ' in cypher and\
                        (' create ' not in cypher and ' CREATE ' not in cypher):
                    result = session.read_transaction(self._cypher_run, cypher=cypher, rtype=rtype)  # 查询操作
                else:
                    session.write_transaction(self._cypher_run, cypher=cypher, rtype=rtype)  # 写操作
        else:
            with self._driver.session() as session:
                if ' return ' in cypher.lower() or ' RETURN ' in cypher and\
                        (' create ' not in cypher and ' CREATE ' not in cypher):
                    result = session.read_transaction(self._cypher_run, cypher=cypher, rtype=rtype)  # 查询操作
                else:
                    session.write_transaction(self._cypher_run, cypher=cypher, rtype=rtype)  # 写操作
        return result

    def delete_all(self):
        """delete_all方法用于删除图数据所有数据,慎用"""
        self._driver2.delete_all()
