import os
from typing import Type, List


def load_dir_model_subclasses(directory: str) -> List[Type]:
  subdir_paths = os.walk(directory)
  print(subdir_paths)
