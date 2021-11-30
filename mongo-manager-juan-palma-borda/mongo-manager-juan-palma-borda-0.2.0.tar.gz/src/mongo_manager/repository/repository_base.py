import pymongo

from ..mongo_manager import SingletonMeta
from bson import ObjectId


class RepositoryBase(metaclass=SingletonMeta):

    def __init__(self, collection, clase) -> None:
        __metaclass__ = SingletonMeta
        from ..mongo_manager import mongo_manager_gl
        self.__collection = mongo_manager_gl.collection(collection)
        self.__clase = clase

    @property
    def collection(self) -> pymongo.collection.Collection:
        return self.__collection

    @property
    def clase(self):
        return self.__clase

    def count_all(self):
        return self.collection.count_documents({})

    def get_all(self, skip=0, limit=1000):
        return self.clase.generar_objects_from_list_dicts(self.collection.find().skip(skip).limit(limit), self.clase)

    def find_by_id(self, id_mongo):
        return self.clase.generar_object_from_dict(self.collection.find_one({'_id': ObjectId(id_mongo)}))

    def delete_object(self, objeto):
        if objeto.id_mongo is not None:
            return self.delete_by_id(objeto.id_mongo)

    def delete_by_id(self, id_mongo):
        return self.collection.delete_one({'_id': ObjectId(id_mongo)})

    def insert_one(self, objeto):
        return self.collection.insert_one(objeto.get_dict_no_id())

    def insert_many(self, lista_objetos: list):
        return self.collection.insert_many(self.clase.generar_list_dicts_from_list_objects(lista_objetos))

    def insert_or_replace_id(self, objeto):
        if objeto.id_mongo is None:
            return self.insert_one(objeto)
        else:
            return self.replace_by_id(objeto.id_mongo, objeto)

    def replace_by_id(self, id_mongo, objeto):
        return self.collection.replace_one({"_id": id_mongo}, objeto.get_dict())

    def update_by_id(self, id_mongo, objeto_dict: dict):
        return self.collection.update_one({"_id": id_mongo}, {"$set": objeto_dict})
