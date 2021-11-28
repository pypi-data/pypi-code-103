#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown

from . import patterns


class InlineTokenTypesEnum(base.Enum):
  ''' Specialization of Enum with a different way of adding new entries. '''

  @staticmethod
  def Position(tag):
    ''' Decodes the Position that's part of one of our tags. '''
    return ''.join([c for c in tag if c in '<.#-'])

  @staticmethod
  def MakeName(name, position):
    ''' Returns the name for an inline token type tag, given a position. '''
    return rightdown.Positions.Name(position) + ' ' + name

  @staticmethod
  def MakeTag(tag, position):
    ''' Returns the true tag for an inline token type, given a position. '''
    if position == rightdown.POSITION_OPEN:
      return tag + '<'
    if position == rightdown.POSITION_CLOSE:
      return '>' + tag
    if position == rightdown.POSITION_MIDDLE:
      return '>' + tag + '<'
    if position == rightdown.POSITION_OPENISH:
      return tag + '--'
    if position == rightdown.POSITION_CLOSEISH:
      return '-' + tag
    if position == rightdown.POSITION_SELFISH:
      return '#' + tag
    if position == rightdown.POSITION_START:
      return tag + '<<'
    if position == rightdown.POSITION_END:
      return '>>' + tag
    return tag

  @staticmethod
  def ConfirmPosition(tag, lookbehind, ourfirst, ourlast, lookahead):
    ''' Tests if the tag's encoded position matches a pair of past/next conditions. '''
    position        = ''.join([c for c in tag if c in '><#-'])
    if position == rightdown.POSITION_ANYWHERE:
      return True

    left            = lookbehind is not None and not lookbehind.isspace()
    softleft        = left and not lookbehind.isalnum() and (not ourfirst.isalnum() or lookbehind != ourfirst)

    right           = lookahead is not None and not lookahead.isspace()
    softright       = right and not lookahead.isalnum() and (not ourlast.isalnum() or lookahead != ourlast)

    if position == rightdown.POSITION_OPEN:
      return right and softleft or not left
    if position == rightdown.POSITION_CLOSE:
      return left and softright or not right
    if position == rightdown.POSITION_MIDDLE:
      return left and right
    if position == rightdown.POSITION_OPENISH:
      return softleft or not left
    if position == rightdown.POSITION_CLOSEISH:
      return softright or not right
    if position == rightdown.POSITION_SELFISH:
      return (softleft or not left) and (softright or not right)
    if position == rightdown.POSITION_START:
      return lookbehind is None
    if position == rightdown.POSITION_END:
      return lookahead is None

  def AllPairs(self):
    ''' Returns [ (pair type, open inline type, close inline type), ... ] for all paired token types. '''
    return self.allpairs

  def AllPrograms(self):
    ''' Returns [ (tag, program), ... ] for all token types that have a program. '''
    return self.allprograms

  ###
  ## Setup
  #

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.pairenum     = None
    self.allpairs     = []    # [ (pairtag, opentag, closetag), ... ]
    self.allprograms  = []    # [ (tag, program), ... ]

  def SetPairedTokenTypes(self, pairs):
    ''' If setting a property without a function call violates your ethics. '''
    self.pairenum   = pairs

  def AddPositions(self, name, tag, html=None, pairhtml=None, **positions):
    ''' Adds to the enum one or more entries for a new type of inline token. '''
    open, close     = None, None

    for positionlower in positions:
      position      = rightdown.Positions.Tag(positionlower)
      pname         = (len(positions) > 1) and self.MakeName(name, position) or name
      ptag          = self.MakeTag(tag, position)
      program       = positions[positionlower]
      pattern       = patterns.InlinePattern(program)
      if program:
        self.allprograms.append((ptag, program))
      if html:
        self.Add(pname, ptag, pattern=pattern, html=html)
      else:
        self.Add(pname, ptag, pattern=pattern)
      if position in (rightdown.POSITION_OPEN, rightdown.POSITION_OPENISH):
        open        = ptag
      elif position in (rightdown.POSITION_CLOSE, rightdown.POSITION_CLOSEISH):
        close       = ptag

    if open and close and self.pairenum is not None:
      if pairhtml:
        self.pairenum.Add(name, tag, html=pairhtml)
      else:
        self.pairenum.Add(name, tag)
      self.allpairs.append((tag, open, close))
