"""
    This module defines a base Model class to create
    database models and upload entities to the datastore.
"""
from google.cloud import datastore
from gaelib.db import properties, helpers

from .query import Query


class Model():
  """
      The Model class to create
      database models and upload entities to the datastore.
  """
  __client__ = None

  def __init__(self, key=None, key_str='', **kwargs):
    object.__setattr__(self, "__entity_key__", None)
    object.__setattr__(self, "__entity__", None)
    object.__setattr__(self, "__retrieved__", False)
    client = self.get_client()
    """
            1. First we check for a passed key and set that as the key
            2. Then we check for a passed key str and use that to build
               a key which we set as a key
            3. Then if entity is passed, we set that passed entity as
               the entity. This is to be done only if we are not looking
               for the most recently fetched value of entity. Staleness
               must be expected
            4. Then we try to fetch the entity based on the set key
            5. Only if we see that there was no entity fetched, do we use
               allocate_ids to generate a key. This way we don't unnecessarily
               waste an rpc call on a key we are sure doesn't exist in the DS.
        """
    # Setting a key provided in init
    if key:
      self.__entity_key__ = key
    elif key_str:
      self.__entity_key__ = self.generate_key(key_str)

    # Setting entity either explicitly provided
    # or provided as a key/key_str
    entity = kwargs.pop('entity', None)

    if entity:
      self.__entity__ = entity
    elif self.__entity_key__:
      # Fetch only if the key or key_str were provided to init
      self.__entity__ = client.get(self.__entity_key__)
    else:
      # Only create the entity key if it was not already created
      # base on key str. This will not be dependent on whether the
      # entity was fetched or not.
      incomplete_key = self.get_client().key(
          (object.__getattribute__(self, '__class__').__name__))
      self.__entity_key__ = client.allocate_ids(incomplete_key, 1)[0]

    if self.__entity__:
      # This means that the datastore already had the entity for this key
      self.__retrieved__ = True
    else:
      self.__entity__ = datastore.Entity(key=self.__entity_key__)
      # Setting the default values for properties for absolutely
      # fresh entity
      all_attributes = dir(self)
      for attr in all_attributes:
        attribute = object.__getattribute__(self, attr)
        if isinstance(attribute, properties.Property):
          if attribute._default is not None:
            self.__entity__[attr] = attribute._default

    # kwargs items will overwrite those that were already in the entity
    for key, val in kwargs.items():
      attribute = object.__getattribute__(self, key)
      if isinstance(attribute, properties.Property):
        self.__entity__[key] = attribute.validate(val)

  def __getattribute__(self, attr):
    """
        The modified __getattr__ function to view the value of
        of the attributes in the model.
    """
    attribute = super().__getattribute__(attr)
    if isinstance(attribute, properties.Property):
      return self.__entity__.get(attr, None)
    return attribute

  def update(self, **kwargs):
    """
        The function to update multiple attributes of an entity at once.
    """
    for key, val in kwargs.items():
      attribute = object.__getattribute__(self, key)
      if isinstance(attribute, properties.Property):
        self.__entity__[key] = attribute.validate(val)

  def key(self):
    """
        Method to return cloud datastore key of entity.
    """
    return self.__entity_key__

  @classmethod
  def generate_key(cls, key_str):
    """
        The function to set the key for the entity.
    """
    return cls.get_client().key(cls.__name__, key_str)

  def put(self):
    """
        The function to insert the entity in cloud datastore
    """
    client = self.get_client()
    client.put(self.__entity__)

  @classmethod
  def get(cls, key):
    client = cls.get_client()
    entity = client.get(key)
    return cls(key=entity.key, entity=entity)

  @classmethod
  def retrieve(cls, filters=None, order=None, limit=None, key_strs=None,
               start_cursor=None):
    """
        The function to get the entity in cloud datastore
    """
    if key_strs:
      # Special case to get a multi get
      keys = [cls.generate_key(key_str) for key_str in key_strs]
      client = cls.get_client()
      entities = client.get_multi(keys)
      entity_list = [cls(key=entity.key, entity=entity) for entity in entities]
      ordered_entity_list = []
      for key in keys:
        for entity in entity_list:
          if entity.key() == key:
            ordered_entity_list.append(entity)
      return ordered_entity_list

    if not filters:
      filters = []
    query = Query(cls)

    if order:
      query.assign_order(order=order)

    for filter in filters:
      query.add_filter(filter[0], filter[1], filter[2])

    entities = query.fetch(limit=limit)
    return entities

  def delete(self):
    """
        The function to delete the entity from cloud datastore
    """
    client = self.get_client()
    client.delete(self.__entity_key__)

  def retrieved(self):
    return self.__retrieved__

  @classmethod
  def query(cls, **kwargs):
    """
        The method to create a Query object for the specified kind.
    """
    return Query(cls, **kwargs)

  @classmethod
  def get_client(self):
    """
        The method to get the datastore Client.
    """
    if self.__client__ is None:
      self.__client__ = datastore.Client(
          namespace=helpers.get_datastore_namespace())
    return self.__client__


