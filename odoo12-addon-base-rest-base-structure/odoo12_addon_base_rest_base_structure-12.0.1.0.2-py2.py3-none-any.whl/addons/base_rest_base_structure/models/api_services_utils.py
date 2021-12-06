import datetime
from odoo import models

class APIServicesUtils(object):
  __instance = None

  @staticmethod
  def get_instance():
    if APIServicesUtils.__instance is None:
      APIServicesUtils()
    return APIServicesUtils.__instance

  def __init__(self):
    if APIServicesUtils.__instance is not None:
      raise Exception("This class is a singleton!")
    else:
      APIServicesUtils.__instance = self

  # Creates a dictionary for the given attributes
  # Used to return only the existing attributes of the record
  def generate_get_dictionary(self,record,attributes,rel_attributes = False):
    result = dict()
    if record:
      for attr in attributes:
        value = getattr(record, attr, False)
        if value:
          if isinstance(value, datetime.date):
            result[attr] = str(value)
          elif isinstance(value, models.BaseModel):
            result[attr] = value.id
            if rel_attributes:
              try:
                result[attr] = getattr(value, rel_attributes[attr], False)
              except:
                result[attr] = value.id
          else:
            result[attr] = value
    # result['id'] = record.get_api_external_id()
    result['id'] = record.id
    return result

  # Creates a dictionary for the given attributes
  # Used to return only the existing attributes in the params of a create call
  def generate_create_dictionary(self,params,attributes):
    result = dict()
    if params:
      for attr in attributes:
        if attr in params:
          result[attr] = params[attr]
    return result
