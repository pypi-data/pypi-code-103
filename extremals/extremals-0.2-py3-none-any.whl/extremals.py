"""
Examples in this documentation assume you run

.. code-block:: python

    import pandas as pd
    import extremals as xt

Let's fix also an example dataframe

.. _data:

.. code-block:: python

    data = pd.DataFrame( 
    {'col1' : [3, 100, 1, -3, None, 9, 22, 8, 9, 0],  
     'col2' : [100, 200, -123, None, 7, -34.5, 95, 3, 12, -567], 
     'col3' : [0, 74, -13.4, 44, 21, 3, -4, None, None, 21]},
     index  = list('abcdefghil')
     )

    # data is the dataframe
        col1   col2  col3
    a    3.0  100.0   0.0
    b  100.0  200.0  74.0
    c    1.0 -123.0 -13.4
    d   -3.0    NaN  44.0
    e    NaN    7.0  21.0
    f    9.0  -34.5   3.0
    g   22.0   95.0  -4.0
    h    8.0    3.0   NaN
    i    9.0   12.0   NaN
    l    0.0 -567.0  21.0
"""

import pandas as pd
import numpy as np
import math


def RWD(value,mean,unstd):
    if unstd == 0:
        ## value = mean
        
        if type(value) in [pd.Series, pd.DataFrame]:
            res = value.copy()
            res[pd.isna(res) == False ] = 0 # set all non null elements to 0
            return res
        
        if pd.isna(value): return value
        return 0
        
        
    
    if np.isinf(mean):
        return value # can't compute the normalization
    return (value-mean)/unstd

def TWD(values, means, unstds):
    
    result = sum([ 
                abs(RWD(values[i],means[i],unstds[i])) 
                for i in range(len(values))
                if not pd.isna(values[i])
               ])
    if result == 0 and all([pd.isna(x) for x in values]): result = np.nan
        
    return result
    
def Normalize(obj, dropna = True):
    if type(obj) == pd.Series:
        std = obj.std(ddof = 0)
        true_l = len(obj) - obj.isna().sum()
        un_std = std*math.sqrt(true_l)
        new_series = RWD(obj, obj.mean(), un_std)
        if dropna: new_series.dropna(inplace = True)
        return new_series
    elif type(obj) == pd.DataFrame:
        z, obj = FilterDatakeys(obj)
        obj = obj.copy()
        for x in obj.columns:
            obj[x] = Normalize(obj[x], False)
        return obj

def FilterDatakeys(data, keys = None, exclude = None):
    if exclude is None: exclude = []
    if keys is None: keys = data.columns
    try: return [[k for k in keys if (not k in exclude) and (data[k].dtype in Test.numtype_list) ], data]
    except AttributeError:
        data, keys = _drop_multiple_columns(data, keys)
        return [[k for k in keys if (not k in exclude) and (data[k].dtype in Test.numtype_list) ], data]

class Test:
    numtype_list = ['int', 'float','bool']
    """
    Numeric data types used
    """

    
    def __init__(self, keys = None, function = None, args = None, normalized = False, name = None):
        self.keys = keys
        self.function = function
        self.args = args if args else []
        self.normalized = normalized
        self.name = name

    def GetArgs(self,data):
        pass
    
    def GetValue(self, arr):
        arr.extend(self.args)
        return self.function(arr)
    
    def Apply(self, data, sort = True):
       
        self.keys, data = FilterDatakeys(data, keys = self.keys)
        if self.keys == []: return pd.Series(dtype='float64')
        self.GetArgs(data)
    
        d=data[self.keys]
        s = pd.Series(index = d.index, dtype='float64')
        s.name = self.name

        for x in s.index:

            args = list(d.loc[x].values)  
            value = self.GetValue(args)
            
            if pd.isna(value): s.drop(x, inplace = True)
            else: s[x] = value

        if sort: s.sort_values(inplace=True)
        if self.normalized: s = Normalize(s, dropna = False)

        return s

class TWDTest(Test):
    
    def __init__(self, keys = None, name = 'TWD'):
        super().__init__(name = name, keys = keys, function = TWD, normalized = False)
        self.means = []
        self.stds = []
    
    def GetArgs(self, data):
        self.means = list(data[self.keys].mean())
        for k in self.keys:
            series = data[k]
            std = series.std(ddof = 0)
            true_l = len(series) - series.isna().sum()
            self.stds.append(std*math.sqrt(true_l))
        
    def GetValue(self,arr):
        return self.function(arr,self.means,self.stds)
    
    def Apply(self, data, sort = True):
        return super().Apply(data = data, sort = sort)
    
class ColTest(Test):
    def __init__(self, key, normalized = False, name = None):
        
        super().__init__(keys = [key], function = lambda x : x[0], normalized = normalized, name = name)
        if name is None: self.name = key

class ColDiffTest(Test):
    def __init__(self, key1, key2, normalized = False, name = None):
        
        super().__init__(keys = [key1, key2], function = lambda x : x[1] - x[0], normalized = normalized, name = name)
        if name is None:
            self.name = '(%s - %s)' %(str(key2),str(key1))

def _find_bound(low, high, l, steps = 1):
    if low < 0 or high < 0:
        low = l
        high = 0
    
    if low < 1: low = int(l*low)
    if high < 1: high = int(l*high)
    if low + high >= l:
        low = l
        high = 0
    
    return [int(low/steps),int(high/steps)]
    

