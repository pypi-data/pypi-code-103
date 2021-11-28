#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import argparse
import base
import fnmatch
import itertools
import logging
import math

from . import registry


class TestCase(metaclass=registry.Registry.AutoRegister, skip=1):
  ''' One single test case, though you may log as many test results as you want within it. '''

  TEST_CONTEXT      = None

  def __init__(self, runner=None, context=None):
    self.runner     = runner
    self.context    = context
    self.results    = 0
    self.fails      = 0

  @property
  def name(self):
    return base.utils.ObjectName(self)

  def Run(self):
    ''' Do what processing you need to, return the results, or at least something not False. '''
    return True

  def Explain(self, results):
    ''' Return the results of Run() and return a boolean for whether we passed or not. '''
    return results != False

  def LogResult(self, passed, message, namewidth=25):
    ''' Accumulates a new result for the currently running test. '''
    self.results    = self.results + 1
    if not passed:
      self.fails    = self.fails + 1
    name            = base.utils.PadString(self.name + ':', namewidth)
    message         = message and ' '.join((name, str(message))) or name
    base.utils.Log(passed and ' PASS' or '!FAIL', message)



class TestContext(metaclass=registry.Registry.AutoRegister, skip=1):
  ''' An environment that your test case needs to run within, can be shared between cases.
      Each test case can access the context it's in through a self.context property.
  '''

  def __init__(self):
    self.next       = None

  def __enter__(self):
    self.next       = self.SetUp()
    return self.next or self

  def __exit__(self, _1, exception, _2):
    self.CleanUp()
    if self.next:
      self.next.__exit__(_1, exception, _2)
    elif exception:
      raise

  def SetUp(self):
    ''' Load whatever resources your test case needs.  You may return a context manager object if desired. '''

  def CleanUp(self):
    ''' Release any resources that need manual cleanup. '''

  def GoInteractive(self, **kwargs):
    ''' Opens an interactive console within the local scope. '''
    base.utils.GoInteractive(**kwargs)



class TestModuleContext(TestContext, skip=1):
  ''' If a TestModuleContext subclass exists in the same module as any of your test cases, it will
      be used to wrap all the test cases in that module.
  '''



