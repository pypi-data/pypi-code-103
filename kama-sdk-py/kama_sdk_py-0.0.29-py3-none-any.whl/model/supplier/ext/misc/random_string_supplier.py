import random
import string
from functools import reduce
from typing import Any

from werkzeug.utils import cached_property

from kama_sdk.model.supplier.base.supplier import Supplier


class RandomStringSupplier(Supplier):

  def get_symbol_groups(self):
    return self.get_attr(SYMBOLS_KEY, backup=['letters'])

  def get_string_length(self):
    return self.get_attr(LENGTH_KEY, backup=16)

  def get_output_spec(self):
    return None

  def _compute(self) -> Any:
    reducer = lambda whole, group: f"{whole}{self.populate_symbols(group)}"
    symbols = list(reduce(reducer, self.get_symbol_groups(), ''))
    random.shuffle(symbols)
    scrambled = random.choices(symbols, k=self.get_string_length())
    return ''.join(scrambled)

  @staticmethod
  def populate_symbols(group_name: str) -> str:
    if group_name == 'letters':
      return string.ascii_letters
    elif group_name == 'numbers':
      return string.digits
    elif group_name == 'punctuation':
      return string.punctuation
    else:
      print(f"[kama_sdk:rss] unknown symbol group {group_name}")
      return ''


SYMBOLS_KEY = 'symbols'
LENGTH_KEY = 'length'
