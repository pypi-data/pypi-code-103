import re
from typing import Callable

REGEX = r"\${(.*?)}"

def interpolate(string: str, callback: Callable) -> str:
  new_string = string
  matches = list(re.finditer(REGEX, string))
  for match in matches:
    expr_with_characters = match.group()
    expr = re.findall(REGEX, expr_with_characters)[0]
    interpolated_str = callback(expr)
    new_string = new_string.replace(expr_with_characters, interpolated_str)
  return new_string
