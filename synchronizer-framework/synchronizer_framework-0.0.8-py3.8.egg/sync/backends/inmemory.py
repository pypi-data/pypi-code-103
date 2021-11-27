import logging
from pprint import pformat
from typing import List, Dict, Type

from sync.datasource import DataSource
from sync.mixins import LinkProvider, Timestamped


class InMemoryDs(DataSource):
    def preload_type(self, preload_type, path) -> bool:
        """skip"""
        return True

    def __init__(self):
        self.store: Dict[Type, List] = dict()

    def create(self, entity):
        if entity.__class__ not in self.store:
            self.store[entity.__class__] = list()

        if entity not in self.store[entity.__class__]:
            self.store[entity.__class__].append(entity)
            return True
        return False

    def all(self, of_type, limit=None) -> set:
        if of_type in self.store:
            return self.store[of_type].copy()
        else:
            return list()

    def delete(self, entity) -> bool:
        if entity in self.store[entity.__class__]:
            self.store[entity.__class__][self.id(entity)] = None
            return True
        return False

    def entity_types(self) -> List[type]:
        return self.store.keys()

    @staticmethod
    def from_collection(entities, db=None):
        if not db:
            db = InMemoryDs()

        for element in entities:
            db.create(element)

            for prop in element.__dict__:
                value = element.__dict__[prop]
                if isinstance(value, set) or isinstance(value, list):
                    InMemoryDs.from_collection(value, db)

        return db

    def find(self, by_type, by_conditions):
        def object_matches(object, conditions):
            if not object:
                return False
            for k, v in conditions:
                if getattr(object, k) != v:
                    return False
            return True

        if by_type not in self.store:
            return []

        result_set = [
            e for e in self.store[by_type] if object_matches(e, by_conditions.items())
        ]

        logging.debug(
            f"Searching for {by_type.__name__} by {by_conditions}: {len(result_set)} found"
        )
        return result_set

    def refresh(self, entity):
        if entity in self.all(entity.__class__):
            return entity
        else:
            return None

    def __repr__(self):
        return pformat(self.store)

    def persist(self, entity):
        self.from_collection([entity], self)

    def get(self, type, id):
        return self.store.get(type)[int(id)]

    def id(self, entity):
        class_store = self.store.get(entity.__class__)
        try:
            return class_store.index(entity) if class_store else None
        except ValueError:
            return None


class DoubleDictToSet:
    def __init__(self):
        self.dict = dict()

    def add(self, key1, key2, value):
        if key1 not in self.dict:
            self.dict[key1] = dict()
        if key2 not in self.dict[key1]:
            self.dict[key1][key2] = set()
        self.dict[key1][key2].add(value)

    def get(self, key1, key2):
        return self.dict[key1][key2].copy()

    def __contains__(self, item):
        key1, key2 = item
        return key1 in self.dict and key2 in self.dict[key1]


class InMemoryLinkProvider(LinkProvider):
    def __init__(self):
        self.links = DoubleDictToSet()

    def link(self, entity, other, entity_ds: DataSource, other_ds: DataSource):
        other_type = other.__class__
        entity_type = entity.__class__
        if (
            not (entity, other_type) in self.links
            or not (other, entity_type) in self.links
        ):
            self.links.add(entity, other_type, other)
            self.links.add(other, entity_type, entity)
            return True
        return False

    def others(
        self, entity, entity_ds: DataSource, other_type: Type, other_ds: DataSource
    ):
        if (entity, other_type) in self.links:
            return self.links.get(entity, other_type)
        else:
            return None

    def unlink(self, entity, entity_ds: DataSource, other_ds: DataSource):
        pass


class InMemoryTimestamp(Timestamped):
    _updated_at: int = 0

    def updated_at(self):
        return self._updated_at

    def update_timestamp(self, timestamp):
        self._updated_at = timestamp


class Hierarchical:
    @property
    def parent(self):
        if hasattr(self, "_parent"):
            return self._parent
        else:
            return None

    @parent.setter
    def parent(self, new):
        if hasattr(self, "_parent") and self._parent and self in self._parent._children:
            self._parent._children.remove(self)

        if new:
            if not hasattr(new, "_children"):
                new._children = set()
            new._children.add(self)

        self._parent = new

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, new):
        for child in new:
            child._parent = self
        self._children = new


class InMemoryBase(Hierarchical, InMemoryTimestamp):
    def __repr__(self, show_children=False, show_parent=True, indent=0):
        result = " " * indent
        result += f"{self.__class__.__name__}("

        if hasattr(self, "name"):
            result += f"name={self.name}"

        if show_children and self.children.__len__() > 0:
            result += f", children=[\n"
            for child in self.children:
                result += f"{child.__repr__(indent=(indent + 2))}\n"
            result += " " * indent + "]"
        if show_parent and self.parent:
            result += f", parent={self.parent.__repr__(show_parent=False, show_children=False, indent=indent)}"
        result += ")"
        return result
