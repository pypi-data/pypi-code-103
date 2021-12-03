import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt

from bluebelt.core.checks import check_kwargs

import bluebelt.core.decorators


def resolution_methods(cls):

    def sum(self):
        self.result = self.result.sum()
        self.func = 'sum'
        return self

    def mean(self):
        self.result = self.result.mean()
        self.func = 'mean'
        return self

    def var(self):
        self.result = self.result.var()
        self.func = 'variance'
        return self

    def std(self):
        self.result = self.result.std()
        self.func = 'standard deviation'
        return self

    def min(self):
        self.result = self.result.min()
        self.func = 'min'
        return self

    def max(self):
        self.result = self.result.max()
        self.func = 'max'
        return self
    
    def count(self):
        self.result = self.result.count()
        self.func = 'count'
        return self
    
    def value_range(self):
        self.result = self.result.apply(lambda x: x.max() - x.min())
        self.func = 'value range'
        return self

    def inter_scale(self):
        self.result = ( (self.result.sum() - self.result.sum().shift(fill_value= self.result.sum()[0])) / self.result.sum().shift(fill_value= self.result.sum()[0]) ).abs()
        self.func = 'inter_scale'
        return self

    def intra_scale(self):

        result = self.result.apply(lambda s: s.set_axis(s.index.weekday)).unstack(level=-1)

        self.result = pd.Series((result - result.shift().multiply((result.sum(axis=1) / result.sum(axis=1).shift()), axis=0)).abs().sum(axis=1) / (result.sum(axis=1) * 2), name=self.series.name)
        self.func = 'intra_scale'
        return self
    

    def subsize_count(self, count=3, size=1):
        """
        Count the number of times a list of <count> items with size <size> fit in the groupby object (which is a pandas Series)
        e.g.
        groupby object: pd.Series([10, 8, 3, 3, 5])
        count = 3
        size = 1

        returns 9

        step 0: (3, 3, 5, 8, 10)
        step 1: (3, 3, 4, 7, 9)
        step 2: (3, 3, 3, 6, 8)
        step 3: (2, 3, 3, 5, 7)
        step 4: (2, 2, 3, 4, 6)
        step 5: (2, 2, 2, 3, 5)
        step 6: (1, 2, 2, 2, 4)
        step 7: (1, 1, 1, 2, 3)
        step 8: (0, 1, 1, 1, 2)
        step 9: (0, 0, 0, 1, 1)

        """
        if isinstance(count, (float, int)):
            count = [int(count)]
        
        result = {}
        for c in count:
            result[c] = self.result.apply(lambda x: _subsize_count(series=x, count=c, size=size)).values
        self.result = pd.DataFrame(result, index=self.result.groups.keys()) #self.result.apply(lambda x: _subsize_count(series=x, count=count, size=size))
        self.func = f'count subsize (count={count}, size={size})'
        
        if len(count) == 2:
            d = {}
            #arr = self.result.values.T
            for val in range(int(self.result.values.min()), int(self.result.values.max())):
                
                if self.result.iloc[:,0].mean() > self.result.iloc[:,1].mean():
                #if arr[0].mean() > arr[1].mean():
                    d[val] = self.result.shape[0] - self.result[(self.result.iloc[:,0]>val) & (self.result.iloc[:,1]<val)].shape[0]
                    #d[val] = arr[0][arr[0]<val].size + arr[1][arr[1]>val].size
                else:
                    d[val] = self.result.shape[0] - self.result[(self.result.iloc[:,0]<val) & (self.result.iloc[:,1]>val)].shape[0]
                    #d[val] = arr[0][arr[0]>val].size + arr[1][arr[1]>val].size

            out_of_bounds = np.min(list(d.values()))
            keys = list({key:value for (key,value) in d.items() if value == out_of_bounds}.keys())
            
            self.optimum = (np.min(keys), np.max(keys))
            self.out_of_bounds = out_of_bounds
        else:
            self.optimum = None
            self.out_of_bounds = None

        return self

    def subseries_count(self, subseries=None, **kwargs):
        """
        Count the number of times a subseries of wil fit in the groupby object (which is a pandas Series)
        
        Under construction!! Not valid on extreme value differences...

        e.g.
        groupby object: pd.Series([10, 8, 3, 3, 5])
        subseries: pd.Series([1, 2, 3])

        returns 4

        step 0: (3, 3, 5, 8, 10)
        step 1: (3, 3, 4, 6, 7)
        step 2: (3, 3, 3, 4, 4)
        step 3: (2, 3, 3, 2, 1)
        step 4: (1, 1, 0, 2, 1)

        """
        self.result = self.result.apply(lambda x: _subseries_count(series=x, subseries=subseries, **kwargs))
        self.func = f'count subseries (subseries={list(subseries)})'
        return self

    def plot(self, **kwargs):

        if self.func == '':
            series = self.result.sum()
            func = 'sum'
        else:
            series = self.result
            func = self.func

        style = kwargs.pop('style', bluebelt.styles.paper)
        path = kwargs.pop('path', None)

        xlim = kwargs.pop('xlim', (None, None))
        ylim = kwargs.pop('ylim', (None, None))

        fig, ax = plt.subplots(**kwargs)

        # observations
        ax.plot(series, **style.resolution.plot)

        xlims = ax.get_xlim()
        
        # mean
        if hasattr(self, 'optimum'):
            if self.optimum is not None:
                ax.fill_between(xlims, self.optimum[0], self.optimum[1], **style.resolution.optimum_fill_between)
                ax_text = f'bounds: {self.optimum[0]:1.0f} - {self.optimum[1]:1.0f}\nout of bounds: {self.out_of_bounds}'
                ax.text(0.02, 0.98, ax_text, transform=ax.transAxes, **style.resolution.bounds_text)
            else:
                ax.axhline(series.values.mean(), **style.resolution.axhline)
                ax.text(series.index.values.min(), series.values.mean(), f'{series.values.mean():1.2f}', **style.resolution.text)

        # labels
        ax.set_title(f'{self.series.name} grouped', **style.resolution.title)
        ax.set_xlabel(self.rule)
        ax.set_ylabel(func)

        #reset xlim
        ax.set_xlim(xlims)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    

        if path:
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig

    setattr(cls, 'sum', sum)
    setattr(cls, 'mean', mean)
    setattr(cls, 'var', var)
    setattr(cls, 'std', std)
    setattr(cls, 'min', min)
    setattr(cls, 'max', max)
    setattr(cls, 'count', count)
    setattr(cls, 'value_range', value_range)
    setattr(cls, 'intra_scale', intra_scale)
    setattr(cls, 'inter_scale', inter_scale)
    setattr(cls, 'subsize_count', subsize_count)
    setattr(cls, 'subseries_count', subseries_count)
    setattr(cls, 'plot', plot)
    
    return cls

