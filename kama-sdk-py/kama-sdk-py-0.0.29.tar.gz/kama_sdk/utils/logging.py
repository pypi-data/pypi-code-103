import inspect
import traceback
from typing import List, Any, Optional

from inflection import underscore
from termcolor import cprint


def calling_module_name() -> Optional[str]:
  """
  From https://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
  Wide except-block because it's not worth going deeper.
  :return:
  """
  try:
    this_fame = inspect.currentframe()
    caller_frame = this_fame.f_back.f_back.f_back
    code = caller_frame.f_code
    caller_fname = code.co_filename
    return caller_fname.split("/")[-1].replace(".py", "")
  except:
    return None


def exception2trace(exception: Exception) -> List[str]:
  as_list = traceback.format_exception(
    etype=type(exception),
    value=exception,
    tb=exception.__traceback__
  )
  return list(map(str.strip, as_list)) if as_list else []


def lwin(message, **kwargs):
  print_colored(kwargs.get('sig'), message, 'green')


def lerr(message: Any, **kwargs):
  if kwargs.get('trace', False):
    message = f"{message}\n{traceback.format_exc()}"
  elif exception := kwargs.get('exc'):
    exception_str = "\n".join(exception2trace(exception))
    message = f"{message}\n{exception_str}"
  print_colored(kwargs.get('sig'), message, 'red')


def lwar(message: str, **kwargs):
  if kwargs.get('trace', False):
    message = f"{message}\n{traceback.format_exc()}"
  print_colored(kwargs.get('sig'), message, 'yellow')


def print_colored(sig, message, color):
  if not sig:
    final_sig = f"{calling_module_name()}"
  elif isinstance(sig, type):
    final_sig = f"class::{underscore(sig.__name__)}"
  elif isinstance(sig, str):
    final_sig = sig
  else:
    final_sig = 'unknown_origin'

  cprint(f"[{final_sig}] {message}", color=color, attrs=['bold'])
