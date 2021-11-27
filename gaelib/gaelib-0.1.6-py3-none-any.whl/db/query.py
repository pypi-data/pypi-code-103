"""
    This module defines a base Query class to create
    datastore query objects and perform queries on datastore.
"""
from google.cloud import datastore


class Query():
  """
      The class for creating a datastore query object
      and perform queries on a model.
  """

  def __init__(self, model_class, **kwargs):
    self.__model_class__ = model_class
    self.__query__ = model_class.get_client().query(
        kind=self.__model_class__.__name__, **kwargs)

  def add_filter(self, attribute, op, val):
    """
        The method to add filters for the query.
    """
    self.__query__.add_filter(attribute, op, val)

  def assign_order(self, order):
    self.__query__.order = order

  def fetch(self, **kwargs):
    """
        The method to fetch and return query results.
    """
    results = []
    for obj in list((self.__query__.fetch(**kwargs))):
      result_obj = self.__model_class__(key=obj.key, entity=obj)
      results.append(result_obj)
    return results
