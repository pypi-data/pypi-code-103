from tabledbmapper.logger import DefaultLogger
from tabledbmapper.manager.session.sql_session_factory import SQLSessionFactory, SQLSessionFactoryBuild

from mysqlmapper.engine import MySQLConnHandle, MySQLExecuteEngine, MySQLConnBuilder
from mysqlmapper.manager.mvc.holder import MVCHolder
from mysqlmapper.manager.mvc.service import Service


class MySQLSessionFactory(SQLSessionFactory):

    # mvc holder
    mvc_holder = None

    def __init__(self, conn_builder: MySQLConnBuilder, conn_handle: MySQLConnHandle, execute_engine: MySQLExecuteEngine,
                 lazy_init=True, max_conn_number=10, enable_simple_service=True, logger=DefaultLogger()):
        """
        Init session pool
        :param conn_builder: MySQLConnBuilder
        :param conn_handle: MySQLConnHandle
        :param execute_engine: MySQLExecuteEngine
        :param lazy_init: lazy_init
        :param max_conn_number: max_conn_number
        :param enable_simple_service: enable  simple service
        :param logger: Logger
        """
        self.mvc_holder = MVCHolder(
            conn_builder.host,
            conn_builder.user,
            conn_builder.password,
            conn_builder.database,
            conn_builder.port,
            conn_builder.charset
        )
        if enable_simple_service:
            self.mvc_holder.load_database_service()
        self.mvc_holder.set_logger(logger)
        super().__init__(conn_builder, conn_handle, execute_engine, lazy_init, max_conn_number, logger)

    def get_common_session(self):
        return self.mvc_holder.session

    def service(self, table_name: str) -> Service:
        return self.get_simple_service(table_name)

    def get_simple_service(self, table_name: str) -> Service:
        return self.mvc_holder.services[table_name]

    def get_database_info(self):
        return self.mvc_holder.database_info

    def get_table_info(self, table_name: str):
        if table_name not in self.mvc_holder.table_info:
            return {}
        return self.mvc_holder.table_info[table_name]

    def load_database_service(self):
        self.mvc_holder.load_database_service()
        return self

    def load_tables_service(self, table_names: list):
        self.mvc_holder.load_tables_service(table_names)
        return self

    def load_table_service(self, table_name: str):
        self.mvc_holder.load_table_service(table_name)
        return self

    def load_service(self, database_info: dict):
        self.mvc_holder.load_service(database_info)
        return self


class MySQLSessionFactoryBuild(SQLSessionFactoryBuild):

    _enable_simple_service = True

    def __init__(self, host: str, user: str, password: str, database: str, port=3306, charset="utf8"):
        """
        Init
        :param host: host
        :param user: user
        :param password: password
        :param database: database
        :param port: data source port
        :param charset: charset
        """
        conn_builder = MySQLConnBuilder(host, user, password, database, port, charset)
        super().__init__(conn_builder, MySQLConnHandle(), MySQLExecuteEngine())

    def close_simple_service(self):
        self._enable_simple_service = False
        return self

    def build(self) -> MySQLSessionFactory:
        return MySQLSessionFactory(
            self._conn_builder,
            self._conn_handle,
            self._execute_engine,
            self._lazy_init,
            self._max_conn_number,
            self._enable_simple_service,
            self._logger
        )
