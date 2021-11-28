#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown


class BaseTokenizer:
  ''' The tip of a somewhat generalized lexical analyzer.

      Specific sub-classes, below, specialize this for the three different passes
      of tokenization we need in order to process a single blob of rightdown text.
  '''

  TOKEN_TYPE         = None
  TOKEN_ENUM         = None

  def Tokenize(self, input, debug=False):
    tokenlist       = [self.TOKEN_TYPE(data=input)]
    isalive         = True
    while isalive:
      isalive       = False
      newtokenlist  = []
      for token in tokenlist:
        split       = not token.halted and self._DoOneSplit(token, debug=debug)
        if split:
          newtokenlist.extend(split)
          isalive   = True
          if debug:
            base.utils.Log('SPLIT', 'Split: ' + ' '.join([x.DebugString() for x in split]))
        elif token.type:
          newtokenlist.append(token)
      tokenlist     = newtokenlist

    if debug:
      base.utils.Log('SPLIT', 'Final: ' + ' '.join([x.DebugString() for x in tokenlist]))

    return tokenlist

  def _EnumDefinitions(self):
    ''' Returns a list of all the enum definitions that we are responsible for pattern-matching. '''
    return [x for x in self.TOKEN_ENUM.by_tag.values() if x.tag and hasattr(x, 'pattern') and x.pattern]

  def _DoOneSplit(self, token, debug=False):
    ''' If it's possible to split the token with any token pattern, do it. '''
    deepdebug       = debug and bool(debug-1)
    lastresort      = None

    for definition in self._EnumDefinitions():
      if definition.pattern == True:
        lastresort  = definition.tag
        continue

      match         = definition.pattern.FindMatch(token, definition.tag, debug=deepdebug)
      if not match:
        continue

      index0, index1          = match
      before, snippet, after  = token.data[:index0], token.data[index0:index1], token.data[index1:]
      newbehind               = before and before[-1] or token.lookbehind
      newahead                = after and after[0] or token.lookahead
      split                   = []

      if before:
        split.append(self.TOKEN_TYPE(lookbehind=token.lookbehind, data=before, lookahead=snippet[0]))

      split.append(self.TOKEN_TYPE(lookbehind=newbehind, data=snippet, lookahead=newahead, type=definition.tag))

      if after:
        split.append(self.TOKEN_TYPE(lookbehind=snippet[-1], data=after, lookahead=token.lookahead))

      if not before and not after:
        if debug:
          base.utils.Log('SPLIT', 'TotalMatch: ' + split[0].DebugString())
        split[0].halted   = True
        token.halted      = True
        return split

      return split

    if debug:
      base.utils.Log('SPLIT', 'NoMatch: ' + token.DebugString())
    token.halted    = True
    if lastresort:
      return self._SplitLastResort(token, lastresort)

  def _SplitLastResort(self, token, lastresort):
    ''' Splits or finalizes a token that matched no pattern. '''
    token.type      = lastresort
    return [token]



class LineTokenizer(BaseTokenizer):
  ''' '\n'-delimited string  -->  list of LineTokens '''
  TOKEN_ENUM        = rightdown.LineTokenTypes
  TOKEN_TYPE        = rightdown.LineToken

  def Tokenize(self, input, debug=False):
    ''' The LineTokenizer is a simpler algorithm than later tokenizing steps: Here we just
        break on \n, then make a LineToken out of each piece, and assign it the first matching
        token type we can find.
    '''
    tokenlist       = []
    for chunk in input.rstrip('\n').split('\n'):
      lastresort    = None
      token         = self.TOKEN_TYPE(data=chunk)
      tokenlist.append(token)
      for definition in self._EnumDefinitions():
        if definition.pattern == True:
          lastresort  = definition.tag
        elif definition.pattern.DoesMatch(token):
          token.type  = definition.tag
          break
      if lastresort and not token.type:
        token.type  = lastresort
    return tokenlist



class BlockTokenizer(BaseTokenizer):
  ''' list of LineTokens  -->  list of BlockTokens '''
  TOKEN_TYPE        = rightdown.BlockToken
  TOKEN_ENUM        = rightdown.BlockTokenTypes

  def _SplitLastResort(self, token, lastresort):
    ''' Splits a single Paragraph token into multiple, based on Empty lines. '''
    paragraphs      = []
    options         = rightdown.RightDownOptions.GetCurrent()

    paragraph       = []
    for linetoken in token.data:
      if linetoken.empty:
        paragraph   = []
        continue
      if not paragraph:
        paragraphs.append(paragraph)
      paragraph.append(linetoken)

    tokenlist       = []
    for paragraph in paragraphs:
      tokenlist.append(self.TOKEN_TYPE(data=paragraph))

    if len(tokenlist) == 1:
      tokenlist[0].type   = lastresort
      tokenlist[0].halted = True

    return tokenlist



class InlineTokenizer(BaseTokenizer):
  ''' string  -->  list of InlineTokens '''
  TOKEN_TYPE        = rightdown.InlineToken
  TOKEN_ENUM        = rightdown.InlineTokenTypes

  def PairTokens(self, tokenlist, debug=False):
    ''' Matches open/close pairs to make a tree from a list of inline tokens. '''
    opentags        = set()
    closetags       = set()
    openings        = {}        # InlineTokenType: (PairTokenType, [ indices ])
    pairings        = {}        # closing InlineTokenType: opening InlineTokenType

    # init opens/closes with each possible tag type
    for pairtag, opentag, closetag in self.TOKEN_ENUM.AllPairs():
      opentags.add(opentag)
      closetags.add(closetag)
      openings[opentag]   = (pairtag, [])
      pairings[closetag]  = opentag

    lastlen         = 0
    while tokenlist and len(tokenlist) != lastlen:
      lastlen       = len(tokenlist)

      if debug:
        base.utils.Log('PAIR ', 'Iterating: ' + ' '.join([x.DebugString() for x in tokenlist]))

      # scan forward through tokenlist
      for index, token in enumerate(tokenlist):
        # remember open tags that we see
        if token.type in opentags:
          openings[token.type][1].append(index)

        # stop at the first close tag
        if token.type in closetags:
          closetag  = token.type
          opentag   = pairings[token.type]
          pair, indices = openings[opentag]
          indices   = [x for x in indices if x < index]
          if indices:
            # we have a matching open!  cut it out and restart the loop
            index0  = indices[-1]
            index1  = index+1
            newtoken      = rightdown.PairedToken(type=pair, open=opentag, close=closetag)
            newtoken.data = tokenlist[index0+1:index1-1]
            tokenlist = tokenlist[:index0] + [newtoken] + tokenlist[index1:]
            if lastlen and len(tokenlist) > lastlen:
              raise base.errors.RightDownProcessingError('How did we get bigger from snipping out a pair?')
            break

    if debug:
      base.utils.Log('PAIR ', 'Final: ' + ' '.join([x.DebugString() for x in tokenlist]))
    return tokenlist

  def _EnumDefinitions(self):
    ''' Sorts our definitions by length of program. '''
    definitions     = [x for x in self.TOKEN_ENUM.by_tag.values() if x.tag and hasattr(x, 'pattern') and x.pattern]
    definitions.sort(key=lambda x: x.pattern != True and x.pattern.program and -len(x.pattern.program) or 0)
    return definitions
