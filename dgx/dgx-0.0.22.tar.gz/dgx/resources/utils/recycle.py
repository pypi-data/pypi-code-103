from collections import defaultdict
from datetime import datetime
from flask import session
from mongoCon import MongoCon
from pymongo import database


class Recycle:
    """
    Funciones para el manejo de la papelera
    """

    @staticmethod
    def add_event(item: dict, event: str):
        user = session.get('user_name', 'System')
        events = item.get("events", [])
        events.append({
            "event": event,
            "user": user,
            "datetime": datetime.now(),
            "msg": "The user {} has {} this registry.".format(user, event)
        })
        item.update({"events": events})

    @classmethod
    def __add(self, cnx: database.Database, collection: str, query: dict, display: str):
        _ids = []
        items = []
        nw = datetime.now()
        for item in cnx[collection].find(query):
            self.add_event(item, "deleted")
            nitem = {
                "type": collection,
                "delete_date": nw,
                "deleted_by": session.get('user_name', 'System'),
                "display": display.format(**item),
                "item": item
            }
            item.get('group_code', False) and item.update({"group_code": item['group_code']})
            item.get('dealer_code', False) and item.update({"dealer_code": item['dealer_code']})
            items.append(nitem)
            _ids.append(item["_id"])  # agrega identificador a eliminar
        if items:  # si hay items para insertar en papelera
            cnx.recycle.insert_many(items)
            cnx[collection].delete_many({"_id": {"$in": _ids}})

    @classmethod
    def __recovery(self, cnx: database.Database, query: dict):
        items = list(cnx.recycle.find(query, {"item": True, "type": True}))
        tpsC = defaultdict(list)  # tipos de collecion
        if items:
            for item in items:
                self.add_event(item['item'], "restored")
                tpsC[item['type']].append(item['item'])  # agrega el tipo
            for cname, citems in tpsC.items():
                cnx[cname].insert_many(citems)
            cnx.recycle.delete_many(query)

    @classmethod
    def add(self, collection: str, query: dict, display: str, cnx: (database.Database or dict) = None):
        if isinstance(cnx, database.Database):
            self.__add(cnx, collection, query, display)
        elif cnx is None or isinstance(cnx, dict):
            with MongoCon(cnx) as cnx:
                self.__add(cnx, collection, query, display)
        else:
            raise Exception("%s is not supported" % cnx)

    @classmethod
    def recovery(self, query: dict, cnx: (database.Database or dict) = None):
        """
        Recupera los items borrados
        """
        if isinstance(cnx, database.Database):
            self.__recovery(cnx, query)
        elif cnx is None or isinstance(cnx, dict):
            with MongoCon(cnx) as cnx:
                self.__recovery(cnx, query)
        else:
            raise Exception("%s is not supported" % cnx)
