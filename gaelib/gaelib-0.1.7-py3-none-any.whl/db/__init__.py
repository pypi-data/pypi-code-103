from google.cloud import datastore
from . import helpers


def put_multi(entity_list):
  client = datastore.Client(namespace=helpers.get_datastore_namespace())
  client.put_multi(entity_list)
  return
