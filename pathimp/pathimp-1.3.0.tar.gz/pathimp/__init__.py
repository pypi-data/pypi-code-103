def import_module(name, paths, notfound='error'):
  import importlib.util
  import pathlib
  import sys

  # Validate user input.
  assert notfound in ('error', 'ignore')
  if isinstance(paths, (str, pathlib.Path)):
    paths = [paths]
  paths = [str(pathlib.Path(path).expanduser()) for path in paths]

  # Try to find the module.
  for finder in sys.meta_path:
    if not hasattr(finder, 'find_spec'):
      continue
    spec = finder.find_spec(name, paths)
    if spec is not None:
      break
  else:
    if notfound == 'ignore':
      return False
    raise ModuleNotFoundError(f'No module named {name!r}', name=name)

  # Import the module.
  module = importlib.util.module_from_spec(spec)
  sys.modules[name] = module
  spec.loader.exec_module(module)
  return module
