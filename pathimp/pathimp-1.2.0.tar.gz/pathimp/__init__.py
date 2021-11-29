def import_module(name, path, notfound='error'):

  # Import statements.
  import importlib.util
  import pathlib
  import sys

  # Validate user input.
  assert notfound in ('error', 'ignore')
  if isinstance(path, (str, pathlib.Path)):
    path = [path]
  path = [str(pathlib.Path(x).expanduser()) for x in path]

  # Try to find the module.
  for finder in sys.meta_path:
    spec = finder.find_spec(name, path)
    if spec is not None:
      break
  else:
    if notfound == 'ignore':
      return False
    raise ModuleNotFoundError(f'No module named {name!r}', name=name)

  # Import the module.
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  sys.modules[name] = module
  return module
