# AUTOGENERATED! DO NOT EDIT! File to edit: 03_Tracking.ipynb (unless otherwise specified).

__all__ = ['create', 'append', 'delete', 'print_keys', 'get_stat', 'get_stats', 'print_best', 'graph_stat',
           'graph_stats']

# Cell
import shelve
import matplotlib.pyplot as plt
import os
from fastcore.foundation import *
import numpy as np

# Cell
def create(filename,keys):
  with shelve.open(filename) as d:
    if type(keys) == str: d[keys] = L()
    else:
        for key in keys: d[key] = L()

# Cell
def append(filename,new_dict,key='exp'):
    '''Append a new_dict to list store in key - create db if needed'''
    if not os.path.exists(filename): create(filename,key)
    with shelve.open(filename) as d:
        if key not in list(d.keys()): d[key] = L()
        tmp = d[key]
        tmp.append(new_dict)
        d['exp'] = tmp

# Cell
def delete(filename,exp_num,key='exp'):
    '''delete an item from list stored in key'''
    with shelve.open(filename) as d:
        tmp = d[key]
        if type(exp) == int:
            tmp.pop(exp_num)
        if type(exp) == str:
            for i,e in eumerate(tmp):
              if e['name'] == name: tmp.pop(i)
        d[key] = tmp

# Cell
def print_keys(filename,last_only=True, with_type=False, key='exp'):
    with shelve.open(filename) as d:
        if last_only and not with_type: print(list(d[key][-1].keys()))
        if last_only and with_type: print({k:type(v) for k,v in d['exp'][-1].items()})
        if not last_only and not with_type:
            a = L()
            for o in d['exp']: a = a + L(o.keys())
            a = a.unique()
            print(a)
        if not last_only and with_type:
            a = {}
            for o in d['exp']: a.update({k:type(v) for k,v in o.items()})
            print(a)

# Cell
def get_stat(filename,exp_num,stat,key='exp',display=True):
    '''get a specific stat (ie loss) from key for a given expirament
    Goes well with partial
    '''
    with shelve.open(filename) as d:
      if display: print(f'd[{key}][{exp_num}][{stat}]: {d[key][exp_num][stat]}')
      return (f'd[{key}][{exp_num}][{stat}]',d[key][exp_num][stat])

# Cell
def get_stats(filename,exp_num,stats,key='exp',display=True):
    return [get_stat(filename,exp_num,stat,key,display) for stat in stats]

# Cell
def print_best(filename,stat,best='min', key='exp'):
    with shelve.open(filename) as d: exps = len(d[key])
    if best == 'min':
        out = (np.inf,None)
        for i in range(exps):
          a,b = get_stat(filename,i,stat,display=False)
          if min(b) < out[0]: out = (min(b),i)
    if best == 'max':
        out = (-np.inf,None)
        for i in range(exps):
          a,b = get_stat(filename,i,stat,display=False)
          if max(b) > out[0]: out = (max(b),i)

    print(f'{stat} {best} value = {out[0]} | best idx = {out[1]-exps}')

# Cell
def graph_stat(filename,stat,idxs=[-1,-2,-3], key='exp',name='name',figsize=(12,6)):
    with shelve.open(filename) as d:
        fig,ax = plt.subplots(figsize=figsize)
        for e in L(d[key])[idxs]:
            try:
              vals = e[stat]
              ax.plot(range(len(e[stat])),e[stat],label=e[name])
              ax.legend();ax.set_title(f'{stat}')
            except:
              print(f'Unable to plot {stat} for {e[name]}')

def graph_stats(filename,stats,idxs=[-1,-2,-3],key='exp',name='name',figsize=(12,6)):
    for stat in stats:
        graph_stat(filename,stat,idxs,key,name,figsize)