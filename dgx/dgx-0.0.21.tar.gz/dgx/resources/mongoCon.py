from pymongo import MongoClient
from const import MONGO_CONN


class MongoCon:
    """
    Connect to MongoDB
    """

    def __init__(self, conf: dict = None):
        conf = conf or MONGO_CONN
        self.conf = conf
        self.cnx = MongoClient(conf['host'], conf['port'])
        self.db().authenticate(conf['user'], conf['password'])

    def db(self):
        """Devuelve la base de datos"""
        return self.cnx[self.conf['database']]

    def __enter__(self):
        return self.db()

    def __exit__(self, _, __, ___):
        self.cnx.close()
