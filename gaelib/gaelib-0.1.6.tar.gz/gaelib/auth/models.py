from enum import Enum
from gaelib.db import model, properties


class UserRole(Enum):
  """
      Enum for User.role
  """
  DEFAULT = 0
  STAFF = 1
  ADMIN = 2


USER_ROLE_CHOICES = [user_role.value for user_role in UserRole]


class User(model.Model):
  """
      The database model for User kind.
  """
  email = properties.StringProperty()
  uid = properties.StringProperty()
  name = properties.StringProperty()
  picture = properties.StringProperty()
  role = properties.IntegerProperty(choices=USER_ROLE_CHOICES)
  os = properties.StringProperty()
  device_notification_token = properties.StringProperty()
  token = properties.StringProperty()
  phone = properties.StringProperty()
