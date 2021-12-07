import fnmatch
import pandas
import numpy as np
import pandas as pd
from slugify import slugify

from . import xsettings
from . import xagg


def x_match(self, values, exclude=False):
    """
    Filter DataFrame by column values

    Examples:
    >> df['animal'].x_match(['cat', 'dog', '*ouse'], exclude=True)
    """

    possible_values = self.unique()

    if isinstance(values, str):
        values = [values]

    keep_exact = []
    for keep_pattern in values:
        if isinstance(keep_pattern, str):
            vals = [v for v in possible_values if fnmatch.fnmatch(v, keep_pattern)]
            keep_exact.extend(vals)

        else:
            keep_exact.append(keep_pattern)

    idxs = self.isin(keep_exact)
    if exclude:
        idxs = ~idxs

    return idxs


def x_filter_by(self, values, col_name, exclude=False, dropna=True, ignore_index=None, sanity_checks=None):
    """
    Filter DataFrame by column values

    Examples:
    >> df.x_filter_by(['cat', 'dog', '*ouse'], 'animal', exclude=True)
    """

    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)
    sanity_checks = xsettings.get_default(xsettings.SANITY_CHECKS, sanity_checks)

    if dropna:
        self = self.dropna(subset=[col_name])

    idxs = x_match(self[col_name], values, exclude=exclude)

    df_filtered = self[idxs]

    if ignore_index:
        df_filtered = df_filtered.reset_index(drop=True)

    if sanity_checks:
        assert len(df_filtered) > 0, f"attr_name={col_name}, keep_values={values}, exclude={exclude}"

    return df_filtered


def x_split_on(self, values, col_name, ignore_index=None):
    """
    Filters & splits dataframe by values

    >> df_cats, df_dogs = df.x_split_on(['cat', 'dog'], 'animal')
    """
    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)

    res = []
    for value in values:
        df_value = self.x_filter_by([value], col_name, ignore_index=ignore_index)
        res.append(df_value)

    return tuple(res)


def x_append(self, other, ignore_index=None, verify_integrity=False, sort=False):
    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)

    if self is None:
        return other

    if other is None:
        return self

    return self.append(other, ignore_index=ignore_index, verify_integrity=verify_integrity, sort=sort)


def x_replace(self, valid_vals=tuple(), replace_vals=None, default=None):
    replace_vals = replace_vals or dict()
    valid_vals = tuple(set(valid_vals) | set(replace_vals.keys()) | set(replace_vals.values()))

    def do(x):
        if x not in valid_vals:
            return default

        return replace_vals.get(x, x)

    sa_replaced = self.apply(do)
    return sa_replaced


def x_clean_text(self):
    return self.apply(lambda x: slugify(x, separator="_"))


def x_as_float(self, nan_texts=None):
    nan_texts = xsettings.get_default(xsettings.NAN_TEXTS, nan_texts)

    def conv(x):
        try:
            return np.float(x)
        except ValueError:
            if x.strip() in nan_texts:
                return np.nan
            raise ValueError(x)

    return self.apply(conv)


def x_groupby(self, by, aggs, ignore_index=None, **kwargs):
    """
    A simpler groupby interface
    (inspired by Turicreate)

    >> df.x_groupby('a', {'min_b': xagg.Min('b'), 'max_c': xagg.Max('c'), 'n': xagg.Count()})
    """

    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)

    d = dict()
    for k, v in aggs.items():
        if isinstance(v, xagg._Agg):
            tup = v.as_tuple()
            if tup[0] is None:
                tup = tuple([self.columns[0], tup[1]])
            d[k] = tup

        elif isinstance(v, tuple):
            d[k] = v

        else:
            raise ValueError(f"{k}: {v}")

    g = self.groupby(by=by, **kwargs).agg(**d)

    if ignore_index:
        g = g.reset_index()

    return g


def x_calc_rank_num(self, key_col_name, score_col_name, ascending=True):
    """
    creates a series ranking each group of key_col_name by score_col_name

    >> df.x_calc_rank_num('user_id', 'product_score', ascending=False)
    """

    return self.groupby(key_col_name)[score_col_name].rank(ascending=ascending).astype(int)


def x_add_history(self, key, value):
    if not hasattr(self, '_x_history'):
        self._metadata.append('_x_history')
        self._x_history = []

    self._x_history.append((key, value))


def x_get_history(self):
    if not hasattr(self, '_x_history'):
        return []

    return self._x_history


