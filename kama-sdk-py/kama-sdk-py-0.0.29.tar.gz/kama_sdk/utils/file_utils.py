import os
from typing import List

import yaml

from kama_sdk.core.core.types import K8sResDict
from kama_sdk.utils import env_utils


class short_lived_resfile:

  resdict: K8sResDict
  resdicts: List[K8sResDict]

  def __init__(self, **kwargs):
    self.res_dict = kwargs.get('resdict')
    self.res_dicts = kwargs.get('resdicts')
    self.fname = kwargs.get('fname')

  def __enter__(self):
    with open(self.fname, 'w') as file:
      if self.res_dict is not None:
        file.write(yaml.dump(self.res_dict))
      elif self.res_dicts is not None:
        file.write(yaml.dump_all(self.res_dicts))

  def __exit__(self, exc_type, exc_val, exc_tb):
    if os.path.isfile(self.fname):
      if env_utils.is_prod():
        os.remove(self.fname)


class short_lived_file:

  def __init__(self, fname, contents):
    self.fname = fname
    self.contents = contents

  def __enter__(self):
    with open(self.fname, 'w') as file:
      file.write(self.contents)

  def __exit__(self, exc_type, exc_val, exc_tb):
    if os.path.isfile(self.fname):
      if env_utils.is_prod():
        os.remove(self.fname)


