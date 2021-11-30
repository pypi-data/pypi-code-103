#!/usr/bin/env python

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage("""
Remove a given dataset

Usage:
   %s <datasetName>
""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

def main():

    argss = Script.getPositionalArgs()
    fc = FileCatalogClient()

    if len(argss) == 1:
      datasetName = argss[0]
    else:
      Script.showHelp()

    result = fc.removeDataset(datasetName)

    if not result['OK']:
      gLogger.error("Failed to remove dataset %s: %s" % (datasetName, result['Message']))
    else:
      gLogger.notice("Successfully removed dataset", datasetName)
      DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()