#!/usr/bin/env python3

import base
from base import rightdown
import itertools


###
## Helper Functions
#


def MakeLeftRightString(left, right, width=40, stepping=40):
  ''' Joins two strings with an arrow; mostly here to hold our defaults for width and stepping. '''
  return base.utils.PadString(left, width, stepping=stepping) + '  -->  ' + right



###
## TestContexts
#


class OptionsContext(base.TestContext):
  ''' A TestContext that sets up RightDownOptions for a test case. '''

  def __init__(self, **kwargs):
    self.kwargs     = kwargs

  def SetUp(self):
    return rightdown.RightDownOptions(**self.kwargs).__enter__()

  def GoInteractive(self, **kwargs):
    super().GoInteractive(rightdown=rightdown, **kwargs)



class ReferenceDocumentContext(OptionsContext):
  ''' A TestContext that loads our reference document and corresponding result set for us. '''

  def __init__(self, expect=None, **kwargs):
    super().__init__(**kwargs)
    self.reference  = ''
    self.expected   = []
    self.expect     = expect


  def SetUp(self, expect=None):
    with open('base/rightdown/data/reference.rd', 'rt') as file:
      self.reference  = file.read().rstrip() + '\n'
    if self.expect:
      with open('base/rightdown/data/reference-{}.txt'.format(self.expect), 'rt') as file:
        self.expected = file.read().rstrip().split('\n')
    return super().SetUp()



###
## a parent TestCase for a few of our actual TestCases
#


class StringListComparisonTestCase(base.TestCase):
  ''' Common code for our tests that want to compare results against lines in a file. '''

  def Explain(self, actual):
    ''' Given two lists of strings, compares them and spews results to console on mismatch. '''
    expected        = self.context.expected or []
    errors          = 0
    for exp, act in itertools.zip_longest(expected, actual):
      if exp != act:
        errors      = errors + 1

    self.LogResult(not errors, '{} line{}'.format(len(actual), len(actual) != 1 and 's' or ''))

    if errors:
      minwidth      = 16
      maxwidth      = rightdown.RightDownOptions.truncate_width
      width         = min(maxwidth, max(base.utils.Flatten(minwidth, [len(x) for x in expected], [len(x) for x in actual])))
      dashinglie    = '-'*width
      lines         = [
          '+-{dashinglie}-+----+-{dashinglie}-+'.format(dashinglie=dashinglie),
          '| {:^{width}s} | == | {:^{width}s} |'.format('Expected', 'Actual', width=width),
          '+-{dashinglie}:+:--:+:{dashinglie}-+'.format(dashinglie=dashinglie),
      ]
      for exp, act in itertools.zip_longest(expected, actual, fillvalue='(None)'):
        ex          = (len(exp) > maxwidth) and (exp[:maxwidth-1] + '…') or exp
        ac          = (len(act) > maxwidth) and (act[:maxwidth-1] + '…') or act
        lines.append('| {:{width}s} | {} | {:{width}s} |'.format(ex, exp == act and '  ' or '!=', ac, width=width))
      lines.append('+-{dashinglie}-+----+-{dashinglie}-+'.format(dashinglie=dashinglie))
      base.utils.Log('DETAIL', '\n  ' + '\n  '.join(lines))

    return True   # LogResult() already called

base.registry.UnRegister(StringListComparisonTestCase)



###
## TestCases
#


class TestTagPatterns(base.TestCase):
  ''' Tests that our TagPattern trees can match well-known sequences of LineTokenTypes. '''

  TEST_CONTEXT      = OptionsContext(contextual_breaks=False)

  def Run(self):
    ##
    #### Prefix any test case string with '@' to turn on deep debugging!
    ##
    self.DoTest(rightdown.BLOCK_HARD_BREAK, {
        '':                                                                       rightdown.RESULT_BROKEN,
        'break0':                                                                 rightdown.RESULT_HALT,
        'break0,empty':                                                           rightdown.RESULT_FULL,
        'break0,break1':                                                          rightdown.RESULT_OVERFULL,
        'break1':                                                                 rightdown.RESULT_BROKEN,
    })
    self.DoTest(rightdown.BLOCK_MULTI_FIELD, {
        '':                                                                       rightdown.RESULT_BROKEN,
        'paragraph':                                                              rightdown.RESULT_HUNGRY,
        'paragraph,empty':                                                        rightdown.RESULT_BROKEN,
        'paragraph,value':                                                        rightdown.RESULT_OKAY,
        'paragraph,value,value':                                                  rightdown.RESULT_OKAY,
        'paragraph,value,slug':                                                   rightdown.RESULT_OVERFULL,
    })
    self.DoTest(rightdown.BLOCK_PSEUDO_YAML, {
        'break0':                                                                 rightdown.RESULT_HUNGRY,
        'break1':                                                                 rightdown.RESULT_BROKEN,
        'break0,break1':                                                          rightdown.RESULT_HALT,
        'break0,field':                                                           rightdown.RESULT_HUNGRY,
        'break0,field,break1':                                                    rightdown.RESULT_HALT,
        'break0,field,break1,slug':                                               rightdown.RESULT_OVERFULL,
        'break0,field,field,indent,indent,ndent,slug,value,field,break1':         rightdown.RESULT_HALT,
        'break0,field,field,indent,indent,ndent,slug,indent,field,break1':        rightdown.RESULT_BROKEN,
    })

  def DoTest(self, blocktype, cases):
    pattern         = rightdown.BlockTokenTypes.Definition(blocktype).pattern
    for case, expected in cases.items():
      debug, tokenlist  = self.MakeTokenList(case)
      _, result     = pattern._Consume(tokenlist, debug=debug)
      expected_str  = rightdown.Results.Name(expected)
      result_str    = rightdown.Results.Name(result)
      passed        = result == expected
      logleft       = '{:s}({})'.format(rightdown.BlockTokenTypes.Name(blocktype), case)
      if passed:
        logright    = expected_str
      else:
        logright    = 'expected={} actual={}'.format(expected_str, result_str)
      self.LogResult(passed, MakeLeftRightString(logleft, logright))

  def MakeTokenList(self, case):
    ''' Breaks down a comma-delimited list of LineTokenTypes; returns (debug, [LineToken]). '''
    stripped        = case.lstrip('@')
    debug           = len(case) - len(stripped)
    tokenlist       = []
    for linetype in stripped.split(','):
      linetoken     = rightdown.LineToken(type=linetype)
      linetoken.data  = linetype or ''
      tokenlist.append(linetoken)
    return debug, tokenlist



