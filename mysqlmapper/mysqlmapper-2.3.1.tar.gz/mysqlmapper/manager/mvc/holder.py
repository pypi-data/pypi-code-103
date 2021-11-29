from tabledbmapper.logger import Logger, DefaultLogger
from tabledbmapper.manager.manager import Manager
from tabledbmapper.manager.session.sql_session import SQLSession
from tabledbmapper.manager.xml_config import parse_config_from_string

from mysqlmapper.engine import MySQLConnBuilder, MySQLTemplateEngine
from mysqlmapper.manager.mvc.dao import DAO
from mysqlmapper.manager.mvc.info import _table_xml, _column_xml, _index_xml, _key_xml, get_db_info, get_table_info
from mysqlmapper.manager.mvc.mapper import get_mapper_xml
from mysqlmapper.manager.mvc.service import Service


class MVCHolder:
    """
    MVC retainer
    """
    # Host name
    _host = None
    # User name
    _user = None
    # Password
    _password = None
    # database name
    _database = None
    # enable simple service
    _enable_simple_service = None
    # Database port
    _port = None
    # Encoding format
    _charset = None

    # Database session
    session = None
    # Database info Manager
    database_info_manager = None
    # Database description information
    database_info = None
    # Database table info
    table_info = None
    # Service dictionary
    services = None

    def __init__(self, host: str, user: str, password: str, database: str, port=3306, charset="utf8"):
        """
        Initialize MVC holder
        :param host: Host name
        :param user: User name
        :param password: Password
        :param database: Database name
        :param port: Database port
        :param charset: Encoding format
        """
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port
        self._charset = charset

        # conn the database
        conn_handle = MySQLConnBuilder(host, user, password, database, port, charset)
        conn = conn_handle.connect()
        template_engine = MySQLTemplateEngine(conn)

        # build session
        self.session = SQLSession(template_engine)
        self.session.set_logger(DefaultLogger())

        # build database info manager
        # 1.Read profile
        table_config = parse_config_from_string(_table_xml)
        column_config = parse_config_from_string(_column_xml)
        index_config = parse_config_from_string(_index_xml)
        key_config = parse_config_from_string(_key_xml)

        # 2.builder manager
        self.database_info_manager = {
            "table_manager": Manager(template_engine, table_config),
            "column_manager": Manager(template_engine, column_config),
            "index_manager": Manager(template_engine, index_config),
            "key_manager": Manager(template_engine, key_config)
        }

        # init info and service
        self.database_info = {}
        self.table_info = {}
        self.services = {}

    def set_logger(self, logger: Logger):
        """
        Set Logger
        :param logger: log printing
        :return self
        """
        self.session.engine().set_logger(logger)
        return self

    def load_database_service(self):
        """
        load database service
        :return: self
        """
        _database_info = get_db_info(self.database_info_manager, self._database)
        return self.load_service(_database_info)

    def load_tables_service(self, table_names: list):
        """
        used by load table,s service when close the simple service
        :param table_names: database table names
        :return: self
        """
        for item in table_names:
            self.load_table_service(item)
        return self

    def load_table_service(self, table_name: str):
        """
        used by load table,s service when close the simple service
        :param table_name: database table name
        :return: self
        """
        _database_info = get_table_info(self.database_info_manager, self._database, table_name)
        return self.load_service(_database_info)

    def load_service(self, database_info: dict):
        """
        load service from database info
        :param database_info: database info
        :return: self
        """
        # for item table in database info
        for table in database_info["tables"]:
            # get mapper xml
            xml_string = get_mapper_xml(database_info, table["Name"])
            # parse to config
            config = parse_config_from_string(xml_string)
            # get manager
            manager = Manager(self.session.engine(), config)
            # get dao
            dao = DAO(manager)

            # get the database info && set the table info
            self.table_info[table["Name"]] = table
            # get service
            self.services[table["Name"]] = Service(dao)
        # update the database info
        self.database_info["tables"] = list(self.table_info.values())
        return self
