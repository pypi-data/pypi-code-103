#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown


class InlineNode(rightdown.Node):
  ''' Parent class for any node that handles an inline token. '''

  CONTROLLER_NAMESPACE  = rightdown.InlineTokenTypes

  def Text(self, joiner='', *args, **kwargs):
    return super().Text(joiner='')

  def Html(self, joiner='', *args, **kwargs):
    return super().Html(joiner='', *args, **kwargs)

  def DebugString(self, joiner='', *args, **kwargs):
    return super().DebugString(joiner=' ', *args, **kwargs)

  def WrapText(self, indent=False, *args, **kwargs):
    return super().WrapText(indent=False, *args, **kwargs)

  def TextParts(self, *args, **kwargs):
    children        = super().TextParts(*args, **kwargs)
    if children:
      return children

    pattern         = self.pattern
    if pattern and pattern.program:
        return [pattern.program]

    return children

  def WrapHtml(self, indent=False, *args, **kwargs):
    return super().WrapHtml(indent=False, *args, **kwargs)

  def DebugParts(self, indent=0, ourself='', *args, **kwargs):
    if type(self) == InlineNode and not self.type:
      return self._AccumulateLists('DebugParts', indent=indent+1, *args, **kwargs)
    ourself         = ourself or self.type or base.utils.ClassName(self)
    children        = super().DebugParts(ourself=ourself, *args, **kwargs)
    if len(children) > 1:
      children      = [children[0] + '[' + children[1]] + children[2:]
      children[-1]  = children[-1] + ']'
    return children



class Text(InlineNode):
  ''' A node that represents an atomic chunk of text. '''

  CONTROLLER_NAME   = rightdown.INLINE_TEXT

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.text       = ''

  def FinishProcessing(self):
    if self.token:
      self.text     = self.token.data
    super().FinishProcessing()

  def TextParts(self, *args, **kwargs):
    return [self.text]

  def HtmlParts(self, *args, **kwargs):
    return [self.text]

  def DebugParts(self, *args, **kwargs):
    return ['"' + self.text + '"']



class Space(Text):
  CONTROLLER_NAME   = rightdown.INLINE_SPACE

  def DebugParts(self, *args, **kwargs):
    return len(self.text) > 1 and ['__'] or ['_']



class PairedNode(InlineNode):
  ''' Parent class for the subset of nodes that handle paired inline tokens. '''
  CONTROLLER_NAMESPACE  = rightdown.PairedTokenTypes

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

  def HtmlOpen(self):
    return super().HtmlOpen() or self.text_open

  def HtmlClose(self):
    return super().HtmlClose() or self.text_close

  def FinishProcessing(self):
    if self.token:
      self.children = [x.MakeNode() for x in self.token.data]
      self.open     = self.token.open
      self.close    = self.token.close
    super().FinishProcessing()

  def TextParts(self, *args, **kwargs):
    return [self.text_open] + super().TextParts(*args, **kwargs) + [self.text_close]

  def DebugParts(self, *args, **kwargs):
    ourself         = self.type or base.utils.ClassName(self)
    return super().DebugParts(ourself=ourself, *args, **kwargs)
