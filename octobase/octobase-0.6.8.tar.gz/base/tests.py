#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.
'''
  This module *should* include lots of cute test cases for most of our utils.
  Instead we have one single test case for our most complex util.

  For many more test cases, see rightdown/tests.py

  It is extremely unlikely the rightdown tests can pass if our fundamentals
  are broken.
'''

import base
import datetime


class SplitPathToTextAndTimeTest(base.TestCase):
  ''' Tests our ability to parse timestamps from filepaths. '''

  CASES             = [
      ('abcde:/',                                                 'abcde',            None),
      ('2012:/01-02 - Max.min',                                   'Max',              datetime.date(2012, 1, 2)),
      ('abcde:/Foo/20140225 - 8633 Miles/',                       '8633 Miles',       datetime.date(2014, 2, 25)),
      ('abcde:/Foo/2012-FrameNumber.jpg.lrbak',                   '2012-FrameNumber', None),
      ('abcde:/Foo/2012/16-FrameNumber.jpg',                      '16-FrameNumber',   None),
      ('abcde:/Foo/2012/08/16-EventName.jpg',                     'EventName',        datetime.date(2012, 8, 16)),
      ('abcde:/Foo/2012/08/16 - EventName.jpg',                   'EventName',        datetime.date(2012, 8, 16)),
      ('abcde:/Foo/2012 - 08/16 - EventName.jpg',                 'EventName',        datetime.date(2012, 8, 16)),
      ('abcde:/Foo/2000-2004 - Xyz/',                             '2000-2004 - Xyz',  None),
  ]

  if base.consts.TIME_ZONE:
    CASES.extend([
      ('abcde:/Foo/Screen Shot 2012-9-4 at 1.6.44 AM.jpg',        'Screen Shot',      base.consts.TIME_ZONE.localize(datetime.datetime(2012, 9,  4,  1,  6, 44))),
      ('abcde:/Foo/Screen Shot 2012-9-4 at 1.13.44 PM.jpg',       'Screen Shot',      base.consts.TIME_ZONE.localize(datetime.datetime(2012, 9,  4, 13, 13, 44))),
      ('abcde:/Foo/2012-01-26 21.22.06.jpg',                      None,               base.consts.TIME_ZONE.localize(datetime.datetime(2012, 1, 26, 21, 22,  6))),
      ('abcde:/Foo/2012-01-26/21.22.06.jpg',                      None,               base.consts.TIME_ZONE.localize(datetime.datetime(2012, 1, 26, 21, 22,  6))),
      ('abcde:/Foo/20120816T010203.456Z.jpg',                     None,               base.consts.TIME_UTC.localize(datetime.datetime(2012, 8, 16, 1, 2, 3, 456))),
      ('abcde:/Foo/20120816T010203.jpg',                          None,               base.consts.TIME_ZONE.localize(datetime.datetime(2012, 8, 16, 1, 2, 3))),
      ('abcde:/Foo/20120816T0102.jpg',                            None,               base.consts.TIME_ZONE.localize(datetime.datetime(2012, 8, 16, 1, 2))),
      ('2021-03-23T15:55:15.574494Z',                             None,               base.consts.TIME_UTC.localize(datetime.datetime(2021, 3, 23, 15, 55, 15, 574494))),
      ('2020-08-17T01:05:08.7733076Z',                            None,               base.consts.TIME_UTC.localize(datetime.datetime(2020, 8, 17, 1, 5, 8, 773308))),
  ])

  def Run(self):
    for (src, stext, stime) in self.CASES:
      (rtext, rtime)  = base.utils.SplitPathToTextAndTime(src)
      passed          = stext == rtext and stime == rtime
      message         = '{}  -->  {!s:32} {!s}'.format(base.utils.PadString(src, 55), rtext, rtime)
      if not passed:
        message       = message + '  EXPECTED:  {!s:32} {!s}'.format(stext, stime)
      self.LogResult(passed, message)
