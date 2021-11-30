from pymongo import MongoClient

from .patrones.singleton import SingletonMeta

mongo_manager_gl = None


class MongoManager(metaclass=SingletonMeta):
    __bd = None

    def __init__(self, username: str = '', password: str = '', db: str = '', auth_source: str = '',
                 bd_online: bool = False, port_local: int = 27017,
                 url_online='') -> None:
        """
        Crea la instancia conectada a la collecion en cuestion.
        """
        if bd_online:
            self.__bd = MongoClient(url_online)[db]
        else:
            self.__bd = \
                MongoClient('mongodb://{}:{}@localhost:{}'.format(username, password, port_local),
                            authSource=auth_source)[db]
        global mongo_manager_gl
        mongo_manager_gl = self

    @property
    def bd(self):
        return self.__bd

    def collection(self, collection):
        return self.bd[collection]


class MongoException(Exception):
    pass

# bd = MongoManager('tmo', 'tmo', 'tmo', 'tmo')
