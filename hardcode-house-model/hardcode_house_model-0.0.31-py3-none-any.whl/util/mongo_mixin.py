from datetime import date, datetime
from enum import Enum

from bson import ObjectId


class MongoMixin(object):
    '''Contains various querying methods, useful for mongodb.'''
    class MongoUpdateMethod(Enum):
        SET = 'set'
        UNSET = 'unset'

    @classmethod
    def all_fields(cls):
        return cls._fields.keys()

    @classmethod
    def all_relationships(cls):
        return cls._relationships.keys()

    def resolved_relationships(self):
        return [
            a for a in self.all_relationships()
        ]

    def dict_include(self):
        return self.all_fields()

    def dict_exclude(self):
        return []

    # Default to_dict, can be overridden
    # Returns all fields, with values transformed:
    # -ObjectIds casted to strings
    # -Date/Datetime formatted as string, with format specified by
    # default_date_format property of class
    # -Values of lists and dicts recursively transformed
    def to_dict_default(self, date_format="%Y-%m-%d", ignore_unloaded=False):
        def transform_field(value):
            if isinstance(value, ObjectId):
                return str(value)
            elif isinstance(value, list):
                return map(transform_field, value)
            elif issubclass(value.__class__, MongoMixin):
                return value.to_dict() if hasattr(value, 'to_dict') else \
                    value.to_dict_default(ignore_unloaded=ignore_unloaded)
            elif isinstance(value, dict):
                return dict([(key, transform_field(val))
                             for key, val in value.iteritems()])
            elif isinstance(value, (datetime, date)):
                return value.strftime(date_format)
            return value

        _dict = {}
        exclude = self.dict_exclude()
        for fname in self.dict_include():
            if fname not in exclude:
                value = getattr(self, fname)
                _dict[fname] = transform_field(value)
        return _dict

    @classmethod
    def from_dict(cls, dict_data, created=False):
        return super()._from_son(dict_data, created=created)

    def to_dict(self):
        return self.to_dict_default("%Y-%m-%d %H:%M:%S")

class DocumentMixin(object):
    @classmethod
    def bulk_update(cls, requests, ordered=True, bypass_document_validation=False, session=None):
        collection = cls._get_collection()
        collection.bulk_write(
            requests, ordered, bypass_document_validation, session)