@bluebelt.core.decorators.class_methods
@resolution_methods
class Resample():
    """
    Resample as series and apply a specific function.
        arguments
        series: pandas.Series
        rule: str
            the resampling rule
        any pandas.Series.resample argunment

        Apply one of the following functions:
            .sum()
            .mean()
            .min()
            .max()
            .std()
            .value_range()
            .count()
            .subsize_count()
            .subseries_count()

        e.g. series.blue.data.resample(rule="1W").sum()
    """
    
    def __init__(self, series, rule="1W", **kwargs):

        check_kwargs(locals())

        # fetch resample kwargs
        resample_kwargs = {
            'rule': rule,
            'axis': kwargs.pop('axis', 0),
            'closed': kwargs.pop('closed', None),
            'label': kwargs.pop('label', None),
            'convention': kwargs.pop('convention', 'start'),
            'kind': kwargs.pop('kind' ,None),
            'loffset': kwargs.pop('loffset', None),
            'base': kwargs.pop('base', None),
            'on': kwargs.pop('on', None),
            'level': kwargs.pop('level', None),
            'origin': kwargs.pop('origin', 'start_day'),
            'offset': kwargs.pop('offset', None),
        }

        self.series = series
        self.rule = rule
        self.func = ''
        self.nrows = self.series.size
        self.resample_kwargs = resample_kwargs
        self.kwargs = kwargs
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.result = self.series.resample(**self.resample_kwargs)

    def __str__(self):
        return ""
    
    def __repr__(self):
        return self.result.__repr__()

