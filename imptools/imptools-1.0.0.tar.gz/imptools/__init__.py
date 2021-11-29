def import_from_path(name, paths, notfound='error', reload=False):
  """
  Import a module from any path on the filesystem.

  Usually, this would be achieved by adding the parent directory of the module
  to sys.path or the PYTHONPATH environment variable. However, this pollutes
  the import path and can lead to accidentally importing the wrong modules. The
  function import_from_path() avoids this problem by importing a package from a
  search path without modifying the Python import path.

  The module can be either a directory containing __init__.py or a single file.

  Relative paths are resolved relative to the source file that calls
  import_from_path().
  """
  import importlib.util
  import inspect
  import pathlib
  import sys

  # Skip if the module is already loaded.
  if name in sys.modules and not reload:
    return

  # Find calling filename.
  for info in inspect.stack():
    if info.filename == __file__:
      continue
    break
  script = info.filename
  root = pathlib.Path(script).parent

  # Validate user input.
  assert notfound in ('error', 'ignore')
  if isinstance(paths, (str, pathlib.Path)):
    paths = [paths]
  for index, path in enumerate(paths):
    path = pathlib.Path(path).expanduser()
    if not path.is_absolute():
      path = (root / path).resolve()
    paths[index] = str(path)

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


def enable_relative():
  """
  Enable relative imports for scripts that are not executed as module.

  Usually, scripts that are part of a module and use relative imports must be
  run as python3 -m module.script. However, this requires being in the correct
  working directory and can be annoying. The enable_relative() function allows
  to execute those scripts normally as python3 script.py.

  Since PEP 366, this can be achieved by specifying the __package__ variable in
  the script and importing the package or making it availble on the Pyhton
  import path. The enable_relative() function hides this behind a simple
  function that can be imported and called inside the script, before any
  relativer imports.
  """
  import pathlib
  import __main__

  # Skip if the script is executed as a module.
  if __main__.__package__ is not None:
    return

  # Assume the module is simply the parent directory.
  root = pathlib.Path(__main__.__file__).parent

  # Import the module without polluting the Python import path.
  import_from_path(root.name, root.parent)

  # Set the package variable so Python can resolve relative imports.
  __main__.__package__ = root.name
