#!/usr/bin/env python3

"""Easy statistics

The main class `Statistics` just extends `dict{str:function}`,
where `function` will act on the object of statistics.
As the value of dict, `function` has not to be a function.
If it is a string, then the attribute of object will be called.

Please see the following example and the function `_call`, the underlying implementation.

Pseudo codes:
    ```
    if s: str
        f = getattr(obj, s)
        if f: function
            r = f()
        else
            r = f
    elif s: function
        r = s(obj)
    elif s is number:
        r = s
    ```

Example:

    >>> import numpy as np

    >>> T = np.random.random((100,100))
    >>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
    >>> print(s(T))
    >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

    >>> print(s(T, split=True)) # split the tuple if it needs
    >>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape[0]': 100, 'shape[1]': 100}

`MappingStatistics` subclasses Statistics. It only copes with iterable object,
and maps it to an array by a "key" function.

Example:

    >>> s = MappingStatistics('mean', {'mean':np.mean, 'max':np.max})
    >>> print(s(T))
    >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957}

In the exmaple, 'mean', an attribute of T, maps T to a 1D array.


Advanced Usage:
`Statistics` acts on a list/tuple of objects iteratively, gets a series of results,
forming an object of pandas.DataFrame.

    history = pd.DataFrame(columns=s.keys())
    for obj in objs:
        history = history.append(s(obj), ignore_index=True)

"""

from typing import Callable, Iterable, Dict, Union, TypeVar

import pandas as pd
import numpy as np

Constant = TypeVar('Constant', int, float, tuple)
Statistic = Union[str, Callable, Constant]
Result = Dict[str, Constant]


def _call(s, obj):
    """Core function of ezstat
    
    s {function | string} -- Statistics
    obj -- object of statistics
    
    An extension for s(x) or x.s
    If s is an string, then it only returns x.s() if callable, otherwise x.s.

    The return value should be a number or a tuple of numbers.
    """
    if isinstance(s, str):
        if not hasattr(obj, s):
            raise ValueError(f"the object has no attribute '{s}'")
        f = getattr(obj, s)
        r = f() if callable(f) else f
    elif callable(s):
        r = s(obj)
    elif isinstance(s, Constant):
        # print('Deprecated to use a constant number!')
        r = s
    else:
        raise TypeError(f"The type of `{s}` is not permissible!") 

    return r


class Statistics(dict):
    """
    Statistics is a type of dict{str:function},
    where `function` will act on the object of statistics.
    As the value of dict, `function` has not to be a function.
    If it is a string, then the attribute of object will be called.
    """

    def do(self, obj, split:bool=False) -> Result:
        """Execute a staistical task

        Arguments:
            obj {object} -- an object (population) of statistics
            split {bool} -- if True, it will split the tuple-type statistics result to numbers
        
        Returns:
            dict

        Example:
        >>> import numpy as np

        >>> T = np.random.random((100,100))
        >>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
        >>> print(s(T))
        >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

        >>> print(s(T, split=True)) # split the tuple if it needs
        >>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape-0': 100, 'shape-1': 100}
        """
        res = {}
        for k, s in self.items():
            # if s is True and isinstance(k, str):
            #     r = _call(k, obj)
            r = _call(s, obj)
  
            if split and isinstance(r, Iterable):
                for i, ri in enumerate(r):
                    res[f'{k}[{i}]'] = ri
            else:
                res[k] = r
        return res

    def dox(self, objs:Iterable):
        # wrap the sequence of statistical resutls as a dataframe
        return pd.DataFrame(data=map(self, objs), columns=self.keys())

    __call__= do # alias of do


class MappingStatistics(Statistics):
    """Just a wrapper of `Statistics`

    Only recommanded to cope with iterable object of statistics.
    It will transfrom the object to array by `key` (functional attribute) before doing statistics.
    
    Extends:
        Statistics

    Example:
    >>> import numpy as np

    >>> T = np.random.random((100,100))
    >>> s = MappingStatistics('mean', {'mean':np.mean, 'min':np.min})
    >>> print(s(T))
    >>> {'mean': 0.4995186088546244, 'min': 0.39975807140966796}

    In the exmaple, 'mean', an attribute of np.ndarray, maps each row of T to a number.
    As a result, the object of statistics is a 1D array.
    """

    def __init__(self, key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, v):
        self._key = v
    
    def do(self, obj:Iterable, split:bool=False)->Result:
        """
        The object of statistics should be iterable
        """
        if self.key:
            obj = np.array([_call(self.key, obj_) for obj_ in obj]) # should be an array of numbers
        return super().do(obj, split=split)

if __name__ == "__main__":
    import numpy as np

    T = np.random.random((100,100))
    s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
    print(s(T))
    # {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

    print(s(T, split=True)) # split the tuple if it needs
    # {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape[0]': 100, 'shape[1]': 100}
