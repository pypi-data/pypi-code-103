"""
Pandas Accessors with Helper Functions for 
Aggregating and Manipulating Statements
"""
import functools as ft
import pandas as pd

class UtilsMixin:
    ### FStat Extension Utilities for Statements; 
    ### This is mixed in to Statement Objects (NOT a pandas accessor) ###
    def __init__(self, *args, **kwargs):
        from finstat.finstat import BaseBSheet, BaseIStat

        if isinstance(self, BaseIStat):
            self.UTILITY = IStatUtils
        elif isinstance(self, BaseBSheet):
            self.UTILITY = BSheetUtils
        else:
            raise ValueError(f'Statement not recognized {type(self)}')
        
    @property
    def utils(self):
        if not hasattr(self, '_utils'):
            self._utils = self.UTILITY(self)
        
        return self._utils

    def resample(self, *args, **kwargs):
        if hasattr(self, 'aggfuncs'):
            kwargs['aggfunc'] = self.aggfuncs

        return self.utils.resample(stat=self.stat, *args, **kwargs)

    def sgmts(self):
        return self.utils.sgmts()

    def accts(self):
        return self.utils.accts()

    def annually(self, *args, **kwargs):
        if hasattr(self, 'aggfuncs'):
            kwargs['aggfunc'] = self.aggfuncs
        return self.utils.annually(*args, **kwargs)

    def quarterly(self, *args, **kwargs):
        if hasattr(self, 'aggfuncs'):
            kwargs['aggfunc'] = self.aggfuncs
        return self.utils.quarterly(*args, **kwargs)

class FStatUtils:
    """
    Pandas extension to add common styles to dataframes in Jupyter Notebook
    """
    RANK = {
        'A-DEC': 2,
        'Q-DEC': 1,
        'M': 0,
    }
    DIVISOR = {
        'A-DEC': {'Q-DEC': 4, 'M': 12},
        'Q-DEC': {'M': 3}
    }

    def __init__(self, obj):
        self._statobj = obj
        self._obj = obj.stat

    def parse_period(self, period):
        if period in ['A', 'a', 'annual', 'annually']:
            period = 'A-DEC'
        if period in ['Q', 'q', 'quarter', 'quarterly']:
            period = 'Q-DEC'
        if period in ['M', 'm', 'month', 'mon', 'monthly']:
            period = 'M'
        
        return period

    def by_acct(self, acct, drop=False):
        if self._obj.index.nlevels > 1:
            return self._obj.xs(acct, level='Account', drop_level=drop)
        else:
            return self._obj.loc[acct]

    def annually(self, period='A-DEC', **kwargs):
        return self.resample(period=period, **kwargs)

    def quarterly(self, period='Q-DEC', **kwargs):
        return self.resample(period=period, **kwargs)

    def monthly(self, period='M', **kwargs):
        return self.resample(period=period, **kwargs)

    def sgmts(self):
        if 'Segment' not in self._obj.index.names:
            raise ValueError('This statement does not have Segments')

        return self._obj.groupby(['Segment', 'Account']).sum()

    def accts(self):
        return self._obj.groupby('Account').sum()

    def clip_rng(self, df, clip_rng):
        if clip_rng and isinstance(clip_rng, pd.PeriodIndex):
            colmask = clip_rng
        else:
            colmask = (self._statobj._START <= df.columns) & (self._statobj._END >= df.columns)
        return df.loc[:, colmask]

def resampler(func):
    @ft.wraps(func)
    def wrapper(self, period, sgmts=False, accts=False, clip_rng=[], str_cols=False, stat=None, **kwargs):
        if stat is not None:
            self._obj = stat

        if sgmts:
            self._temp = self.sgmts()
        elif accts:
            self._temp = self.accts()
        else:
            self._temp = self._obj

        if clip_rng:
            self._temp = self.clip_rng(self._temp, clip_rng)

        self._temp = self._temp.sort_index()

        period = self.parse_period(period)
        self._temp = func(self, period, **kwargs)
        if str_cols:
            strf = '%Y' if period == 'A-DEC' else '%b-%y'
            self._temp.columns = self._temp.columns.strftime(strf)

        return self._temp

    return wrapper

class IStatUtils(FStatUtils):
    @resampler
    def resample(self, period, aggfunc='', **kwargs):
        if aggfunc:
            return self._temp.T.resample(period).agg(aggfunc).T
        else:
            if self.RANK[period] >= self.RANK[self._temp.columns.freqstr]:
                return self._temp.T.resample(period).sum().T
            else:
                divint = self.DIVISOR[self._temp.columns.freqstr][period]
                return (self._temp.T.resample(period).asfreq().T / divint).ffill(axis=1)

class BSheetUtils(FStatUtils):
    @resampler
    def resample(self, period, aggfunc='', **kwargs):
        if self.RANK[period] >= self.RANK[self._temp.columns.freqstr]:
            if isinstance(aggfunc, list):
                stats = []
                for func in aggfunc:
                    stat = self._temp.loc[list(func.values())[0]].T.resample(period).agg(list(func.keys())[0]).T
                    stats.append(stat)
                df = pd.concat(stats)
                newidx = df.index.to_frame().reset_index(drop=True)
                newidx.Account = pd.CategoricalIndex(newidx.Account, categories=self._temp.index.get_level_values(0).categories, ordered=True)
                multindex = pd.MultiIndex.from_frame(newidx)
                df.index = multindex
                self._temp = df.sort_index()
                return self._temp
            else:
                aggfunc = 'last' if not aggfunc else aggfunc
                return self._temp.T.resample(period).agg(aggfunc).T
        else:
            raise ValueError('Balance Sheet cannot be downsampled')

@pd.api.extensions.register_dataframe_accessor('isutils')
class IStatExt(IStatUtils):
    """
    Pandas extension to add common styles to dataframes in Jupyter Notebook
    """
    def __init__(self, obj):
        self._obj = obj

@pd.api.extensions.register_dataframe_accessor('bsutils')
class BSheetExt(BSheetUtils):
    """
    Pandas extension to add common styles to dataframes in Jupyter Notebook
    """
    def __init__(self, obj):
        self._obj = obj
