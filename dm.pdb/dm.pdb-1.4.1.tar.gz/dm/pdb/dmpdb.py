# Copyright (C) 2005-2018 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: dmpdb.py,v 1.9 2018/12/20 13:39:51 dieter Exp $
"""Dieter Maurers PDB extension.

`Pdb`, the Python debugger, has severe limitations (apart from some bugs).
This extension tries to get rid of some of them.

 * setting breakpoints

   Allow *filename* to specify a module as well.

   Allow setting breakpoints from outside via ``do_break``.
   This is useful for debug setups.

 * exception display

   We store the exception in the `Pdb` instance.
   A new command `exception` (abbreviated `e`) calls `print_exception`
   on the stored exception value.


 * `where` command improvements

   - each frame identifies its level (the top frame is at level 0,
     the one below it at level 1, etc...)

   - the current frame is marked as such

   - `where` gets optional arguments *number* and *end*

     *number* controls how many frames are displayed (default: `maxint`),
     *end* at what level the display ends, negative numbers count from
     the bottom (default: `-1`, i.e. the bottom frame).

 * new command `frame level` (abbr: `f`)

   switch to call frame at *level*

   without argument, provide info about current frame

 * allow to customize the display of the `where` command
   and of tracebacks
   e.g. to display additional debugging information as
   provided by Zope (for example).

   This can be done by customizing `getAdditionalFrameInfo`.

Still missing

 * Returning from `debug` occasionally returns to `stop`
   rather than where we entered the recursive debugger.
   This is often nasty (and should be fixed)
"""

from __future__ import print_function

from pdb import Pdb, set_trace, post_mortem, pm
from traceback import format_exception_only
import sys
try: from sys import maxsize as maxint
except ImportError: from sys import maxint
from os.path import splitext

from dm.reuse import rebindFunction

from .proxy import proxy_factory

class _ProxyMixin(object):
  def error(self, *args, **kw):
    unwrapped = self._unwrapped
    unwrapped.exception = sys.exc_info()
    unwrapped.error(*args, **kw)


class _Redirector(object):
  '''auxiliary class to define the 'curframe' descriptor.'''

  def __get__(self, instance, owner):
    if instance is None: return self
    cf = getattr(instance, self.attr, self)
    return self._fetch(instance) if cf is self else cf

  def __set__(self, instance, value):
    if value is None:
      # implement assigning 'None' as making 'curframe' undefined
      if hasattr(instance, self.attr): delattr(instance, self.attr)
      return
    setattr(instance, self.attr, value)

  def __delete__(self, instance):
    delattr(instance, self.attr)

class _CurframeRedirector(_Redirector):
  attr = "_curframe"

  def _fetch(self, instance):
    i = 0
    while True:
      try: cf = sys._getframe(i)
      except: return
      fn = cf.f_globals["__name__"]
      if fn not in ("dm.pdb.dmpdb", "pdb"): return cf
      i += 1

class _Curframe_localsRedirector(_Redirector):
  attr = "_curframe_locals"

  def _fetch(self, instance):
    return instance.curframe.f_locals
    
  
def _callMyClass(*args, **kw):
  callframe = sys._getframe(1)
  self = callframe.f_locals['self']
  return self.__class__(*args, **kw)

class Pdb(Pdb, object):
  '''PDB extension.'''

  curframe = _CurframeRedirector()
  curframe_locals = _Curframe_localsRedirector()

  def print_stack_entry(self, frame_lineno, prompt_prefix=None, frameno=None):
    if prompt_prefix is None:
      if frameno is None: frameno = self.curindex
      prompt_prefix = '\n  [%d] ' % frameno
    super(Pdb, self).print_stack_entry(frame_lineno, prompt_prefix)
    info = self.getAdditionalFrameInfo(frame_lineno)
    if info:
      if hasattr(info, "split"): info = info.split('\n')
      print ('  ' + '\n  '.join(info))

