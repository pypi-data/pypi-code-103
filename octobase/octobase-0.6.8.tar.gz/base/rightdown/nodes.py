#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown
import string
import textwrap


class Node(base.Controller):
  ''' Parent class for every node in the tree of rightdown content. '''

  CONTROLLER_ITEM_NAME  = 'token'

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    if self.token:
      self.type     = self.token.type
      self.enum     = self.token.enum
    else:
      self.type     = self.CONTROLLER_NAME
      self.enum     = self.CONTROLLER_NAMESPACE

    self.children   = []

  @property
  def definition(self):
    ''' Returns our enum definition. '''
    if self.enum and (self.type or self.type in self.enum):
      return self.enum.Definition(self.type)

  @base.utils.cached_property
  def html(self):
    ''' Returns our token type's HTML tag pattern, if we have one. '''
    return self._Definition('html')

  @base.utils.cached_property
  def html_is_ascii_alnum(self):
    ''' It turns out '⅕'.isalnum() is True in Python, but not True here. '''
    alphanum        = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return isinstance(self.html, str) and not [c for c in self.html if c not in alphanum]

  @base.utils.cached_property
  def pattern(self):
    ''' Returns our token type's pattern, if we have one. '''
    return self._Definition('pattern')

  @base.utils.cached_property
  def options(self):
    return rightdown.RightDownOptions.GetCurrent()

  @property
  def name(self):
    ''' Returns a human-readable name for our node type. '''
    if self.enum and (self.type or self.type in self.enum):
      return self.enum.Name(self.type)
    return base.utils.ClassName(self)

  ###
  ## Document Rendering
  #

  def Text(self, joiner='\n', *args, **kwargs):
    ''' Renders the rightdown content out as rightdown content, returns a single string. '''
    results         = self.WrapText(*args, **kwargs)
    return results and joiner.join(results) or ''

  def Html(self, joiner=None, *args, **kwargs):
    ''' Renders the content of all our child nodes as HTML, returns a string. '''
    results         = self.WrapHtml(*args, **kwargs)
    if joiner is None:
      joiner        = not self.options.compact_html and '\n' or ''
    return results and joiner.join(results) or ''

  def DebugString(self, joiner='\n', rich=False, suffix='', *args, **kwargs):
    ''' Renders the content out as a tree of node names. '''
    return joiner.join(self.DebugParts(rich=rich, suffix=suffix))

  def DebugParts(self, rich=False, indent=0, ourself='', suffix=''):
    ourself         = ourself or ('{:32s}'.format('  '*indent + self.name + ' Node') + suffix).rstrip()
    children        = self._AccumulateLists('DebugParts', rich=rich, indent=indent+1)
    token           = self.token and self.token.DebugString(rich=rich, indent=(2*(indent+1)))
    return [x for x in (ourself, token) if x] + children

  ###
  ## Structured Data
  #

  def Metadata(self, html=False):
    ''' Returns a dictionary of structured data from the (invisible) YAML prefix. '''
    return self._AccumulateDicts('Metadata', html=html)

  def Fields(self, html=False):
    ''' Returns a dictionary of structured data from (visible) tuples and definition lists. '''
    return self._AccumulateDicts('Fields', html=html)

  def Links(self, html=False):
    ''' Returns a list of (name, target) for links. '''
    return self._AccumulateLists('Links', html=html)

  def Taxonomies(self, html=False):
    ''' Returns all the tree-like structures in our data, like bullet and number lists. '''
    return self._AccumulateLists('Taxonomies', html=html)

  ###
  ## Child Class Hooks
  #

  def FinishProcessing(self):
    ''' Child classes should pull from self.token everything they need then call through super(). '''
    self.token      = None
    for child in self.children:
      if isinstance(child, Node):
        child.FinishProcessing()

  def TextParts(self, *args, **kwargs):
    ''' Returns a list of lines of rightdown text. '''
    return self._AccumulateLists('WrapText', *args, **kwargs)

  def HtmlParts(self, *args, **kwargs):
    ''' Returns a list of lines of rendered HTML. '''
    return self._AccumulateLists('WrapHtml', *args, **kwargs)

  def WrapText(self, indent=False, collapse_empty=False, *args, **kwargs):
    ''' Wraps the results of calling TextParts() with whatever we might need. '''
    innertext       = self.TextParts(*args, **kwargs)
    if collapse_empty:
      innertext     = [x for x in innertext if x]

    if indent:
      indent        = ' '*self.options.tab_width
      innertext     = [indent + x for x in innertext]

    return innertext

  def WrapHtml(self, indent=True, collapse_empty=False, *args, **kwargs):
    ''' Roughly akin to calling:  [HtmlOpen()] + HtmlParts() + [HtmlClose()] '''
    innerhtml       = self.HtmlParts(*args, **kwargs)
    if collapse_empty:
      innerhtml     = [x for x in innerhtml if x]

    if not innerhtml:
      if isinstance(self.html, str) and not self.html_is_ascii_alnum:
        innerhtml   = [self.html]
      elif not self.html and self.pattern and self.pattern != True and self.pattern.program:
        innerhtml   = [self.pattern.program]

    open            = self.HtmlOpen()
    close           = self.HtmlClose()

    if indent and not self.options.compact_html:
      open          = ' '*self.options.tab_width + open
      if len(innerhtml) != 1:
        close       = ' '*self.options.tab_width + close

    if len(innerhtml) == 1 and not innerhtml[0].isspace():
      return [open + innerhtml[0].lstrip() + close]
    return [open] + innerhtml + [close]

  def HtmlOpen(self):
    ''' Returns the HTML blurb that should open this node. '''
    return self._HtmlTag('<')

  def HtmlClose(self):
    ''' Returns the HTML blurb that should close this node. '''
    return self._HtmlTag('</')

  def _HtmlTag(self, opener='<'):
    ''' Retrieves the html blurb we put before or after our children's html. '''
    if isinstance(self.html, tuple) or isinstance(self.html, list):
      tagnames      = list(self.html)
      if opener != '<':
        tagnames.reverse()
    elif self.html_is_ascii_alnum:
      tagnames      = (self.html,)
    else:
      return ''
    return ''.join([opener+x+'>' for x in tagnames])

  def _Definition(self, argname):
    ''' Retrieves an argument from our enum definition. '''
    definition      = self.definition
    return hasattr(definition, argname) and getattr(definition, argname) or None

  def _AccumulateLists(self, methodname, space_out_blocks=False, **kwargs):
    ''' Returns an aggregated list by calling 'methodname' on all our children. '''
    results         = []
    for node in self.children:
      result        = getattr(node, methodname)(**kwargs)
      if space_out_blocks and results and result and node.enum == rightdown.BlockTokenTypes:
        results.append('')
      if result:
        results.extend(result)
    return results

  def _AccumulateDicts(self, methodname, **kwargs):
    ''' Returns an aggregated dict by calling 'methodname' on all our children. '''
    results         = {}
    for node in self.children:
      results.update(getattr(node, methodname)(**kwargs) or {})
    return results

base.registry.UnRegister(Node)
