#
# Delegated Accessor Attributes for DataFrames
#
import pandas as pd
from ._util import rgetattr, get_summary
from ._accessor_series import GeosSeriesAccessor

__all__ = ['unary_dataframe_expanded']


def unary_dataframe_expanded(name, expansion):
    """
    Create a unary method that calls the :class:`pgpd.GeosSeriesAccessor` method
    on each geos column and aggregates the result.

    Args:
        name (str): Name of the method in the :class:`pgpd.GeosSeriesAccessor`.
        expansion (int): Type of dataframe expansion
    """
    func_summary = get_summary(rgetattr(GeosSeriesAccessor, f'{name}.__doc__', None))

    def delegated1(self, *args, inplace=False, **kwargs):
        """
        {summary}

        Applies :func:`pgpd.GeosSeriesAccessor.{func}` to each column of "geos" dtype
        and aggregates the results in a DataFrame.

        Args:
            args: Arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}` after the first argument.
            inplace (bool, optional): Whether to perform the modifications inplace; Default **False**.
            kwargs: Keyword arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}`.

        Returns:
            pandas.DataFrame or None:
                DataFrame where each "geos" column from the original is transformed or None if ``inplace=True``.
        """
        result = {}
        remainder = []
        for column, dtype in self._obj.dtypes.iteritems():
            if pd.api.types.pandas_dtype('geos') == dtype:
                result[column] = getattr(self._obj[column].geos, name)(*args, **kwargs)
            else:
                remainder.append(column)

        if not inplace:
            return pd.DataFrame.from_dict({**{col: self._obj[col].copy() for col in remainder}, **result})
        else:
            for column, values in result.items():
                self._obj[column] = values

    def delegated2(self, *args, **kwargs):
        """
        {summary}

        Applies :func:`pgpd.GeosSeriesAccessor.{func}` to each column of "geos" dtype
        and aggregates the results in a DataFrame.

        Args:
            args: Arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}` after the first argument.
            kwargs: Keyword arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}`.

        Returns:
            pandas.DataFrame:
                DataFrame with the results `{func}` for each of the geos columns.
        """
        result = {}
        for column, dtype in self._obj.dtypes.iteritems():
            if pd.api.types.pandas_dtype('geos') == dtype:
                result[column] = getattr(self._obj[column].geos, name)(*args, **kwargs)

        return pd.DataFrame.from_dict(result)

    if expansion == 1:
        delegated1.__doc__ = delegated1.__doc__.format(func=name, summary=func_summary)
        return delegated1
    else:
        delegated2.__doc__ = delegated2.__doc__.format(func=name, summary=func_summary)
        return delegated2