class TestInlineProcessor(base.TestCase):
  CASES             = (
      ('paragraph with *two emphasized* words',
          '"paragraph" _ "with" _ star1["two" _ "emphasized"] _ "words"'),
      ('_underlined *italics* underlined_',
          'under["underlined" _ star1["italics"] _ "underlined"]'),
      ('abcdefg ((hijk)) lmnop',
          '"abcdefg" _ paren2["hijk"] _ "lmnop"'),
      ('abcdefg((hijk))lmnop',
          '"abcdefg(" paren["hijk"] ")lmnop"'),
      ('_*underitalics*_',
          'under[star1["underitalics"]]'),
      ('*emphasized once *twice and *three times* back to twice* back to once*',
          'star1["emphasized" _ "once" _ star1["twice" _ "and" _ star1["three" _ "times"] _ "back" _ "to" _ "twice"] _ "back" _ "to" _ "once"]'),
  )

  def Run(self):
    ''' Runs a few known hard strings through the inline processor. '''

    for case, expected in self.CASES:
      stripped      = case.lstrip('@')
      debug         = len(case) - len(stripped)
      case          = stripped

      node          = rightdown.Processor.ProcessInline(case, debug=debug)
      actual        = node.DebugString()

      passed        = actual == expected
      self.LogResult(passed, MakeLeftRightString(case, actual))



class TestDocumentationExample(base.TestCase):
  ''' It is extremely embarassing if our simplest possible examples in the docs
      raises an exception, no matter whether all the more complex test cases pass
      or not.
  '''

  def Run(self):
    text            = '***every markdown file is _already_ a rightdown file***'
    expected        = '<section><p><b><i>every markdown file is <u>already</u> a rightdown file</i></b></p></section>'

    html0           = base.RightDownData.Process(text).Html()
    with base.RightDownOptions(html_add_head=False):
      html1         = base.RightDownData.Process(text).Html()

    passed          = html1 == expected
    self.LogResult(passed, MakeLeftRightString(expected, html1))

    if passed:
      passed        = html1 in html0 and html1 != html0
      self.LogResult(passed, html0)



class TestLineTokenizer(StringListComparisonTestCase):
  ''' Tests that running reference.rd through LineTokenizer yields the expected LineToken sequence. '''

  TEST_CONTEXT      = ReferenceDocumentContext(expect='lines')

  def Run(self):
    linetokens      = base.rightdown.LineTokenizer().Tokenize(self.context.reference)
    return [(x.type or 'paragraph') for x in linetokens]



class TestProcessingToBlocks(StringListComparisonTestCase):
  ''' Tests running reference.rd through the first half of our our processor. '''

  TEST_CONTEXT      = ReferenceDocumentContext(expect='blocks')

  def Run(self):
    data            = base.RightDownData.Process(self.context.reference)
    return data.DebugString(rich=self.runner.dumpmode).split('\n')



class TestProcessingToNodes(StringListComparisonTestCase):
  ''' Tests running reference.rd through the both halves of our our processor. '''

  TEST_CONTEXT      = ReferenceDocumentContext(expect='nodes')

  def Run(self):
    with rightdown.RightDownOptions(defer_inline_processing=False):
      data          = base.RightDownData.Process(self.context.reference)
    return data.DebugString(rich=self.runner.dumpmode).split('\n')



class TestRenderText(StringListComparisonTestCase):
  ''' Tests that processing then re-emitting a rightdown file yields the same file. '''

  TEST_CONTEXT      = ReferenceDocumentContext()

  def Run(self):
    self.context.expected = self.context.reference.split('\n')
    return base.RightDownData.Process(self.context.reference).Text().split('\n')



class TestRenderHtml(StringListComparisonTestCase):
  ''' Tests running reference.rd through the both halves of our our processor. '''

  TEST_CONTEXT      = ReferenceDocumentContext(expect='html')

  def Run(self):
    foo             = base.RightDownData.Process(self.context.reference).Html()
    return foo.split('\n')
