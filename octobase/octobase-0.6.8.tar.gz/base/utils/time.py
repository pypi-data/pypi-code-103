#!/opt/local/bin/python
# Copyright 2014, Octoboxy LLC.  All Rights Reserved.
''' Functions for working with datetimes and timedeltas. '''

import base
import datetime
import math
import re


def Now():
  ''' Timezone-aware now() '''
  return datetime.datetime.now(base.consts.TIME_UTC)


def LocalTime(dt):
  ''' Converts a datetime to our default timezone. '''
  return dt.astimezone(base.consts.TIME_ZONE)


def EnsureTzInfo(dt, timezone=None):
  ''' Stamps "UTC" on a datetime since we don't know anything better. '''
  timezone        = timezone or base.consts.TIME_UTC
  if dt.tzinfo:
    return dt
  return dt.replace(tzinfo=timezone)


def DateFromDateTime(timestamp):
  ''' Shifts a timestamp to local time, then strips the time part and returns the date. '''
  return LocalTime(timestamp).date()


def DateTimeFromDate(date):
  ''' Promotes a date object into a datetime object by setting the time to high-noon, local time. '''
  timestamp       = datetime.datetime.combine(date, datetime.time(12, 00))
  return EnsureTzInfo(timestamp, timezone=base.consts.TIME_ZONE)


def FormatTimestamp(dt, force_utc=False, force_local=True, limit_granularity=None):
  ''' Returns a nice string representation of the date, time, or datetime. '''
  if not dt:
    return ''

  if type(dt) == datetime.time:
    if limit_granularity == 'minute':
      return dt.strftime('%H:%M %Z')
    return dt.strftime('%H:%M:%S %Z')

  if type(dt) == datetime.date:   # don't use isinstance() because datetime is a date
    if dt <= base.consts.DATE_MIN:
      return 'Dawn of Time'
    if dt >= base.consts.DATE_MAX:
      return 'End of Time'
    return dt.strftime('%Y-%m-%d')

  if dt <= base.consts.DATETIME_MIN:
    return 'Dawn of Time'
  if dt >= base.consts.DATETIME_MAX:
    return 'End of Time'

  if force_utc:
    dt            = dt.astimezone(base.consts.TIME_UTC)
  elif force_local:
    dt            = dt.astimezone(base.consts.TIME_ZONE)

  if limit_granularity == 'date':
    return dt.strftime('%Y-%m-%d')
  if limit_granularity == 'minute':
    return dt.strftime('%Y-%m-%d %H:%M %Z')
  return dt.strftime('%Y-%m-%d %H:%M:%S %Z')


def FormatTimeDelta(td):
  ''' Returns a human-readable string for a datetime.timedelta. '''
  Plural          = lambda x: x != 1 and 's' or ''

  if not td:
    return ''

  frac, seconds   = math.modf(td.total_seconds())
  seconds         = int(seconds)

  minutes         = int(math.floor(seconds / 60))
  seconds         -= minutes * 60

  hours           = int(math.floor(minutes / 60))
  minutes         -= hours * 60

  days            = int(math.floor(hours / 24))
  hours           -= days * 24

  years           = int(math.floor(days / 365))
  days            -= years * 365

  if frac:
    frac          = '.{:03}'.format(int(math.floor(frac * 1000)))
  else:
    frac          = ''

  parts           = []
  if years:
    parts.append('{} year{}'.format(years, Plural(years)))
  if days:
    parts.append('{} day{}'.format(days, Plural(days)))
  if hours or minutes or seconds or frac:
    if parts:
      parts.append('{}:{:02}:{:02}{}'.format(hours, minutes, seconds, frac))
    else:
      if hours:
        parts.append('{} hour{}'.format(hours, Plural(hours)))
      if minutes:
        parts.append('{} minute{}'.format(minutes, Plural(minutes)))
      if seconds or frac:
        if parts:
          parts.append('{} second{}'.format(seconds, Plural(seconds)))
        else:
          parts.append('{}{} second{}'.format(seconds, frac, Plural(seconds)))

  return ', '.join(parts)



def ParseTimestamp(text, force_datetime=False):
  ''' Does our very best to extract a meaningful timestamp from the text string given.

        force_datetime -- calls DateTimeFromDate() if needed
  '''
  _, timestamp    = SplitPathToTextAndTime(text)
  if force_datetime and isinstance(timestamp, datetime.date):
    timestamp     = base.utils.DateTimeFromDate(timestamp)
  return timestamp



