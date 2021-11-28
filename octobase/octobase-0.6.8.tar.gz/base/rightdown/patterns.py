#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown
import re


_once_initialized = False

def InitializeAllPatterns():
  ''' Compiles all block patterns.  Idempotent. '''
  global _once_initialized
  if _once_initialized:
    return
  _once_initialized = True

  for enum in (rightdown.LineTokenTypes, rightdown.BlockTokenTypes, rightdown.InlineTokenTypes, rightdown.PairedTokenTypes):
    for tag in enum:
      definition  = enum.Definition(tag)
      if hasattr(definition, 'pattern'):
        if definition.pattern and definition.pattern != True:
          definition.pattern.Initialize()

  safetycheck     = rightdown.BlockTokenTypes.Definition(rightdown.BLOCK_PSEUDO_YAML).pattern
  if safetycheck.regexp != rightdown.YAML_TAG_PATTERN_REGEXP:
    raise base.errors.RightDownTagPatternError('Our test pattern did not compile as expected.', safetycheck.regexp)



class BasePattern:
  ''' Base class for the various types of pattern matchers we can use. '''

  def __init__(self, program=None):
    self.program    = program

  @property
  def code(self):
    program         = self.program
    if program == "'":
      program       = '"\'"'
    else:
      program       = "'" + program.replace('\\', '\\\\').replace('\n', '\\n') + "'"
    return base.utils.ClassName(self) + '(' + program + ')'

  def Initialize(self):
    ''' Child classes should do any pre-processing setup here. '''

  def FindMatch(self, token, tag, debug=False):
    ''' Return None or (index0, index1) for the first match that's possible inside token.data '''

  def DoesMatch(self, token):
    ''' Simplifed wrapper around FindMatch, if all you need is a bool. '''
    return bool(self.FindMatch(token, None))



###
## Patterns for string-like data
#

class PatternForString(BasePattern):
  ''' Parent class for any pattern that handles a string as input data. '''



class ExactPattern(PatternForString):
  ''' The simplest possible pattern is an exact string match. '''

  def FindMatch(self, token, tag, debug=False):
    if self.program == token.data:
      return 0, len(token.data)



class PrefixPattern(PatternForString):
  ''' The other simplest possible pattern is a string prefix match. '''

  def FindMatch(self, token, tag, debug=False):
    if token.data.startswith(self.program):
      return 0, len(token.data)



class RegExPattern(PatternForString):
  ''' A pattern type that thinly wraps python's `re` module.
      Mostly this exists so that we don't have to compile all our regular expressions
      at module load time.
  '''

  def __init__(self, program):
    super().__init__(program)
    self.compiled   = None

  def Initialize(self):
    if self.program and not self.compiled:
      self.compiled = re.compile(self.program)

  def FindMatch(self, token, tag, debug=False):
    match           = self.compiled and self.compiled.fullmatch(token.data)
    if match:
      return 0, len(token.data)



class IndentedTextPattern(PatternForString):
  ''' A pattern that matches any indented line. '''

  def FindMatch(self, token, tag, debug=False):
    options         = rightdown.RightDownOptions.GetCurrent()
    if options.indent_width:
      if token.data and token.white0 >= options.indent_width:
        return 0, len(token.data)



class AlmostIndentedTextPattern(PatternForString):
  ''' A pattern that matches any line indented to tab_width if that's < indent_width. '''

  def FindMatch(self, token, tag, debug=False):
    options         = rightdown.RightDownOptions.GetCurrent()
    if options.tab_width and options.indent_width:
      if token.data and token.white0 >= options.tab_width and token.white0 < options.indent_width:
        return 0, len(token.data)



class InlinePattern(PatternForString):
  ''' A pattern type that matches inside the string, rather than the entire string.
      Notably, uses Position to restrict matches based on lookbehind/lookahead.
  '''

  def FindMatch(self, token, tag, debug=False):
    index0          = 0
    index           = token.data.find(self.program)
    proglen         = len(self.program)
    textlen         = len(token.data)
    while index >= 0 and index0 < textlen:
      index1        = index + proglen
      lookbehind    = index and token.data[index-1] or token.lookbehind
      lookahead     = (index1 < textlen - 1) and token.data[index1] or token.lookahead
      if rightdown.InlineTokenTypesEnum.ConfirmPosition(tag, lookbehind, self.program[0], self.program[-1], lookahead):
        return index, index1
      index0        = index + 1
      index         = token.data.find(self.program, index0)



class InlineWhitespacePattern(PatternForString):
  ''' Matches runs of whitespace in the string. '''

  def FindMatch(self, token, tag, debug=False):
    return base.utils.FindWhitespace(token.data)



###
## Patterns for lists of tokens
#



class PatternForTokenList(BasePattern):
  ''' Parent class for any pattern that handles a list of tokens as input data. '''



