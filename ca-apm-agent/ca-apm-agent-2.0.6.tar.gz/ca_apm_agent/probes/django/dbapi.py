__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""
import logging
import os
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.utils import network
from ca_apm_agent.python_modifiers.singleton import Singleton

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.django.dbapi')

# Constants
SQLITE = 'sqlite'
SQLITE_STRING = 'SQLite DB'
FIREBIRD = 'firebird'
FIREBIRD_STRING = 'Firebird DB'
MYSQL = 'mysql'
MYSQL_STRING = 'MySQL DB'
POSTGRESQL = 'postgresql'
POSTGRESQL_STRING = 'PostgreSQL DB'
ORACLE = 'oracle'
ORACLE_STRING = 'Oracle DB'
SAP_SQL = 'sqlanywhere'
SAP_SQL_STRING = 'SAP SQL Anywhere DB'
MICROSOFT = 'microsoft'
MICROSOFT_SQLSERVER = 'sqlserver_ado'
MICROSOFT_ODBC = 'django_pyodbc'
MICROSOFT_SQLSERVER_STRING = 'MS SQL Server DB'
MICROSOFT_ODBC_STRING = 'MS ODBC'
HOST = 'HOST'
PORT = 'PORT'
NAME = 'NAME'
ENGINE = 'ENGINE'
QUERY = 'query'
DATABASE = 'database'
DATABASE_NAME = 'dbname'
URL = 'url'
COMMAND_TYPE = 'commandtype'
SQL = 'sql'
REGULAR = 'Regular'


class DBAPIProbe(Singleton):
    def __init__(self):
        self.host = network.getfqdn()

    def start(self, context):
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        vendor = str(context.args[0].db.vendor)
        context.func_name = vendor + '.' + QUERY

        database = None
        url = None
        host = context.args[0].db.settings_dict[HOST]
        port = context.args[0].db.settings_dict[PORT]
        name = context.args[0].db.settings_dict[NAME]
        if host in ('localhost', '127.0.0.1', '', ' ',):
            host = self.host
        if port in ('', ' ', None,):
            port = 'local'

        if vendor in (SQLITE, FIREBIRD,):  # For file and memory based DB's
            t = os.path.split(name)[1]
            if name[0] == '/':
                name = name[1:]
            url = host + ':' + port + '/' + name
            name = t
            if vendor == SQLITE:
                database = SQLITE_STRING
            elif vendor == FIREBIRD:
                database = FIREBIRD_STRING
            else:
                pass

        elif vendor in (MYSQL, POSTGRESQL, ORACLE, SAP_SQL, MICROSOFT,):  # For server based DB's
            url = host + ':' + port + '/' + name
            if vendor == MYSQL:
                database = MYSQL_STRING
            elif vendor == POSTGRESQL:
                database = POSTGRESQL_STRING
            elif vendor == ORACLE:
                database = ORACLE_STRING
            elif vendor == SAP_SQL:
                database = SAP_SQL_STRING
            elif vendor == MICROSOFT:
                engine = context.args[0].db.settings_dict[ENGINE].split('.')[-1]
                if engine == MICROSOFT_SQLSERVER:
                    database = MICROSOFT_SQLSERVER_STRING
                elif engine == MICROSOFT_ODBC:
                    database = MICROSOFT_ODBC_STRING
                else:
                    pass
        else:
            pass
        context.set_params(
            {DATABASE: database, DATABASE_NAME: name, HOST.lower(): host, PORT.lower(): port, URL: url,
             COMMAND_TYPE: REGULAR, SQL: str(context.args[1]), })
        logger.debug('Pushed params: %s', str(context.params))

    def finish(self, context):
        pass
