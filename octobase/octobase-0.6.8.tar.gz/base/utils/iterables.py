#!/opt/local/bin/python
# Copyright 2014, Octoboxy LLC.  All Rights Reserved.
''' Functions for iterable data types. '''

import inspect


def Flatten(*lst):
  ''' Flattens lists of lists of lists as you would expect. '''
  # A naive implementation might be something like:
  #     return sum( ([x] if not hasattr(x, '__iter__') else Flatten(x) for x in lst), [] )
  # But we have this annoying thing called FileType that is iterable, includes itself in
  # its own iteration, and fits really well inside lists of things people want to Flatten().
  seen              = []
  results           = []

  def IsIterable(x):
    return hasattr(x, '__iter__') and not isinstance(x, str)

  def Accumulate(x):
    if isinstance(x, tuple) or isinstance(x, list):
      for y in x:
        Accumulate(y)
    elif isinstance(x, str) or not hasattr(x, '__iter__'):
      results.append(x)
    else:
      # An iterable that is not a tuple or list, be careful, may become recursive
      if not x in seen:
        seen.append(x)
        for y in x:
          if y == x:
            results.append(x)
          else:
            Accumulate(y)

  for item in lst:
    Accumulate(item)

  return results


def CountUnique(l):
  ''' Given an iterable we return a dict of each unique item mapped to a count of its occurrences. '''
  r             = {}
  for k in l:
    r[k]        = r.get(k, 0) + 1
  return r


def ReverseDict(d):
  ''' Given { key: value } we return { value: [key] } '''
  r             = {}
  for k in d:
    r.setdefault(d[k], []).append(k)
  return r


def GetAttrs(thing, capitals=True, lowers=True, hidden=False):
  ''' Returns a dictionary of every attribute we can read off the thing. '''
  members           = {x:y for x,y in inspect.getmembers(thing)}
  if not hidden:
    members         = {x:y for x,y in members.items() if x[0] != '_'}
  if not capitals:
    members         = {x:y for x,y in members.items() if not x[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
  if not lowers:
    members         = {x:y for x,y in members.items() if not x[0] in 'abcdefghijklmnopqrstuvwxyz'}
  return members


def SetAttrs(thing, **kwargs):
  ''' Calls setattr() on thing for each key-value pair in kwargs. '''
  for key, value in kwargs.items():
    setattr(thing, key, value)
