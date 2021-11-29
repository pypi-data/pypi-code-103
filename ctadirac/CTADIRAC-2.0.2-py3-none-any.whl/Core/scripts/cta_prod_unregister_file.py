#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC.Core.Base import Script

Script.setUsageMessage("""
Bulk removal of a list of files from the catalog
Usage:
   %s <ascii file with lfn list>

""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from CTADIRAC.Core.Utilities.tool_box import read_lfns_from_file

fc = FileCatalog()

def unregisterFile(lfn):
  res = fc.removeFile(lfn)
  if res['OK']:
    if 'Failed' in res['Value']:
      if lfn in res['Value']['Failed']:
        gLogger.error(res['Value']['Failed'][lfn])
      elif lfn in res['Value']['Successful']:
        gLogger.notice("Successfully removed from the catalog", lfn)
      else:
        gLogger.error("Unexpected error result", res['Value'])
    else:
      gLogger.notice("Successfully removed from the catalog", lfn)
  else:
    gLogger.error("Failed to remove file from the catalog:", res['Message'])

  if not res['OK']:
    gLogger.error(res['Message'])


def main():
  args = Script.getPositionalArgs()
  if len(args) > 0:
    infile = args[0]
  else:
    Script.showHelp()

  infileList = read_lfns_from_file(infile)
  p = Pool(10)
  p.map(unregisterFile, infileList)

if __name__ == '__main__':
  main()