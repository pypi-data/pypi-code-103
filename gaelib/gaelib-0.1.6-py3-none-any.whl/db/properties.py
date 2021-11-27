"""
    This module defines the property classes for attributes.
"""
from datetime import datetime
from google.cloud.datastore.key import Key


class Property():
  """
      The base property class for defining attribute types.
  """
  _repeated = None
  _default = None
  _choices = None

  def __init__(self, value, prop, repeated=None, default=None, choices=None):
    if repeated is not None:
      self._repeated = repeated
    if default is not None:
      self._default = default
    if choices is not None:
      self._choices = choices

    self.property = prop
    self.value = self.validate(value)

  def validate(self, value):
    """
        Method to validate the property value.
    """
    valid = True
    if self._repeated is True:
      if isinstance(value, list):
        for v in value:
          valid = valid and isinstance(v, self.property)

      if not valid:
        error_subject = "One repeated value"

    elif value and not isinstance(value, self.property):
      valid = False
      error_subject = "Value"

    if not value and self._default:
      value = self._default
      if not isinstance(value, self.property):
        valid = False
        error_subject = "Default value"

    choices = self._choices
    default = self._default
    if choices and value and value not in choices:
      raise ValueError("Value does not conform to the choices %s" % choices)

    if choices and default and default not in choices:
      raise ValueError(
          "Default Value does not conform to the choices %s" % choices)

    if not valid:
      raise ValueError("{} {} doesn't match the class type for {}".format(
          error_subject, str(value), self.property))

    return value


class StringProperty(Property):
  """
      Attribute property class for string type
  """

  def __init__(self, val=None, choices=None, default=None):
    super().__init__(val, str, default=default, choices=choices)


class FloatProperty(Property):
  """
      Attribute property class for float type
  """

  def __init__(self, value=None, repeated=None):
    super().__init__(value, float, repeated)


class IntegerProperty(Property):
  """
      Attribute property class for int type
  """

  def __init__(self, value=None, repeated=None, default=None, choices=None):
    # choices is used when you want to have an enum
    super().__init__(value, int, repeated, default=default, choices=choices)


class BooleanProperty(Property):
  """
      Attribute property class for int type
  """

  def __init__(self, value=None, repeated=None):
    super().__init__(value, bool, repeated)


class DateTimeProperty(Property):
  """
      Attribute property class for datetime type
  """

  def __init__(self, value=None, repeated=None):
    super().__init__(value, datetime, repeated)


class ReferenceProperty(Property):
  """
      Attribute property class for datastore key type.
  """

  def __init__(self,  value=None, reference_class=None, repeated=None):
    self.reference_class = reference_class
    super().__init__(value, Key, repeated)
