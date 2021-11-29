def import_module(name, path, notfound='error'):
  import sys
  import importlib.util
  assert notfound in ('error', 'ignore')
  if isinstance(path, str):
    path = [path]
  for finder in sys.meta_path:
    spec = finder.find_spec(name, path)
    if spec is not None:
      break
  else:
    if notfound == 'ignore':
      return False
    raise ModuleNotFoundError(f'No module named {name!r}', name=name)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  sys.modules[name] = module
  return module