class TestRunner:
  ''' Engine that calls TestCases for you. '''

  def __init__(self, **kwargs):
    self.cases      = 0
    self.results    = 0
    self.fails      = 0
    self.only       = None
    self.skip       = None
    self.dumpmode   = False
    base.utils.SetAttrs(self, **kwargs)

  def RunFromCommandLine(self):
    COMMANDS        = {
        'list':           self.ListTests,
        'interact':       self.InteractWithContext,
        'dump':           self.DumpTestResults,
    }
    COMMANDS_NEED_ONLY  = ('interact', 'dump')

    parser          = argparse.ArgumentParser()

    parser.add_argument('command', nargs='*',
        help='do something special besides just running a test')

    parser.add_argument('--only', metavar='LIST',
        help='comma-delimited list of tests to run; wildcards are allowed')
    parser.add_argument('--skip', metavar='LIST',
        help='comma-delimited list of tests to not run; wildcards are allowed')

    args            = parser.parse_args()
    self.only       = ((self.only or []) + (args.only and args.only.split(',') or [])) or None
    self.skip       = ((self.skip or []) + (args.skip and args.skip.split(',') or [])) or None

    if args.command:
      for command, handler in COMMANDS.items():
        if command == args.command[0]:
          if command in COMMANDS_NEED_ONLY and len(args.command) < 2:
            base.utils.Log('ERROR', 'Command "{}" needs the name of a test case to operate on'.format(command), level=logging.ERROR)
            return
          self.only = [args.command[1]]
          return handler()
      base.utils.Log('ERROR', 'Unknown command: ' + str(args.command), level=logging.ERROR)
      return

    self.RunAll()

  def RunAll(self):
    ''' Runs every registered TestCase within the proper TestContexts. '''
    self._RunInContext(self._GetTestCasesByContext())

    if self.cases:
      status        = self.fails and 'FAILED' or 'PASSED'
    elif not self.results and not self.fails:
      base.utils.Log('EMPTY', 'No test cases were run.')
      return
    else:
      status        = 'CONFUSED'

    base.utils.Log(status, '{} TestCase{} run, {} result{} logged, {} failure{}'.format(
        self.cases,   self.cases    != 1 and 's' or '',
        self.results, self.results  != 1 and 's' or '',
        self.fails,   self.fails    != 1 and 's' or ''
    ))


  ###
  ## Special commands besides just running tests
  #


  def ListTests(self):
    ''' Lists to console all available TestCases and the TestContexts they run within. '''
    for modcon, subthings in self._GetTestCasesByContext().items():
      print('  ' + (modcon and base.utils.ObjectName(modcon) or 'No Module Context'))
      for context, caselist in subthings.items():
        print('    ' + (context and base.utils.ObjectName(context) or 'No Test Context'))
        for case in caselist:
          print('      ' + base.utils.ObjectName(case))

  def DumpTestResults(self):
    ''' Prints the results of running the test to the console. '''
    self.dumpmode   = True
    self.RunAll()

  def InteractWithContext(self):
    ''' Opens an interactive python shell inside the specified TestContext. '''
    for modcon, subthings in self._GetTestCasesByContext().items():
      for context in subthings:
        if not context:
          base.utils.Log('TEST', 'No context to run in!')
          return
        if isinstance(context, type):
          context   = context()
        if modcon:
          if isinstance(modcon, type):
            modcon  = modcon()
          with modcon:
            with context:
              context.GoInteractive()
        else:
          with context:
            context.GoInteractive()
        return


  ###
  ## Mechanics
  #


  @staticmethod
  def _MatchGlobList(thing, globlist):
    charm           = base.utils.ObjectName(thing)
    strange         = base.utils.ClassName(thing)
    if charm in globlist or thing in globlist:
      return True
    for pattern in globlist:
      if fnmatch.fnmatch(charm, pattern):
        return True
      if fnmatch.fnmatch(strange, pattern):
        return True

  def _GetTestCasesByContext(self):
    ''' Returns { module context: { test context: [ test case, ... ] } } '''
    def first(iter):
      if iter:
        for x in iter:
          return x

    def GetModuleContext(testcase):
      if testcase:
        for modcon in base.registry.GetAll(TestModuleContext):
          if modcon.__module__ == testcase.__module__:
            return modcon

    by_module       = {}
    for testcase in base.registry.GetAll(TestCase):
      if not self.only or self._MatchGlobList(testcase, self.only):
        if not self.skip or not self._MatchGlobList(testcase, self.skip):
          by_module.setdefault(testcase.__module__, {}).setdefault(testcase.TEST_CONTEXT, []).append(testcase)

    return { GetModuleContext(first(first(x.values()))): x for x in by_module.values() }

  def _RunInContext(self, thing, lastcontext=None):
    if isinstance(thing, dict):
      for context, subthing in thing.items():
        if context:
          if isinstance(context, type):
            context = context()
          with context:
            self._RunInContext(subthing, lastcontext=context)
        else:
          self._RunInContext(subthing)
    else:
      for testcase in thing:
        self._RunOne(testcase, lastcontext)

  def _RunOne(self, testclass, context=None):
    ''' Runs one single TestCase subclass, increments our counters for the result. '''
    self.cases      = self.cases + 1
    success         = False
    testcase        = None

    try:
      testcase      = testclass(runner=self, context=context)
      base.utils.Log('TEST', 'Running: ' + testcase.name)
      results       = testcase.Run()
      if self.dumpmode:
        self._Dump(results)
        return
      success       = testcase.Explain(results)
    except Exception as e:
      base.utils.Log('TEST', 'Uncaught Exception: ' + str(e), level=logging.WARN)
      self.fails    = self.fails + 1
      raise

    if not success:
      self.fails    = self.fails + 1
    self.results    = self.results + testcase.results
    self.fails      = self.fails + testcase.fails
    if testcase.fails:
      success       = False

    if success and isinstance(success, str):
      base.utils.Log('PASS', testcase.name + ': ' + success)
    else:
      base.utils.Log(success and 'PASS' or 'FAIL', testcase.name)

  def _Dump(self, results):
    if not results:
      print('')
    elif isinstance(results, list):
      print('\n'.join([str(x) for x in results]))
    else:
      print(str(results))






