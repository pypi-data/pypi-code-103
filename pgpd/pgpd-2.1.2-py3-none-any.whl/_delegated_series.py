#
# Delegated Accessor Attributes for Series
#
from collections.abc import Iterable
from inspect import signature
from warnings import warn
import numpy as np
import pandas as pd
import pygeos
from ._util import rgetattr, get_summary
from ._array import GeosArray

__all__ = [
    'unary_return',
    'unary_none',
    'unary_series',
    'unary_series_indexed',
    'unary_series_keyed',
    'unary_dataframe_indexed',
    'unary_dataframe_keyed',
    'binary',
    'enable_dataframe_expand',
]


def unary_return(name, **defaults):
    """
    Create a method that returns the output of the function unmodified.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data and returns its result unmodified.

        Args:
            args: Arguments passed to :py:obj:`~pygeos.{func}` after the first argument.
            kwargs: Keyword arguments passed to :py:obj:`~pygeos.{func}`.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        return func(self._obj.array.data, *args, **kwargs)

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary)
    return delegated


def unary_none(name, **defaults):
    """
    Create a unary method that runs the pygeos function on the data and returns itself.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data.

        Args:
            args: Arguments passed to :py:obj:`~pygeos.{func}` after the first argument.
            kwargs: Keyword arguments passed to :py:obj:`~pygeos.{func}`.

        Returns:
            pandas.Series: returns the series for chaining.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        func(self._obj.array.data, *args, **kwargs)
        return self

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary)
    delegated.__DataFrameExpand__ = 1
    return delegated


def unary_series(name, index=None, geos=False, **defaults):
    """
    Create a method that returns a Series with values.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        index (list): Values to use as the index of the returned Series; Default **None**.
        geos (bool, optional): Whether the returned data is PyGEOS dtype; Default **False**.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data and returns a Series with the result.

        Returns:
            pandas.Series: Series with the results of the function.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        result = func(self._obj.array.data, *args, **kwargs)
        if geos:
            result = GeosArray(result)

        return pd.Series(result, index=index, name=func.__name__)

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary)
    if index is not None:
        delegated.__DataFrameExpand__ = 2
    return delegated


def unary_series_indexed(name, geos=False, **defaults):
    """
    Create a method that returns a Series with values, where each object in the original data maps to one new value.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        geos (bool, optional): Whether the returned data is PyGEOS dtype; Default **False**.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data and returns a Series with the result.

        Returns:
            pandas.Series: Series with the results of the function.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        result = func(self._obj.array.data, *args, **kwargs)
        if geos:
            result = GeosArray(result)

        return pd.Series(result, index=self._obj.index, name=func.__name__)

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary)
    delegated.__DataFrameExpand__ = 1
    return delegated


def unary_series_keyed(name, geos=False, **defaults):
    """
    Create a method that returns a Series with values, where each object in the original data can return a different number of values.
    The difference with :func:`unary_series` is that the pygeos method should return the index of the original data, so we can setup the index as a foreign key.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        geos (bool, optional): Whether the returned data is PyGEOS dtype; Default **False**.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data and returns a Series with the result.

        Returns:
            pandas.Series: Series with the results of the function.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        result, index = func(self._obj.array.data, *args, **kwargs)
        if geos:
            result = GeosArray(result)

        return pd.Series(result, index=self._obj.index[index], name=func.__name__)

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary)
    return delegated


def unary_dataframe_indexed(name, columns, geos=False, **defaults):
    """
    Create a method that returns a DataFrame, where each object in the original data maps to N new values (different columns).

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        columns (list<str>): List with column names.
        geos (bool or list<bool>, optional): Whether the returned data is PyGEOS dtype; Default **False**.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    if isinstance(geos, bool):
        geos = [geos] * len(columns)

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data and returns a Series with the result.

        Returns:
            pandas.Series: Series with the results of the function.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        result = func(self._obj.array.data, *args, **kwargs)
        if any(geos):
            result = [GeosArray(result[:, i]) if g else result[:, i] for g, i in zip(geos, range(result.shape[1]))]

        return pd.DataFrame(result, index=self._obj.index, columns=columns)

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary, columns=columns)
    return delegated


