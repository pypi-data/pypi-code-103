#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC.Core.Base import Script

Script.setUsageMessage("""
Bulk removal of a list of files
Usage:
   %s <ascii file with lfn list>

""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from CTADIRAC.Core.Utilities.tool_box import read_lfns_from_file

fc = FileCatalog()

def removeFile(lfn):
  res = fc.removeFile(lfn)
  if not res['OK']:
    gLogger.error('Error removing file', lfn)
    return res['Message']


def main():
  args = Script.getPositionalArgs()
  if len(args) > 0:
    infile = args[0]
  else:
    Script.showHelp()

  infileList = read_lfns_from_file(infile)
  p = Pool(10)
  p.map(removeFile, infileList)

if __name__ == '__main__':
  main()
