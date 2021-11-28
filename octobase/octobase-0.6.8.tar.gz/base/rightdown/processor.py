#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown
import re


class Processor:
  ''' The engine that digests a string of text into a RightDownData instance. '''

  @classmethod
  def Process(klass, content, fragment=None):
    ''' Takes text content, returns a RightDownData.  If you specify a fragment number,
        we return an instance populated with only that fragment.

        In our 3-stage processing, this is stages 1 and 2.  First we tokenize the content
        into a list of LineTokens, then we re-tokenize those into a list of BlockTokens.
        For post-processing, we group those BlockTokens into Fragment instances.

        The 3rd stage of processing, inline processing, is done by Nodes (Fragment is a Node)
        on an as-needed basis.
    '''
    if not content:
      return []

    options         = rightdown.RightDownOptions.GetCurrent()

    if fragment and options.accumulate_data:
      raise base.errors.RightDownCantAccumulate

    # pre-filter to requested fragment using regular expressions, if possible
    if fragment is not None and options.fast_fragments:
      content       = klass._IsolateFragment(content, fragment)

    # tokenizer stage 1 - turn the content into a list of LineTokens
    linetokens      = rightdown.LineTokenizer().Tokenize(content)

    # tokenizer stage 2 - turn the list of LineTokens into a list of BlockTokens
    blocktokens     = rightdown.BlockTokenizer().Tokenize(linetokens)

    # group those blocktokens into ProtoFragments
    fragments       = klass._MakeProtoFragments(blocktokens)

    # If we didn't filter to a fragment before, do it now
    if fragment is not None and not options.fast_fragments:
      if fragment > len(fragments):
        raise base.errors.RightDownFragmentOutOfRange(fragment)
      fragments     = [fragments[fragment]]

    # Nodes are now more useful than the tokens that make them
    data            = rightdown.RightDownData(options)
    data.fragments  = [x.MakeNode() for x in fragments]
    data.fragment   = fragment
    if fragments and not fragment:
      data.fragments[0].first = True

    # Kick off the next level of recursion
    if not options.defer_inline_processing:
      for fragment in data.fragments:
        fragment.FinishProcessing()

    return data

  @classmethod
  def ProcessInline(self, content, debug=False):
    ''' Returns an InlineNode which represents the fully processed string of text. '''
    if not content:
      return []
    tokenizer       = rightdown.InlineTokenizer()
    tokenlist       = tokenizer.Tokenize(content, debug=debug)
    tokenroots      = tokenizer.PairTokens(tokenlist, debug=debug)
    noderoots       = [x.MakeNode() for x in tokenroots]
    for node in noderoots:
      node.FinishProcessing()
    root            = rightdown.InlineNode()
    root.children   = noderoots
    return root


  ###
  ## Mechanics
  #

  @classmethod
  def _IsolateFragment(klass, content, fragment):
    ''' Filters the content to only the range that represents the requested fragment.
        **Hard breaks inside fenced code blocks *will* be broken on.**
    '''
    pattern         = re.compile(r'^---\s*$', flags=re.MULTILINE)

    prefix          = ''
    fragsleft       = fragment
    while fragsleft >= 0:
      match         = pattern.search(content)
      if not match:
        if fragsleft:
          raise base.errors.RightDownFragmentOutOfRange(fragment)
        return prefix + content
      start, end    = match.span()

      if start == 0 and not prefix:
        prefix      = content[start:end] + '\n'
        content     = content[min(end+1, len(content)):]

        match       = pattern.search(content)
        if not match:
          if fragsleft:
            raise base.errors.RightDownFragmentOutOfRange(fragment)
          return prefix + content
        start, end  = match.span()

      if not fragsleft:
        return prefix + content[:start]

      prefix        = content[start:end] + '\n'
      content       = content[min(end+1, len(content)):]
      fragsleft     = fragsleft - 1

    raise base.errors.RightDownFragmentOutOfRange(fragment)

  @classmethod
  def _MakeProtoFragments(klass, blocklist):
    ''' Splits a list of BlockTokens into a list of ProtoFragments, at hard break boundaries. '''
    fragment        = klass.ProtoFragment()
    fragmentlist    = [fragment]
    first           = True
    for block in blocklist:
      if block.type in (rightdown.BLOCK_PSEUDO_YAML, rightdown.BLOCK_HARD_BREAK):
        if not first:
          fragment  = klass.ProtoFragment()
          fragmentlist.append(fragment)
        if block.type == rightdown.BLOCK_PSEUDO_YAML:
          fragment.data.append(block)
      else:
        fragment.data.append(block)
      first         = False
    return fragmentlist

  class ProtoFragment(rightdown.BlockToken):
    ''' Special token-like thing that is a list of other tokens with a way to become a Fragment. '''
    def __init__(self):
      super().__init__(type=rightdown.BLOCK_FRAGMENT)
