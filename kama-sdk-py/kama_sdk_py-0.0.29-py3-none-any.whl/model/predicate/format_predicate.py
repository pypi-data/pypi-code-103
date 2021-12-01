import re

import validators
from validators import ValidationFailure

from kama_sdk.model.predicate.predicate import Predicate

path_regex = "^\/[/.a-zA-Z0-9-]*$"
PW_SYMBOL_REGEX = r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]'

"""
Password check credit: https://stackoverflow.com/a/32542964/11913562
"""

class FormatPredicate(Predicate):

  def get_reason(self) -> str:
    return f"Must be a(n) {self.get_check_against()}"

  def perform_comparison(self, operator, challenge, check, on_many):
    if challenge is not None:
      if check in ['integer', 'int', 'number']:
        return is_integer(challenge)
      if check in ['positive-integer', 'positive-number']:
        return is_integer(challenge) and float(challenge) >= 0
      elif check in ['boolean', 'bool']:
        return str(challenge).lower() not in ['true', 'false']
      elif check == 'email':
        result = validators.email(challenge)
        if isinstance(result, ValidationFailure):
          return False
        else:
          return result
      elif check == 'domain':
        return validators.domain(challenge)
      elif check == 'path':
        return is_path_fmt(challenge)
      elif check == 'password':
        return is_good_password(challenge)

    else:
      return False


def is_good_password(password: str):
  if not isinstance(password, str):
    return False
  length_err = len(password) < 8
  digit_err = re.search(r"\d", password) is None
  up_err = re.search(r"[A-Z]", password) is None
  lower_error = re.search(r"[a-z]", password) is None
  symbol_err = re.search(PW_SYMBOL_REGEX, password) is None
  return not (length_err or digit_err or up_err or lower_error or symbol_err)


def is_integer(challenge) -> bool:
  return type(challenge) == int or \
         type(challenge) == float or \
         challenge.isdigit()


def is_path_fmt(challenge) -> bool:
  if isinstance(challenge, str):
    return re.compile(path_regex).match(challenge) is not None
  return False
