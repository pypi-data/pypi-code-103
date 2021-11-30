import json
from abc import ABC, abstractmethod


class ObjetoMongoAbstract(ABC):

    def __init__(self, id_mongo=None):
        self.__id_mongo = id_mongo

    @property
    def id_mongo(self):
        return self.__id_mongo

    def get_dict(self):
        d = self.get_dict_no_id()
        d['_id'] = self.id_mongo
        return d

    @abstractmethod
    def get_dict_no_id(self):
        ...

    def serialize(self):
        return json.dumps(self.get_dict_no_id())

    @staticmethod
    def serialize_all(objetos):
        return json.dumps(ObjetoMongoAbstract.generar_list_dicts_from_list_objects(objetos))

    @staticmethod
    @abstractmethod
    def generar_object_from_dict(dictionary):
        pass

    @staticmethod
    def generar_objects_from_list_dicts(dictionaries: list, cls):
        return [cls.generar_object_from_dict(dictionary) for dictionary in dictionaries]

    @staticmethod
    def generar_list_dicts_from_list_objects(lista_objetos: list):
        return [c.get_dict_no_id() for c in lista_objetos]