def unary_dataframe_keyed(name, columns, geos=False, **defaults):
    """
    Create a method that returns a DataFrame with values, where each object in the original data can return different rows of N values.
    The pygeos method should return the index of the original data, so we can setup the index as a foreign key.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        columns (list<str>): List with column names.
        geos (bool or list<bool>, optional): Whether the returned data is PyGEOS dtype; Default **False**.
        defaults (**kwargs): Default argument values that cannot be overwritten
    """
    try:
        func, func_summary, default_pos = get_func_info(name, defaults)
    except AttributeError:
        return None

    if isinstance(geos, bool):
        geos = [geos] * len(columns)

    def delegated(self, *args, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to the data and returns a Series with the result.

        Returns:
            pandas.Series: Series with the results of the function.
        """
        args, kwargs = setup_args(args, kwargs, defaults, default_pos)
        result, index = func(self._obj.array.data, *args, **kwargs)
        if any(geos):
            result = [GeosArray(result[:, i]) if g else result[:, i] for g, i in zip(geos, range(result.shape[1]))]

        return pd.DataFrame(result, index=self._obj.index[index], columns=columns)

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary, columns=columns)
    return delegated


def binary(name, geos=False, **defaults):     # noqa: C901
    """
    Create a binary method that runs a PyGEOS function on the original data and some other.

    Args:
        name (str): Name of the method within the ``pygeos`` module.
        geos (bool, optional): Whether the returned data is PyGEOS dtype; Default **False**.
    """
    try:
        func, func_summary = get_func_info(name)
    except AttributeError:
        return None

    def delegated(self, other=None, manner=None, **kwargs):
        """
        {summary}

        Applies :py:obj:`pygeos.{func}` to ``(self, other)`` and returns the result.
        If no ``other`` data is given, the function gets applied to all possible combinations of the ``self`` data, by expanding the array.

        Args:
            other (pandas.Series or numpy.ndarray or pygeos.Geometry, optional): Second argument to :py:obj:`~pygeos.{func}`; Default **self**.
            manner ('keep' or 'align' or 'expand', optional): How to apply the :py:obj:`~pygeos.{func}` to the data; Default **None** .
            kwargs: Keyword arguments passed to :py:obj:`~pygeos.{func}`.

        Returns:
            pandas.Series: Series with the result of the function applied to self and other, with the same index as self.
            numpy.ndarray: 2-Dimensional array with the results of the function applied to each combination of geometries between self and other.

        Raises:
            ValueError: ``other`` argument is not a geos Series or PyGEOS NumPy Array

        Note:
            The ``manner`` argument dictates how the data gets transformed before applying :py:obj:`~pygeos.{func}`:

            - **keep**:
                Keep the original data as is and simply run the function.
                This returns a Series where the index is the same as the ``self`` data.
            - **align**:
                Align both Series according to their index, before running the function (we align the data according the ``self`` data).
                This returns a Series where the index is the same as the ``self`` data.
            - **expand**:
                Expand the data with a new index, before running the function.
                This means that the result will be an array of dimensions ``<len(a), len(b)>`` containing the result of all possible combinations of geometries.

            Of course, not every method is applicable for each type of ``other`` input.
            Here are the allowed manners for each type of input, as well as the default value:

            - *Series*: keep, align, expand (default: align)
            - *1D ndarray*: keep, expand (default: keep)
            - *nD ndarray*: keep (default: keep)
            - *Geometry*: keep (default: keep)
            - *None* (aka. use self): expand (default: expand)
        """
        if manner is not None:
            manner = manner[0].lower()

        if other is None:
            if manner is not None and manner != 'e':
                warn('When no other is given, we always "expand" to an array')
            data = self._obj.array.data[:, np.newaxis]
            other = self._obj.array.data[np.newaxis, :]
        elif isinstance(other, pd.Series):
            if not (pd.api.types.pandas_dtype('geos') == other.dtype):
                raise ValueError('"other" should be of dtype "geos".')

            if manner == 'e':
                data = self._obj.array.data[:, np.newaxis]
                other = other.array.data[np.newaxis, :]
            else:
                this = self._obj
                if (manner is None or manner == 'a') and not this.index.equals(other.index):
                    warn('The indices of the two Series are different, so we align them.')
                    this, other = this.align(other)

                data = this.array.data
                other = other.array.data
        elif isinstance(other, np.ndarray):
            if other.ndim == 1:
                data = self._obj.array.data
                if manner == 'e':
                    data = self._obj.array.data[:, np.newaxis]
                    other = other[np.newaxis, :]
                elif manner == 'a':
                    warn('Cannot align a NumPy Array.')
            else:
                if manner == 'e':
                    warn('Cannot expand a multi-dimensional NumPy Array')
                elif manner == 'a':
                    warn('Cannot align a NumPy Array.')

                data = self._obj.array.data
        elif isinstance(other, pygeos.lib.Geometry):
            data = self._obj.array.data
            if manner is not None and manner != 'k':
                warn('Cannot align or expand a single Geometry')
        else:
            raise ValueError('"other" should be a geos Series or PyGEOS NumPy array')

        kwargs = {**kwargs, **defaults}
        result = func(data, other, **kwargs)
        if not isinstance(result, np.ndarray):
            result = result if isinstance(result, Iterable) else [result]
            result = np.array(result)

        if result.ndim == 1 and result.shape[0] == self._obj.shape[0]:
            if geos:
                result = GeosArray(result)
            return pd.Series(result, index=self._obj.index, name=func.__name__)
        else:
            return result

    delegated.__doc__ = setup_docstring(delegated.__doc__, defaults, func=name, summary=func_summary)
    return delegated


def enable_dataframe_expand(expansion=1):
    def decorator(func):
        func.__DataFrameExpand__ = expansion
        return func

    # Allow to use decorator without calling
    if callable(expansion):
        expansion.__DataFrameExpand__ = 1
        return expansion
    else:
        return decorator


def get_func_info(name, defaults=None):
    func = rgetattr(pygeos, name)
    func_summary = get_summary(func.__doc__)
    if defaults is None:
        return func, func_summary

    positions = {}
    for idx, (name, param) in enumerate(signature(func).parameters.items()):
        if name in defaults and param.kind == param.POSITIONAL_OR_KEYWORD:
            positions[idx] = name

    return func, func_summary, positions


def setup_args(args, kwargs, defaults, positions):
    if len(defaults) > 0 and len(args) > 0:
        defaults = defaults.copy()
        for i in range(len(args)):
            if i in positions:
                args[i] = defaults.pop(positions[i])
    return args, {**kwargs, **defaults}


def setup_docstring(string, defaults, **kwargs):
    string = string.format(**kwargs)
    if len(defaults) != 0:
        string += f'\n        Note:\n            The pygeos functions gets called with these default values that cannot be overwritten: `{defaults}`'
    return string