@bluebelt.core.decorators.class_methods
@resolution_methods
class GroupByDatetimeIndex():
    """
    Group a series by DateTime index and apply a specific function.
        arguments
        series: pandas.Series
        rule: str
            a string with date-time keywords that can be parsed to group the index
            keywords:
                weekday_name -> %a  # abbreviated weekday name
                week_day -> %u      # weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
                weekday -> %u       # weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
                iso_week -> %V      # The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week
                isoweek -> %V       # The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week
                monthname -> %b     # abbreviated month name
                month_name -> %b    # abbreviated month name
                monthday -> %d      # day of the month (01 to 31)
                month_day -> %d     # day of the month (01 to 31)
                isoyear -> %G       # 4-digit year corresponding to the ISO week number (see %V).
                iso_year -> %G      # 4-digit year corresponding to the ISO week number (see %V).
                yearday -> %j       # day of the year (001 to 366)
                year_day -> %j      # day of the year (001 to 366)
                year -> %Y          # year including the century
                month -> %m         # month (01 to 12)
                week -> %W          # week number of the current year, starting with the first Monday as the first day of the first week
                day -> %d           # day of the month (01 to 31)
                hour -> %H          # hour, using a 24-hour clock (00 to 23)
                minute -> %M        # minute
                second -> %S        # second
                time -> %T          # current time, equal to %H:%M:%S
            
            default value "iso_year-iso_week"

            e.g. "iso_year-Wiso_week" will parse to "%G-W%V" which will print "2021-W01" for the first week of 2021

        Apply one of the following functions:
            .sum()
            .mean()
            .min()
            .max()
            .std()
            .value_range()
            .count()
            .subsize_count()
            .subseries_count()

        e.g. series.blue.data.group_index(rule="iso_year-iso_week").sum()
        
    """
    
    def __init__(self, series, rule="iso_year-iso_week", **kwargs):

        self.series = series
        self.rule = rule
        self.nrows = self.series.size
        self.func = ''
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.result = self.series.groupby(self.series.index.strftime(_strf(self.rule)))

    def __str__(self):
        return ""
    
    def __repr__(self):
        return self.result.__repr__()

def _subsize_count(series, count=3, size=1):
    series = pd.Series(series)/size
    result = series.sum()*count
    for i in range(count, 0, -1):
        result = min(result, math.floor(series.nsmallest(len(series) - count + i).sum() / i))
    return result

def _subseries_count(series, subseries=None, **kwargs):
    series = pd.Series(series)
    subseries = pd.Series(subseries)
    result=series.sum()*subseries.sum()
    for i in range(len(subseries), 0, -1):
        result = min(result, math.floor(series.nsmallest(len(series) - len(subseries) + i).sum() / subseries.nsmallest(i).sum()))
    return result

def _strf(string):
    strf_dict = {'weekday_name': '%a', # abbreviated weekday name
                'week_day': '%u', # weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
                'weekday': '%u', # weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
                'iso_week': '%V', # The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week
                'isoweek': '%V', # The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week
                'monthname': '%b', # abbreviated month name
                'month_name': '%b', # abbreviated month name
                'monthday': '%d', # day of the month (01 to 31)
                'month_day': '%d', # day of the month (01 to 31)
                'isoyear': '%G', # 4-digit year corresponding to the ISO week number (see %V).
                'iso_year': '%G', # 4-digit year corresponding to the ISO week number (see %V).
                'yearday': '%j', # day of the year (001 to 366)
                'year_day': '%j', # day of the year (001 to 366)
                'year': '%Y', # year including the century
                'month': '%m', # month (01 to 12)
                'week': '%W', # week number of the current year, starting with the first Monday as the first day of the first week
                'day': '%d', # day of the month (01 to 31)
                'hour': '%H', # hour, using a 24-hour clock (00 to 23)
                'minute': '%M', # minute
                'second': '%S', # second
                'time': '%T', # current time, equal to %H:%M:%S
                }
    for key, value in strf_dict.items():
        string = string.replace(key, value)
    
    return string

