import os


def get_default_storage_bucket():
  return str(os.getenv('GOOGLE_CLOUD_PROJECT')) + '.appspot.com'


def get_storage_bucket():
  return os.getenv('CLOUD_STORAGE_BUCKET', default=get_default_storage_bucket())
