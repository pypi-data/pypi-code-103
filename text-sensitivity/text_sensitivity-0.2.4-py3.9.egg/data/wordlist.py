from functools import lru_cache
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from genbase import CaseMixin, Readable, SeedMixin

Label = Union[str, int]


class WordList(Readable, SeedMixin, CaseMixin):
    def __init__(self,
                 wordlist: pd.DataFrame,
                 main_column: Optional[Label] = None,
                 seed: int = 0):
        self.wordlist = wordlist
        self.__wordlist = wordlist.copy(deep=True)
        self.main_column = main_column
        self._seed = self._original_seed = seed
        self._lowercase = self._sentencecase = self._titlecase = self._uppercase = False

    @classmethod
    def from_list(cls, wordlist: List[str], name: Label = 'words', seed: int = 0):
        return cls(pd.DataFrame(wordlist, columns=[name]), seed=seed)

    @classmethod
    def from_dictionary(cls,
                        wordlist: Dict,
                        key_name: Label = 'key',
                        value_name: Label = 'value',
                        value_as_main: bool = False,
                        seed: int = 0):
        main_column = value_name if value_as_main else key_name
        return cls(pd.DataFrame(wordlist, columns=[key_name, value_name]), main_column=main_column, seed=seed)

    @classmethod
    def from_dict(cls, *args, **kwargs):
        """Alias for `WordList.from_dictionary()`."""
        return cls.from_dictionary(*args, **kwargs)

    @classmethod
    def from_csv(cls, filename: str, main_column: Optional[Label] = None, seed: int = 0, *args, **kwargs):
        return cls(pd.read_csv(filename, *args, **kwargs), main_column=main_column, seed=seed)

    @classmethod
    def from_json(cls, filename: str, main_column: Optional[Label] = None, seed: int = 0, *args, **kwargs):
        return cls(pd.read_json(filename, *args, **kwargs), main_column=main_column, seed=seed)

    @classmethod
    def from_excel(cls, filename: str, main_column: Optional[Label] = None, seed: int = 0, *args, **kwargs):
        return cls(pd.read_excel(filename, *args, **kwargs), main_column=main_column, seed=seed)

    @classmethod
    def from_pickle(cls, filename: str, main_column: Optional[Label] = None, seed: int = 0, *args, **kwargs):
        return cls(pd.read_pickle(filename, *args, **kwargs), main_column=main_column, seed=seed)

    @classmethod
    def from_file(cls, filename: str, main_column: Optional[Label] = None, seed: int = 0, *args, **kwargs):
        import os
        extension = str.lower(os.path.splitext(filename)[1])

        if extension == 'csv':
            return cls.from_csv(filename=filename, main_column=main_column, seed=seed, *args, **kwargs)
        elif extension == 'json':
            return cls.from_json(filename=filename, main_column=main_column, seed=seed, *args, **kwargs)
        elif extension in ['xls', 'xlsx']:
            return cls.from_excel(filename=filename, main_column=main_column, seed=seed, *args, **kwargs)
        elif extension == 'pkl':
            return cls.from_pickle(filename=filename, main_column=main_column, seed=seed, *args, **kwargs)
        else:
            return cls(pd.read_table(filename, main_column=main_column, seed=seed, *args, **kwargs),
                       main_column=main_column)

    @lru_cache(1)
    def get(self,
            sort_by: Optional[Label] = None,
            **sort_kwargs):
        wordlist = self.wordlist.sort_values(by=sort_by, **sort_kwargs) if sort_by is not None else self.wordlist
        col = wordlist.iloc[:, 0] if self.main_column is None or self.main_column not in self.wordlist.columns \
              else wordlist.loc[:, self.main_column]
        return [self.apply_case(c) for c in list(col)]

    def generate_list(self,
                      n: Optional[int] = None,
                      likelihood_column: Optional[Label] = None):
        if n is None or isinstance(n, int) and n >= len(self.wordlist.index):
            return self.get()
        if likelihood_column is not None:
            likelihood_column = self.wordlist[likelihood_column].values / self.wordlist[likelihood_column].sum()
        np.random.seed(self._seed)
        return list(np.random.choice(self.get(), size=n, replace=False, p=likelihood_column))

    def filter(self,
               column: Label,
               values: Union[Label, List[Label]]):
        if not isinstance(values, list):
            values = [values]
        self.wordlist = self.wordlist[self.wordlist[column].isin(values)]
        return self

    def reset(self):
        self.wordlist = self.__wordlist.copy(deep=True)
        return self

    def __len__(self):
        return len(self.get())

    def __getitem__(self, item):
        return self.get()[item]


class WordListGetterMixin:
    def get(self, *args, **kwargs):
        return self.wordlist.get(*args, **kwargs)

    def generate_list(self, *args, **kwargs):
        return self.wordlist.generate_list(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self.wordlist.filter(*args, **kwargs)

    def reset(self):
        return self.wordlist.reset()

    def __len__(self):
        return len(self.wordlist)
