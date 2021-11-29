#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
from multiprocessing import Pool

# DIRAC imports
from DIRAC.Core.Base import Script

Script.setUsageMessage("""
Bulk upload of a list of local files from the current directory to a Storage Element
Usage:
   %s <ascii file with lfn list> <SE>
""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

args = Script.getPositionalArgs()
if len(args) > 1:
  infile = args[0]
  SE = args[1]
else:
  Script.showHelp()

from DIRAC import gLogger
from DIRAC.Interfaces.API.Dirac import Dirac
from CTADIRAC.Core.Utilities.tool_box import read_lfns_from_file

def main():
  infileList = read_lfns_from_file(infile)
  p = Pool(10)
  p.map(addfile, infileList)

def addfile(lfn):
  dirac = Dirac()
  res = dirac.addFile(lfn, os.path.basename(lfn), SE)
  if not res['OK']:
    gLogger.error('Error uploading file', lfn)
    return res['Message']

if __name__ == '__main__':
  main()