##  # for analysis only
##  def message(self, msg):
##    from traceback import print_stack
##    print("message:\n")
##    print_stack()
##    super(Pdb, self).message(msg)

  def print_stack_trace(self, number=maxint, end=-1):
    if end < 0: end += len(self.stack)
    if end < 0: return
    start = end+1 - number
    if start < 0: start = 0
    try:
      for index in range(start, end+1):
        frame_lineno = self.stack[index]
        self.print_stack_entry(frame_lineno, frameno=index)
    except KeyboardInterrupt: pass

  def do_where(self, arg):
    arg = arg.strip()
    number = maxint; end = -1
    try: 
      if arg:
        args = arg.split()
        number = int(args[0])
        if len(args) > 1: end = int(args[1])
    except ValueError: print ('*** Syntax error', arg); return
    self.print_stack_trace(number, end)
  do_w = do_bt = do_where

  def do_frame(self, arg):
    arg = arg.strip()
    if arg:
      try: arg = int(arg)
      except ValueError: print ('*** Argument must be an integer', arg); return
    else: arg = self.curindex
    if arg < 0: arg += len(self.stack)
    if not (0 <= arg < len(self.stack)):
      print ('*** no such frame')
      return
    elif arg != self.curindex:
      if hasattr(self, "_select_frame"): self._select_frame(arg)
    else: self.print_stack_entry(self.stack[arg])
  do_f = do_frame

  def do_exception(self, arg):
    exc = self.exception
    if exc is None:
      print ('*** no exception information')
      return
    arg = arg.strip()
    number = maxint; end = -1
    if arg:
      args = arg.split()
      try:
        number = int(args[0])
        if len(args) > 1: end = int(args[1])
      except ValueError: print ('*** Arguments must be integers', arg); return
    self.print_exception(exc, number, end)
  do_e = do_exception

  # fix "do_debug"
  do_debug = rebindFunction(Pdb.do_debug,
                            Pdb=_callMyClass,
                            )

  def help_where(self):
    self.help_w()

  def help_w(self):
    print ("""w(here)
Print a stack trace, with the most recent frame at the bottom.
An arrow indicates the "current frame", which determines the
context of most commands.  'bt' is an alias for this command.

It supports optional arguments "number" and "end".
"number" specifies the number of frames to be printed (default: maxint);
"end" specifies the last frame to be printed, a negative value counts
from the end (default: "-1", i.e. the bottom frame).""")

  help_bt = help_w

  def help_frame(self):
    self.help_f()

  def help_f(self):
    print ("""f(rame)
With an argument (an integer), first switch to that frame (a negative value
counts from the end).
In any case, print (then) information about the current frame.""")

  def help_exception(self):
    print ("""e(xception)
Print exception information for the latest exception.
It supports optional arguments "number" and "end".
"number" specifies the number of frames to be printed (default: maxint);
"end" specifies the last frame to be printed, a negative value counts
from the end (default: "-1", i.e. the bottom frame).""")

  help_e = help_exception

  def reset(self):
    super(Pdb, self).reset()
    self.exception = None

  def print_exception(self, exc, number, end):
    # flatten traceback
    ftb = []; tb = exc[2]
    while tb is not None:
      f = tb.tb_frame; lineno = tb.tb_lineno
      ftb.append((f, lineno))
      tb = tb.tb_next
    if end < 0: end += len(ftb)
    if end >= len(ftb): end = len(ftb)-1
    if end >= 0:
      start = end+1 - number
      if start < 0: start = 0
      try:
        for index in range(start, end+1):
          frame_lineno = ftb[index]
          self.print_stack_entry(frame_lineno, frameno=index)
      except KeyboardInterrupt: pass
    print (''.join(format_exception_only(exc[0], exc[1])).rstrip())

  def getAdditionalFrameInfo(self, frame_lineno):
    '''returns additional info, if available.

    If not a false value, this should either be a string or a sequence

    *frame_lineno* is a tuple *(frame, lineno)*.
    '''
    return

  def lookupmodule(self, file_or_module_name):
    '''do what the base function promisses.'''
    try:
      mod = __import__(file_or_module_name, {}, {}, ['__doc__'])
      file_or_module_name = splitext(mod.__file__)[0]
    except ImportError: pass
    return super(Pdb, self).lookupmodule(file_or_module_name)

  def default(self, line):
    return self._call_via_proxy("default", line)

  def _getval(self, arg):
    return self._call_via_proxy("_getval", arg)

  def user_exception(self, frame, exc):
    """This function is called if an exception occurs,
    but only if we are to stop at or just below this level."""
    self.exception = exc
    super(Pdb,self).user_exception(frame, exc)


  def trace_dispatch(self, *args):
    '''ensure we are using the real 'stdout' even if used inside a doctest.'''
    #return super(Pdb, self).trace_dispatch(*args)
    save_stdout = sys.stdout
    sys.stdout = sys.__stdout__
    try: return super(Pdb, self).trace_dispatch(*args)
    finally: sys.stdout = save_stdout

  def _call_via_proxy(self, method, *args, **kw):
    p = proxy_factory(self, _ProxyMixin)
    m = getattr(super(Pdb, self), method).__func__
    return m(p, *args, **kw)

# old "pdb"
if not hasattr(Pdb, "_select_frame"):
  def _select_frame(self, no):
    assert 0 <= no < len(self.stack)
    self.curindex = no
    self.curframe = self.stack[no][0]
    self.curframe_locals = self.curframe.f_locals
    self.print_stack_entry(self.stack[no])
    self.lineno = None

  Pdb._select_frame = _select_frame
    
    
# Python stupidly monkey patches 'set_trace' when it is inside a doctest
# Therefore, we must use code duplication :-(
#set_trace = rebindFunction(set_trace, Pdb=Pdb)
def set_trace(): Pdb().set_trace(sys._getframe().f_back)
post_mortem = rebindFunction(post_mortem, Pdb=Pdb)
pm = rebindFunction(pm, post_mortem=post_mortem)