def SplitPathToTextAndTime(filepath):
  ''' Given a filepath, we split and return (TEXT, TIME) where:
        TEXT is the textual part of the filename, not counting time or date info (or extension)
        TIME is either a datetime.date or datetime.time object if we can find date/time info in the filepath.
  '''
  def IsSepDigits(str):
    ''' Helper to test if a string is composed entirely of separators or digits. '''
    return str and not str.strip('0123456789-_ .')

  def IsFalseMatch(groups):
    ''' Our regexps, below, have a possible false-match case.  This because we want to be tolerant about
        single-digit date parts, and yet simultaneously allow date strings with no separators at all.
        What happens is '2012/16-framenumber' comes out as '2012', '/1', '6'.  Ergo: if we have a
        single digit part that does NOT begin with a separator, we know we false-matched.
    '''
    for num in (2, 3, 5, 6):
      if num < len(groups) and len(groups[num]) == 1:
        return True
    return False

  filepath      = filepath.replace(':', '.')

  if not filepath:
    return (None, None)

  # Split into path chunks
  chunks        = filepath.split('/')

  # Filename is simply the last (non-empty) chunk
  chunks        = [x for x in chunks if x]
  if not chunks:
    return (None, None)
  filename      = chunks.pop(-1)

  # Strip off ALL extensions (there may be more than one).  Note that timestamps are often encoded
  # into a filename with dots (e.g.: 'Screen Shot 2011-10-09 at 3.10.24 AM.jpg') so we say that extensions
  # may not begin with a digit.
  filename      = filename.strip('.')
  while '.' in filename:
    pos         = filename.rfind('.')
    if filename[pos+1].isdigit():
      break
    filename    = filename[:pos].strip('.')
  if not filename:
    return (None, None)

  # At minimum we want to run the (remaining) filename through our regexps.  If that name begins with
  # digits though, and if the parent chunks are entirely digits or separators, we want to also run
  # variations with up to two parent chunks prefixed in.
  variants      = [filename]
  if filename[0].isdigit():
    if chunks and IsSepDigits(chunks[-1]):
      variants.append(chunks.pop(-1) + '/' + filename)
      if chunks and IsSepDigits(chunks[-1]):
        variants.append(chunks.pop(-1) + '/' + variants[-1])

  # We have two regexps to test -- a datetime and a date
  REGEXP_TIME   = re.compile(r'^(\D*)(\d{4})([\-\._/ ]*\d\d?)([\-\._/ ]*\d\d?)( at| ?[tT]| |/)( ?\d\d?)(\.?\d\d?)(\.?\d\d?)?(\.\d+)? ?([zZ]|[aApP][mM]?)?(.*)$')
  REGEXP_DATE   = re.compile(r'^(\D*)(\d{4})([\-\._/ ]*\d\d?)([\-\._/ ]*\d\d?)(.*)$')
  for variant in variants:
    match       = REGEXP_TIME.match(variant)
    if match and not IsFalseMatch(match.groups()):
      break
    match       = REGEXP_DATE.match(variant)
    if match and not IsFalseMatch(match.groups()):
      break
    match       = None

  if not match:
    return (filename, None)

  groups        = match.groups()

  # Date info is always in groups 1, 2, and 3
  yr            = int(groups[1].strip('-._/ '))
  mo            = int(groups[2].strip('-._/ '))
  dy            = int(groups[3].strip('-._/ '))

  # Time info may be present or not
  have_time     = len(groups) > 5
  if have_time:
    hr, mn, sc, ms = groups[5:9]
    mod         = groups[9]
    tz          = base.consts.TIME_ZONE

    hr          = int(hr.strip(' '))
    mn          = int(mn.strip('.'))
    sc          = sc is not None and int(sc.strip('.')) or 0
    ms          = ms is not None and int(ms.strip('.')) or 0

    if mod:
      mod       = mod.upper()
      if  mod in ('P', 'PM'):
        hr        += 12
      elif mod == 'Z':
        tz      = base.consts.TIME_UTC
      elif mod not in ('A', 'AM'):
        raise base.errors.TimezoneParsingNotImpl(filename)

  # Build the date
  try:
    if have_time:
      while ms > 999999:
        ms      = round(ms / 10)
      time      = datetime.datetime(yr, mo, dy, hr, mn, sc, ms)
      if tz:
        time    = tz.localize(time)
    else:
      time      = datetime.date(yr, mo, dy)
  except ValueError as e:
    return (filename, None)


  # The text part is then just prefix text plus suffix text
  text          = (groups[0] + ' ' + groups[-1]).strip('-._/ ')
  if not text:
    text        = None

  return (text, time)
