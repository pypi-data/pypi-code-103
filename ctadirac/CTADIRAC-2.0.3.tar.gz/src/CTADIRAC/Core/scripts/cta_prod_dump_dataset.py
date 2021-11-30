#!/usr/bin/env python

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script
from DIRAC import gLogger

Script.setUsageMessage("""
Dump in a file the list of PROD3 files for a given dataset

Usage:
   %s <dataset>
""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

def main():

  argss = Script.getPositionalArgs()
  fc = FileCatalogClient()

  if len(argss) > 0:
    datasetName = argss[0]
  else:
    Script.showHelp()

  result = fc.getDatasetFiles(datasetName)

  if not result['OK']:
    gLogger.error("Failed to get files for dataset:", result['Message'])
    DIRAC.exit(-1)
  else:
    lfnList = result['Value']['Successful'][datasetName]

    f = open(datasetName + '.list', 'w')
    for lfn in lfnList:
      f.write(lfn + '\n')
    f.close()
    gLogger.notice('%d files have been put in %s.list' % (len(lfnList), datasetName))
    DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()