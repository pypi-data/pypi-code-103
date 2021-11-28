#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown


class BaseToken:
  ''' Represents a type -- a tag in an enum -- and an associated list of chunks of data.
      As the caller (SuperToken) adds chunks to us, we return a result for whether we are
      still matching the expected pattern for our type or not.
  '''

  CONTROLLER_NAMESPACE      = None
  CONTROLLER_NAME_PROPERTY  = 'type'
  DEBUG_NAME_SUFFIX         = ' (token)'

  def __init__(self, **kwargs):
    self.type       = None
    self.data       = None
    self.halted     = False
    self.lookbehind = None          # last datum that comes before the first that's part of us
    self.lookahead  = None          # first datum that comes after the last one that's part of us
    base.utils.SetAttrs(self, **kwargs)
    if self.data is None:
      self.data     = []
    self.length     = len(self.data or '')

  def __str__(self):
    return '{:9s} {} {}'.format(self.type or 'empty', self.halted and 'HALT' or '', self.score)

  def __repr__(self):
    return '{}({}, [{}]){}'.format(base.utils.ClassName(self), self.type or 'None', len(self.data), self.halted and '!' or '')

  def __lt__(self, other):
    return self.score < other.score

  @property
  def enum(self):
    ''' Which token type enum our token belongs to. '''
    return self.CONTROLLER_NAMESPACE

  @property
  def name(self):
    ''' The name of our token type. '''
    return self.CONTROLLER_NAMESPACE.Name(self.type)

  @property
  def pattern(self):
    ''' The pattern this token type matches against. '''
    definition      = self.CONTROLLER_NAMESPACE.by_tag.get(self.type)
    return hasattr(definition, 'pattern') and definition.pattern or None

  @property
  def empty(self):
    ''' True if this token should be treated as a special, empty, breaking chunk of input. '''
    return not self.type

  def DebugString(self, rich=False, indent=0, suffix=''):
    ''' Returns a string that starts with our type name then lists any sub-tokens we contain. '''
    ourself         = ('{:32s}'.format(' '*indent + self.name + self.DEBUG_NAME_SUFFIX) + suffix).rstrip()
    if not self.data or not isinstance(self.data[0], BaseToken):
      return ourself
    children        = [x.DebugString(rich=rich, indent=(indent+2)) for x in self.data]
    children        = '\n'.join([x for x in children if x])
    return ourself + '\n' + children

  def MakeNode(self):
    ''' Returns the correct node instance for our type. '''
    return self.CONTROLLER_NAMESPACE and base.Controller.DowncastFor(self) or None



class LineToken(BaseToken):
  ''' Represents a single line of mostly-unprocessed text. '''

  CONTROLLER_NAMESPACE      = rightdown.LineTokenTypes
  DEBUG_NAME_SUFFIX         = ' Line'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.white0     = 0       # characters of whitespace stripped from beginning
    self.white1     = 0       # characters of whitespace stripped from end (excludes newline)

    if self.data:
      if '\t' in self.data:
        self.data   = self.data.replace('\t', ' '*rightdown.RightDownOptions.GetCurrent().tab_width)
      before        = len(self.data)
      self.data     = self.data.lstrip()
      self.white0   = before - len(self.data)
      before        = len(self.data)
      self.data     = self.data.rstrip()
      self.white1   = before - len(self.data)
    else:
      self.data     = ''

  @property
  def empty(self):
    return self.type == rightdown.LINE_EMPTY

  @property
  def longtext(self):
    ''' Our text with whitespace restored. '''
    return (' ' * self.white0) + self.data + (' ' * self.white1)

  @property
  def shorttext(self):
    ''' A truncated version of our indented text, suitable for console logging. '''
    longtext        = self.longtext
    truncate_width  = rightdown.RightDownOptions.GetCurrent().truncate_width
    if truncate_width:
      shorttext     = longtext[:truncate_width]
      if len(longtext) != len(shorttext):
        shorttext   = shorttext[:-1] + '…'
      return shorttext
    return longtext

  def DebugString(self, rich=False, indent=0):
    if not rich:
      return super().DebugString(rich=rich, indent=indent)
    return super().DebugString(rich=rich, indent=indent, suffix=self.shorttext)



class BlockToken(BaseToken):
  ''' Represents a group of related LineTokens '''

  CONTROLLER_NAMESPACE      = rightdown.BlockTokenTypes
  DEBUG_NAME_SUFFIX         = ' Block'

  @property
  def empty(self):
    return not self.data or len(self.data) == 1 and self.data[0].type == rightdown.LINE_EMPTY



class InlineToken(BaseToken):
  ''' Represents a snippet of text. '''

  CONTROLLER_NAMESPACE      = rightdown.InlineTokenTypes
  DEBUG_NAME_SUFFIX         = ' Inline'

  def __init__(self, *args, type=None, **kwargs):
    super().__init__(*args, type=(type or rightdown.INLINE_TEXT), **kwargs)
    self.data       = self.data or ''

  def DebugString(self, rich=False, indent=0):
    if self.type == rightdown.INLINE_SPACE:
      return ' '*indent + '_' * len(self.data)
    if self.type == rightdown.INLINE_TEXT:
      return ' '*indent + '"' + self.data + '"'
    return str(self.type)



class PairedToken(BaseToken):
  ''' Represents a snippet of text between an open- and close-position versions of an InlineToken. '''

  CONTROLLER_NAMESPACE      = rightdown.PairedTokenTypes
  DEBUG_NAME_SUFFIX         = ' Pair'

  def __init__(self, open=None, close=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.open       = open
    self.close      = close

  @property
  def text_open(self):
    if self.open:
      return rightdown.InlineTokenTypes.Definition(self.open).pattern.program
    return ''

  @property
  def text_close(self):
    if self.close:
      return rightdown.InlineTokenTypes.Definition(self.close).pattern.program
    return ''

  def DebugString(self, rich=False, indent=0):
    return ' '*indent + '{}[{}]'.format(self.type, ' '.join([x.DebugString(rich=rich, indent=0) for x in self.data]))
