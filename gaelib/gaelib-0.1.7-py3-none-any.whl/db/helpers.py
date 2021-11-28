import os

from . import constants


def get_datastore_namespace():
  return os.getenv('DATASTORE_NAMESPACE', default=constants.DEFAULT_DATASTORE_NAMESPACE)
