#!/opt/local/bin/python
# Copyright 2014, Octoboxy LLC.  All Rights Reserved.
''' Helpers for logging to console. '''

import base
import logging
import sys
import traceback


def Log(tag, message, level=logging.INFO, **extra):
  ''' Logs a message to console.  The "tag" should be a short label for the type of log message. '''
  if base.utils.django.available:
    from django.conf  import settings
    tag           = tag and '.'.join((settings.SERVER_NAME, tag.lower())) or settings.SERVER_NAME
    logging.getLogger(tag).log(level, message or '', extra=extra)
  else:
    things        = [x for x in (tag, message) if x]
    sys.stderr.write(' '.join(things) + '\n')



def LogTraceback(error=None, limit=12):
  ''' Logs a stack trace to the console. '''
  exc_type, exc_value, exc_traceback = error and sys.exc_info() or (None, None, None)
  limit           += 1
  raw             = exc_traceback and traceback.extract_tb(exc_traceback, limit=limit) or traceback.extract_stack(limit=limit)
  lines           = traceback.format_list(raw)
  if lines and not exc_traceback:
    lines         = lines[:-1]
  if lines:
    Log('TRACEBACK', '\n' + '\n'.join(lines))


def LogException(exception):
  ''' Logs an exception to the console. '''
  last            = traceback.extract_tb(exception.__traceback__)[-1]
  filename        = last.filename
  if base.utils.django.available:
    from django.conf  import settings
    if filename.startswith(settings.FILEPATH_CODE):
      filename      = filename[len(settings.FILEPATH_CODE):].lstrip('/')
  text            = str(exception).replace('\n', '\n . ')
  base.utils.Log(
      'EXCEPTION', '{filename}:{lineno}\n - {line}\n - {text}'.format(
          filename=filename, lineno=last.lineno, line=last.line, name=last.name, text=text),
      level=logging.WARN)


def XYZZY(*messages):
  ''' Logs a debug message to the console.

      The function name "XYZZY" is chosen to be easy to search for in a codebase,
      to help reduce debug code being committed into production.
  '''
  if not messages:
    Log('XYZZY', None)
  elif len(messages) == 1:
    Log('XYZZY', str(messages[0]))
  else:
    message       = ''
    for i in range(len(messages)):
      message     = message + '\n {:2d}: '.format(i) + str(messages[i]).rstrip()
    Log('XYZZY', message)
