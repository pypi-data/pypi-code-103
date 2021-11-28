#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown
import re


class RightDownOptions:
  ''' Configuration settings for processing and rendering rightdown text. '''

  # How many spaces equals a tab?
  tab_width                   = 2

  # How many spaces equals an indented line?  0 to turn off indented blocks
  indent_width                = 3

  # How many characters when printing lines to the console?  0 to turn off truncation
  truncate_width              = 60

  # How many characters to a line when emitting plain text?
  wrap_width                  = 90

  # How many levels of title should we try to extract as metadata?
  title_metadata_levels       = 3

  # When rendering text, should we include formatting characters?
  text_include_formatting     = True

  # When rendering HTML, should we include formatting characters?
  html_include_formatting     = False

  # Should we wrap your HTML output with an HTML preamble, making it a real document and not a snippet?
  html_add_head               = True

  # Should HTML be compacted down to one line or spread out and indented?
  compact_html                = False

  # Should fenced code blocks be stripped of leading whitespace?
  fenced_code_strip_space     = True

  # HTML definition lists are nifty, but divs with lists inside are more structurally sound
  definition_list_as_field    = True

  ## Performance Related

  # Should breaks inside paragraphs or fenced blocks be not seen as breaks?
  contextual_breaks           = True

  # Should fields, data, and links be accumulated through a file or returned only for the current fragment?
  accumulate_data             = True

  # Should we defer inline processing on fragments that have not been accessed yet?
  defer_inline_processing     = True

  # Allow fragment 0 metadata to override other parser options?
  # XYZZY: maybe someday; would require a second parse
  #allow_option_overrides = True

  @base.utils.anyproperty
  def fast_fragments(self):
    ''' Returns True if it's possible for us to quickly skim to requested fragment when processing. '''
    return not self.contextual_breaks and not self.accumulate_data

  @staticmethod
  def GetCurrent():
    ''' Returns the current options that have been set somewhere on our call stack. '''
    stack           = RightDownOptions._Stash().stack
    return stack and stack[-1] or RightDownOptions()

  def __init__(self, **kwargs):
    stack           = RightDownOptions._Stash().stack
    if stack:
      base.utils.SetAttrs(self, **base.utils.GetAttrs(stack[-1], capitals=False))
    base.utils.SetAttrs(self, **kwargs)

  def __enter__(self):
    self._Stash().stack.append(self)
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self._Stash().stack.pop(-1)
    if exc_value:
      raise

  class _Stash(metaclass=base.utils.ThreadLocal):
    ''' Pocket universe to remember instances on the cuurent thread that are between enter and exit. '''
    def __init__(self):
      self.stack    = []



class RightDownData:
  ''' Represents a completely processed blob of rightdown content. '''

  @staticmethod
  def Process(content, fragment=None, options=None, **kwargs):
    ''' Digests a string of text, returns a RightDownData instance. '''
    if options or kwargs:
      options       = options or RightDownOptions(**kwargs)
      with options:
        return rightdown.Processor().Process(content, fragment=fragment)
    return rightdown.Processor().Process(content, fragment=fragment)

  def Fragments(self):
    ''' In case doing `len()` against our .fragments property is against your ethics. '''
    return len(self.fragments)

  def DebugString(self, fragment=None, rich=True, indent=0):
    ''' Returns a text representation of the parsed rightdown tree. '''
    return self._DeferToFragment('DebugString', fragment, str, rich=rich, indent=indent, finish=False)

  ###
  ## Document Rendering
  #

  def Text(self, fragment=None):
    ''' Renders the rightdown content out as rightdown content. '''
    result          = self._DeferToFragment('Text', fragment, str)
    return result and (result + '\n') or ''

  def Html(self, fragment=None):
    ''' Renders the content out as HTML. '''
    result          = self._DeferToFragment('Html', fragment, str, collapse_empty=True)
    if result and self.options.html_add_head:
      head          = self.HTML_DOCUMENT
      if self.options.compact_html:
        head        = head.replace('\n', '')
      result        = head.format(result)
    return result

  HTML_DOCUMENT     = '<!DOCTYPE html>\n<html>\n<head><meta charset="utf-8"></head>\n<body>\n{}\n</body>\n</html>'

  ###
  ## Structured Data
  #

  def Metadata(self, fragment=None, html=False):
    ''' Returns a dictionary of structured data from the (invisible) YAML prefix. '''
    return self._DeferToFragment('Metadata', fragment, dict, html=html)

  def Fields(self, fragment=None, html=False):
    ''' Returns a dictionary of structured data from (visible) tuples and definition lists. '''
    return self._DeferToFragment('Fields', fragment, dict, html=html)

  def Links(self, fragment=None, html=False):
    ''' Returns a list of (name, target) tuples for links. '''
    return self._DeferToFragment('Links', fragment, list, html=html)

  def Taxonomies(self, fragment=None, html=False):
    ''' Returns a list of tree-like structures in our data, like bullet and number lists. '''
    return self._DeferToFragment('Taxonomies', fragment, list, html=html)

  ###
  ## Mechanics
  #

  def __init__(self, options=None):
    self.options    = options or RightDownOptions.GetCurrent()
    self.fragments  = []      # list of Fragment instances
    self.fragment   = None    # were we filtered to a specific fragment at time of Process()?

  def _DeferToFragment(self, methodname, fragment, type0, finish=True, **kwargs):
    ''' Calls the appropriate method on the right fragment, or fragments. '''
    if self.fragment is None:
      if fragment is not None and (fragment < 0 or fragment >= len(self.fragments)):
        raise base.errors.RightDownFragmentOutOfRange(fragment)
    elif fragment is not None:
      if self.fragment != fragment:
        raise base.errors.RightDownFragmentMismatch(self.fragment, fragment)
      fragment      = None

    if not self.fragments:
      return type0()

    with self.options:
      if (type0 != str and self.options.accumulate_data) or (type0 == str and fragment is None):
        if fragment is None:
          return self._AccumulateData(methodname, len(self.fragments), type0, finish=finish, **kwargs)
        return self._AccumulateData(methodname, fragment, type0, finish=finish, **kwargs)
      fragment      = self.fragments[fragment or 0]
      if finish and hasattr(fragment, 'finished') and not fragment.finished:
        fragment.FinishProcessing()
      return getattr(fragment, methodname)(**kwargs)

  def _AccumulateData(self, methodname, limit, type0, finish=True, collapse_empty=False, **kwargs):
    ''' Collects the results of calling the method on a bunch of our fragments. '''
    results         = type0()
    for index, fragment in enumerate(self.fragments):
      if finish and hasattr(fragment, 'finished') and not fragment.finished:
        fragment.FinishProcessing()
      if index >= limit:
        break
      addon         = getattr(fragment, methodname)(**kwargs)
      if type0 == dict:
        results.update(addon)
      elif type0 == list:
        results.extend(addon)
      elif type0 == str:
        if collapse_empty and not addon:
          continue
        if results:
          results   = results + '\n'
        results     = results + addon
      else:
        results     = results + addon
    return results
