"""
   SDC Base model module
"""
# coding=utf-8
# pylint: disable=invalid-name, unused-argument
import copy
import json
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, event
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import query_expression

Base = declarative_base()
models_namespace = 'sdc_helpers.models'
json_date_format = '%Y-%m-%d %H:%M:%S'

class Model(Base):
    """
       SDC base model class
    """
    # pylint: disable=too-few-public-methods, no-member
    __abstract__ = True
    original = None

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, **kwargs):
        """
            Creation of abstract model
        """
        model_id = kwargs.get('id')
        if model_id is not None:
            self.id = model_id
        self.for_update = kwargs.get('for_update', False)
        self.created_at = self.convert_json_datetime(kwargs.get('created_at'))
        self.updated_at = self.convert_json_datetime(kwargs.get('updated_at'))
        properties = kwargs.get('properties')
        if properties is not None:
            if isinstance(properties, str):
                properties = json.loads(properties)
            self.properties = properties

    @declared_attr
    def for_update(self):
        """
            Declared abstract model attribute
        """
        return query_expression()

    def to_dict(self) -> dict:
        """
            Convert model object to dictionary
        """
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }

    @staticmethod
    def convert_json_datetime(date_string):
        """
            Convert JSON string date to datetime object

            args:
                date_string(str): JSON date string
        """
        if date_string is None:
            return None

        return datetime.strptime(date_string, json_date_format)

@event.listens_for(Model, 'load', restore_load_context=True, propagate=True)
def receive_load(target, context):
    """
        Event listener triggered on first load of model

        args:
            target: Model instance
            context: Context data of the model
     """
    target.original = copy.deepcopy(target.to_dict())