def x_set_data_type(self, data_type):
    """
    sets logical data type: binary, nominal, ordinal, interval, ratio, temporal, geojson
    (inspired by altair, etc.)
    what about cyclical? (can be either ordinal [day of week] or interval [hour of day]
    """

    if not hasattr(self, '_x_data_type'):
        self._metadata.append('_x_data_type')

    data_type = data_type.lower()[0]
    data_type = {
        'b': 'binary',
        'n': 'nominal',
        'o': 'ordinal',
        'i': 'interval',
        'r': 'ratio',
        'q': 'ratio',
        't': 'temporal',
        'g': 'geojson'
    }[data_type]

    self._x_data_type = data_type


def x_get_data_type(self):
    if not hasattr(self, '_x_data_type'):
        return None

    return self._x_data_type


def x_set_column_type(self, column_type):
    """
    sets logical column type: target, feature, meta, key
    - a target variable
    - a feature (can be used for training)
    - meta data (not to use as a training feature, but might be confounding)
    - a sample key (should be unique)
    """

    if not hasattr(self, '_x_column_type'):
        self._metadata.append('_x_column_type')

    column_type = column_type.lower()[0]
    column_type = {
        't': 'target',
        'f': 'feature',
        'm': 'meta',
        'k': 'key'
    }[column_type]

    self._x_column_type = column_type


def x_get_column_type(self):
    if not hasattr(self, '_x_column_type'):
        return None

    return self._x_column_type


def x_rename(self, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='raise'):
    if columns is not None:
        desc_dict = {v: xsettings.COL_DESC.get(k, k) for k, v in columns.items()}
        xsettings.COL_DESC.update(desc_dict)

    self_orig = self
    self = self.rename(mapper=mapper, index=index, columns=columns, axis=axis, copy=copy, inplace=inplace, level=level, errors=errors)

    self = self if self is not None else self_orig
    return self


def x_sort_on_lookup(self: pd.DataFrame, on, sa_lookup: pd.Series, ascending=True):
    """
    Given lookup Series, merge it based 'on', and then sort, and remove
    df.x_sort_on_lookup('height', df.groupon('height')['width'].mean())
    """
    df = self.copy()
    df['tmp_x_sort_on_lookup'] = df.apply(lambda r: sa_lookup[r[on]], axis=1)
    df = df.sort_values('tmp_x_sort_on_lookup', ascending=ascending)
    del df['tmp_x_sort_on_lookup']
    return df


def x_clean_column_names(self, inplace=False):
    """
    renames columns to pythonable names, " Hi there" --> "hi_there"
    """

    orig_columns = self.columns
    new_columns = [slugify(c, separator='_') for c in orig_columns]
    assert len(set(new_columns)) == len(orig_columns), "not all column names become unique"

    rename_dict = dict(zip(orig_columns, new_columns))
    return x_rename(self, columns=rename_dict, inplace=inplace)


def x_apply_multi(self):
    # TODO: do
    return self


def x_drop_by_counts(self, count_on, keep_count):
    """
    count number of unique values for `count_on`, and filter df by `keep_count`
    """

    sa_counts = self[count_on].value_counts()
    sa_counts = sa_counts[sa_counts == keep_count]
    self = self.x_filter_by(sa_counts.index.values, count_on)
    return self


def x_timedelta_as_hours(self):
    """
    Given a Series containing Timedelta, converts it to Series containing hours (float)
    """
    return self.apply(lambda d: d.days * 24 + d.seconds / (60 * 60))


def monkey_patch():
    pandas.Series.x_match = x_match
    pandas.Series.x_replace = x_replace
    pandas.Series.x_clean_text = x_clean_text
    pandas.Series.x_add_history = x_add_history
    pandas.Series.x_get_history = x_get_history
    pandas.Series.x_set_data_type = x_set_data_type
    pandas.Series.x_get_data_type = x_get_data_type
    pandas.Series.x_set_column_type = x_set_column_type
    pandas.Series.x_get_column_type = x_get_column_type
    pandas.Series.x_as_hours = x_timedelta_as_hours

    pandas.DataFrame.x_filter_by = x_filter_by
    pandas.DataFrame.x_split_on = x_split_on
    pandas.DataFrame.x_append = x_append
    pandas.DataFrame.x_groupby = x_groupby
    pandas.DataFrame.x_calc_rank_num = x_calc_rank_num
    pandas.DataFrame.x_add_history = x_add_history
    pandas.DataFrame.x_get_history = x_get_history
    pandas.DataFrame.x_clean_column_names = x_clean_column_names
    pandas.DataFrame.x_rename = x_rename
    pandas.DataFrame.x_sort_on_lookup = x_sort_on_lookup



