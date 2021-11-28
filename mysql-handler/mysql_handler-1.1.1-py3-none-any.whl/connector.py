from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection


class MySQLConnector:
    __instance = None

    def __new__(cls, host, database, user, port, password):
        if MySQLConnector.__instance is None:
            MySQLConnector.__instance = object.__new__(cls)
            MySQLConnector.__instance.__pool = MySQLConnectionPool(pool_name="mysql_pool",
                                                                   pool_size=5,
                                                                   host=host,
                                                                   database=database,
                                                                   port=port,
                                                                   user=user,
                                                                   password=password)
        return MySQLConnector.__instance

    @staticmethod
    def get_connection() -> PooledMySQLConnection:
        return MySQLConnector.__instance.__pool.get_connection()