class PairedPattern(PatternForTokenList):
  ''' The only pattern you should use with paired token types. '''

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.open       = None
    self.close      = None

  def Initialize(self):
    if self.program:
      self.open     = rightdown.InlineTokenTypesEnum.MakeTag(self.program, rightdown.POSITION_OPEN)
      self.close    = rightdown.InlineTokenTypesEnum.MakeTag(self.program, rightdown.POSITION_CLOSE)

  def FindMatch(self, token, tag, debug=False):
    for index1 in range(1, len(token.data)):
      if token.data[index1].type == self.close:
        for index0 in range(index1-1, -1, -1):
          if token.data[index0].type == self.open:
            return index0, index1



###
## Everything below here is TagPattern or TagPatternCompiler
#


class TagPattern(PatternForTokenList):
  ''' Python's `re` module is lovely, if...

        1. you're tokenizing text
        2. your datastream is complete

      If, say, you're a speculative tokenizer, you need to be able to handle lists
      of things that are not characters of text, and you need to be able to handle
      a data underrun and (maybe) still successfully match.

      To these ends, a TagPattern will match against a programmed sequence of enum
      tags.  We have defined our own program syntax, which looks remarkably similar
      to highly-simple regular expressions.  The TagPatternCompiler turns a program
      in this syntax into a tree of TagPattern nodes, which together are a compiled
      form of the program.
  '''

  def __init__(self, program=None):
    super().__init__(program)
    self.operator   = None      # an exact LineToken type to match, or one of:  |, *, +
    self.indent     = 0         # count of whitespace before us in a long-form program
    self.children   = []        # TagPattern instances

  def __str__(self):
    return ((self.operator or '') + (self.children and '()' or '')) or '-'

  @property
  def pattern(self):
    ''' The tag pattern as long-form program. '''
    lines           = []
    if self.operator:
      lines.append(' ' * self.indent + self.operator)
    for child in self.children:
      lines.append(child.pattern)
    return '\n'.join(lines)

  @property
  def regexp(self):
    ''' The tag pattern as a regular expression. '''
    children        = [x.regexp for x in self.children]
    if self.operator == '|':
      return '|'.join(['(' + x + ')' for x in children])
    children        = ''.join(children)
    if self.operator == '*' or self.operator == '+':
      return '(' + children + ')' + self.operator
    operator        = self.operator and ('_' + self.operator) or ''
    return operator + children

  def Initialize(self):
    ''' Triggers the TagPatternCompiler if we haven't invoked it yet. '''
    if self.program and not (self.operator or self.children):
      TagPatternCompiler.Compile(self)

  def Setup(self, line):
    ''' Used by TagPatternCompiler to setup this specific node. '''
    lstripped       = line.lstrip()
    self.indent     = len(line) - len(lstripped)
    self.operator   = lstripped.rstrip()

  def Finalize(self, indent=None):
    ''' Validates our node and recursively updates line indentation to be exactly 2-spaces. '''
    if indent is None:
      indent        = -2
    self.indent     = indent
    indent          = indent + 2
    for child in self.children:
      child.Finalize(indent=indent)

  def FindMatch(self, token, tag, debug=False):
    ''' Return None or (index0, index1) for the first match that's possible inside token.data '''
    for index0 in range(len(token.data)):
      eaten, result = self._Consume(token.data[index0:], debug=debug)
      if eaten and result in rightdown.RESULTS_COLLAPSE_ORDER:
        return index0, index0 + eaten

  def _Consume(self, linetokens, indent=0, debug=False):
    ''' Recursive mechanics of pattern matching, returns (eaten, result). '''
    if debug:
      base.utils.Log('ENTER', ('  ' * indent) + str(self) + ': ' + ','.join([x.type or '' for x in linetokens]))
    def LogExitCase(eaten, result, msg):
      if debug:
        base.utils.Log(' EXIT', '{}•{} "{}" ({})'.format('  ' * indent, rightdown.Results.Name(result), msg, eaten))
      return eaten, result

    options         = rightdown.RightDownOptions.GetCurrent()
    eaten           = 0
    lastresult      = rightdown.RESULT_OKAY

    # Regular tokens
    if self.operator and not self.operator in ('|', '*', '+'):
      if not linetokens:
        return LogExitCase(eaten, rightdown.RESULT_HUNGRY, 'data underflow')
      if self.operator.startswith('!'):
        denotted    = self.operator[1:]
        if linetokens[0].type == denotted:
          return LogExitCase(0, rightdown.RESULT_BROKEN, 'token match on NOT')
      elif linetokens[0].type != self.operator:
        return LogExitCase(0, rightdown.RESULT_BROKEN, 'token mismatch')
      eaten         = 1
      lastresult    = rightdown.RESULT_HALT

    # Anything that's not a loop or an OR: flow through to children
    if not self.operator in ('|', '*', '+'):
      for child in self.children:
        childfood, result = child._Consume(linetokens[eaten:], indent=indent+1, debug=debug)
        if result == rightdown.RESULT_BROKEN:
          return LogExitCase(0, rightdown.RESULT_BROKEN, 'child mismatch')
        eaten       = eaten + childfood
        lastresult  = result

      if eaten < len(linetokens):
        if linetokens[eaten].empty:   # handle empty tokens 5/5
          return LogExitCase(eaten, rightdown.RESULT_FULL, 'data overflow(-ish)')
        return LogExitCase(eaten, rightdown.RESULT_OVERFULL, 'data overflow')
      return LogExitCase(eaten, lastresult, 'regular')

    # OR token - first non-broken child
    if self.operator == '|':
      for index, child in enumerate(self.children):
        eaten, result = child._Consume(linetokens, indent=indent+1, debug=debug)
        if result != rightdown.RESULT_BROKEN:
          return LogExitCase(eaten, result, 'child={}'.format(index))
      return LogExitCase(0, rightdown.RESULT_BROKEN, 'failed "or"')

    # loop token - iterate over children until we can't
    loops           = 0
    max_eaten       = len(linetokens)
    while eaten < max_eaten:
      done          = False
      loopeaten     = 0
      for child in self.children:
        childfood, lastresult = child._Consume(linetokens[(eaten + loopeaten):], indent=indent+1, debug=debug)
        if lastresult in (rightdown.RESULT_BROKEN, rightdown.RESULT_HUNGRY):
          if lastresult == rightdown.RESULT_HUNGRY:
            eaten   = eaten + loopeaten + childfood
          done      = True
          break
        loopeaten   = loopeaten + childfood
      if done:
        break
      loops         = loops + 1
      eaten         = eaten + loopeaten

    if self.operator == '+' and loops < 1:
      if eaten == max_eaten and lastresult in (rightdown.RESULT_HUNGRY, rightdown.RESULT_OKAY):
        return LogExitCase(eaten, rightdown.RESULT_HUNGRY, 'zero-length plus')
      return LogExitCase(0, rightdown.RESULT_BROKEN, 'zero-length plus')
    return LogExitCase(eaten, rightdown.RESULT_OKAY, 'loops={}'.format(loops))



