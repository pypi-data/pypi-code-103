from argparse import ArgumentParser

DEF_DB_HOST, DEF_DB_PORT = 'localhost', 27017


class MongoArgParser(object):
    def __init__(self, def_host: str = DEF_DB_HOST, def_port: str = DEF_DB_PORT,
                 def_replicaset: str = None, def_database: str = None, def_user: str = '', def_password: str = '',
                 def_cert_key_file: str = None, def_ca_file: str = None, def_session_token: str = None) -> None:
        self.__host = def_host
        self.__port = def_port
        self.__replicaset = def_replicaset
        self.__database = def_database
        self.__user = def_user
        self.__password = def_password
        self.__cert_key_file = def_cert_key_file
        self.__ca_file = def_ca_file
        self.__session_token = def_session_token

    def set_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('--mongo_host', type=str, metavar='HOST', default=self.__host,
                            help=f'The database host. By default, {self.__host}.')
        parser.add_argument('--mongo_port', type=int, metavar='PORT', default=self.__port,
                            help=f'The database port. By default, {self.__port}.')
        parser.add_argument('-r', '--replicaset', type=str, metavar='NAME', default=self.__replicaset,
                            help=f'The replicaset. By default, {self.__replicaset}.')
        parser.add_argument('-d', '--database', type=str, metavar='NAME', default=self.__database,
                            help=f'The database name. By default, {self.__database}.')
        parser.add_argument('-u', '--user', type=str, metavar='USER', default=self.__user,
                            help=f'The database user. By default, {self.__user}.')
        parser.add_argument('-p', '--password', type=str, metavar='PASS', default=self.__password,
                            help=f'The user password. By default, {self.__password}.')
        parser.add_argument('--cert_key_file', type=str, metavar='FILE', default=self.__cert_key_file,
                            help=f'The cert key fle to connect to the database. By default, {self.__cert_key_file}.')
        parser.add_argument('--ca_file', type=str, metavar='FILE', default=self.__ca_file,
                            help=f'The CA file to connect to the database. By default, {self.__ca_file}.')
        parser.add_argument('--session_token', type=str, metavar='SESSION', default=self.__session_token,
                            help=f'The session token to connect to the database. By default, {self.__session_token}.')