def OutOfBound(obj, low = 0, high = 0, key = None, bound = None):
   
    bound = bound if bound else []
    if type(obj) == pd.Series:
        sel = 0
        series = obj.dropna()
    else:
        sel = 1
        z, obj= FilterDatakeys(obj)
        series = obj[key].dropna()
    
    
    l = len(series)
    
    if l == 0: return [pd.Series(dtype='float64'), pd.DataFrame(dtype='float64')][sel]
    
    try : low, high = bound
    except ValueError: pass
    
    low, high = _find_bound(low, high, l)
    
    high = max(l - high, 0)
    
    series.sort_values(inplace = True)
    indexes = list(series.index)
    out = indexes[:low]+indexes[high:]
   
    if sel == 0: return series.loc[out]
    return obj.loc[out].sort_values(by = key)


def GetColTests(data, keys = None, exclude = None, normalized = False):
    keys, data = FilterDatakeys(data, keys, exclude)
    return [ColTest(k, normalized = normalized) for k in keys]

def GetDiffTests(data, keys = None, exclude = None, normalized = False):
    keys, data = FilterDatakeys(data, keys, exclude)
    l=len(keys)
    return [ColDiffTest(keys[i], keys[j], normalized = normalized) 
                for i in range(l) for j in range(i+1,l)]
    

class Extremals:
    def __init__(self, data, tests = None):
        self.data = data.copy()
        z, self.data = FilterDatakeys(self.data)
        self.results = None
        self.tests = tests if tests else []
    
    def SetColTests(self, keys = None, exclude = None, normalized = False):
        self.tests = GetColTests(self.data, keys = keys, exclude = exclude, normalized = normalized)
        
    def SetDiffTests(self, keys = None, exclude = None, normalized = False):
        self.tests = GetDiffTests(self.data, keys = keys, exclude = exclude, normalized = normalized)
    
    def Run(self, twd = True):
        self.results = pd.DataFrame(dtype='float64')
        for test in self.tests:
            s = test.Apply(self.data)
            while s.name in self.results.columns:
                s.name = '%s+' % s.name
            self.results = pd.concat([self.results,s], axis = 1)
        if twd:
            series = TWDExtremals(self.results)
            while series.name in self.results.columns:
                series.name = '%s+' % series.name
            
            self.results = pd.concat([self.results, series], axis = 1)
            self.results.sort_values(by=series.name, inplace = True)
        return self.results
    
    def NormalizeTests(self, value = True):
        for test in self.tests: test.normalized = value
        
    def OutOfBound(self,low = 0, high = 0, key = 'TWD', bound = None):
        return OutOfBound(self.results, low = low, high = high, key = key, bound = bound)

class ExtremalsCol(Extremals):
    def __init__(self, data, keys = None, exclude = None, normalized = False):
        super().__init__(data, tests = [])
        self.SetColTests(keys = keys, exclude = exclude, normalized = normalized)

class ExtremalsDiff(Extremals):
    def __init__(self, data, keys = None, exclude = None, normalized = False):
        super().__init__(data, tests = [])
        self.SetDiffTests(keys = keys, exclude = exclude, normalized = normalized)


def TWDExtremals(data, bound = None, keys = None, exclude = None, name = 'TWD'):
    bound = bound if bound else [-1,-1]
    if type(data) == pd.Series:
        data = pd.DataFrame({ 'col' : data }, dtype = 'float64')
        keys = ['col']
    else:
        keys, data = FilterDatakeys(data, keys, exclude)
   
    test = TWDTest(keys = keys, name = name)
    series = test.Apply(data)
    return OutOfBound(series, bound = bound)

def PurgeTWD(data, high, steps = 1, keys = None, exclude = None, verbose = False):
    if type(data) == pd.Series:
        data = pd.DataFrame({ 'col' : data }, dtype = 'float64')
        keys = ['col']
        
    if high <= 0:
        raise ValueError('high should be a positive number, %d passed instead' % high)
    if high < 1:
        high = high*len(data.index)
    low = 0
    if steps > high:
        steps = high
        
    keys, data = FilterDatakeys(data, keys = keys, exclude = exclude)
    new_data = data.copy()
    
    purged_indexes = []
    counter = 1
    while steps > 0 and not new_data.empty:
        if verbose:
            print('Step %d' % counter)
            counter+=1
        twd = TWDExtremals(new_data, keys = keys)
        step_low, step_high = _find_bound(low, high, len(twd), steps)
       
        twd = OutOfBound(twd, step_low, step_high)
        new_data.drop(index = twd.index, inplace = True)
        purged_indexes.extend(twd.index[::-1])
        if verbose:
            howmany = step_low + step_high
            if howmany == 1: info ='1 index'
            else: info='%d indexes' %howmany
            print('%s removed' %info)
            
        low-= step_low
        high-= step_high
        steps -= 1
    purged_data = data.loc[purged_indexes].copy()
    if type(data) == pd.Series:
        purged_data = purged_data['col']
        new_data = new_data['col']
       
    return [purged_data, new_data]

def _drop_multiple_columns(data, keys = []):
    duplicated = ~data.columns.duplicated()
    if all(duplicated): return data, keys
    keys = list(set(keys))
    data = data.loc[:, ~data.columns.duplicated()]
    return data, keys
    
def AddTests(data, tests, normalized = False):
    if not type(tests) == list:
        tests = [tests]
    if normalized: data=Normalize(data)
    results = Extremals(data, tests = tests).Run(twd = False)
    return pd.concat([data, results], axis = 1)
    
def AddTWDTest(data, keys = None, exclude = None, normalized = False):
    keys, data = FilterDatakeys(data, keys, exclude)

    new_data = AddTests(data, tests = TWDTest(keys = keys), normalized = normalized)
    twd_key = new_data.columns[-1]
    new_data.sort_values(by = twd_key, inplace = True)
    return new_data
    