class TagPatternCompiler:
  ''' Processes our grep-like pattern syntax into a TagPattern tree. '''

  @classmethod
  def Compile(klass, pattern):
    ''' Sets up a tree of TagPattern nodes. '''
    program         = pattern.program
    if not program:
      raise base.errors.RightDownTagPatternError('empty pattern', pattern)

    shortform       = ',' in program
    longform        = '\n' in program
    if shortform and longform:
      raise base.errors.RightDownTagPatternError('unsure if using short-form or long-form', program)

    if not longform:
      program       = klass._MakeLongFormProgram(program)
    program         = klass._CleanLongFormProgram(program)
    tree            = klass._ParseLongFormProgram(program)

    pattern.indent    = 0
    pattern.operator  = tree.operator
    pattern.children  = tree.children

  ###
  ## Mechanics
  #

  @classmethod
  def _MakeLongFormProgram(klass, pattern):
    ''' Translates a short-form pattern to a long-form pattern. '''
    if not pattern:
      return pattern
    tokens          = pattern.split(',')
    lines           = []
    for token in tokens:
      indent        = ''
      if token.startswith('+') or token.startswith('*'):
        indent      = '  '
        lines.append(token[0])
        token       = token[1:]
      if '|' in token:
        lines.append(indent + '|')
        for subtoken in token.split('|'):
          lines.append(indent + '  ' + subtoken)
      else:
        lines.append(indent + token)
    return '\n'.join(lines)

  @classmethod
  def _CleanLongFormProgram(klass, pattern):
    ''' Removes the leading whitespace from every line in a pattern. '''
    if not pattern:
      return pattern
    lines           = pattern.split('\n')
    nonblanks       = [x for x in lines if x and not x.isspace()]
    indent          = nonblanks and len(nonblanks[0]) - len(nonblanks[0].lstrip())
    if not indent:
      return pattern
    newlines        = []
    for line in lines:
      if not line or line.isspace():
        continue
      if len(line) < indent:
        raise base.errors.RightDownTagPatternError('indentation error', pattern)
      newlines.append(line[indent:])
    return '\n'.join(newlines)

  @classmethod
  def _ParseLongFormProgram(klass, pattern):
    ''' Returns a parse-tree for the block pattern. '''
    lines           = pattern.split('\n')
    if not lines:
      return None

    if lines[0].lstrip() != lines[0]:
      raise base.errors.RightDownTagPatternError('please clean the pattern', pattern)

    root            = TagPattern()
    root.indent     = -1
    stack           = [root]
    lastnode        = root
    for line in lines:
      node          = TagPattern()
      node.Setup(line)
      parent        = stack[-1]
      if lastnode.indent < node.indent:
        stack.append(lastnode)
        lastnode.children.append(node)
      elif lastnode.indent > node.indent:
        while stack[-1].indent >= node.indent:
          stack     = stack[:-1]
        parent      = stack[-1]
        parent.children.append(node)
      else:
        parent.children.append(node)
      lastnode      = node

    root.Finalize()
    return root
