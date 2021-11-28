#!/opt/local/bin/python
# Copyright 2014, Octoboxy LLC.  All Rights Reserved.
''' Useful functions unlike any other. '''

import base
import os


def ReverseReadLines(file, buf_size=8192):
  ''' A proper memory-buffered generator to read the lines of a text file in reverse order.
      Thanks http://stackoverflow.com/questions/2301789/read-a-file-in-reverse-order-using-python
  '''
  segment         = None
  offset          = 0
  file.seek(0, os.SEEK_END)
  file_size       = remaining_size = file.tell()
  while remaining_size > 0:
    offset        = min(file_size, offset + buf_size)
    file.seek(file_size - offset)
    buffer        = file.read(min(remaining_size, buf_size))
    remaining_size -= buf_size
    lines         = buffer.split('\n')
    # the first line of the buffer is probably not a complete line so
    # we'll save it and append it to the last line of the next buffer
    # we read
    if segment is not None:
      # if the previous chunk starts right from the beginning of line
      # do not concact the segment to the last line of new chunk
      # instead, yield the segment first
      if buffer[-1] != '\n':
        lines[-1] += segment
      else:
        yield segment
    segment       = lines[0]
    for index in range(len(lines) - 1, 0, -1):
      if len(lines[index]):
        yield lines[index]
  # Don't yield None if the file was empty
  if segment is not None:
    yield segment



class StopWatch(object):
  ''' STDERR-logging timer for use in figuring out where your code is slow. '''
  def __init__(self, name='STOPWATCH'):
    self.name       = base.utils.Slugify(name).upper()
    self.laps       = [base.utils.Now()]
    self.lapnames   = []

  def Base(self):
    return self.laps[0]

  def Read(self):
    return base.utils.Now() - self.laps[-1]

  def Lap(self, lapname=None, keep_history=True):
    now             = base.utils.Now()
    prior           = self.laps[-1]
    if keep_history:
      self.laps.append(now)
      self.lapnames.append(lapname)
    else:
      self.laps     = [now]
    return now - prior

  def Log(self):
    base.utils.Log(self.name, str(self.Read()))

  def LapAndLog(self, lapname='Lap'):
    base.utils.Log(self.name, '{!s} {!s}'.format(self.Lap(), lapname))

  def LogAllLaps(self):
    base.utils.Log(self.name, 'Lap times:\n  ' + '\n  '.join(self.FormatLaps()) + '\n')

  def FormatLaps(self):
    times           = []
    for i in range(1, len(self.laps)):
      times.append((self.laps[i] - self.laps[i-1], self.lapnames[i-1] or ''))
    return ['{!s} {!s}'.format(x, y) for x, y in times]

