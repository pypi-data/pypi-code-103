#!/usr/bin/env python

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage("""
Update a given dataset

Usage:
   %s <dataset>
""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

def main():
    argss = Script.getPositionalArgs()

    fc = FileCatalogClient()

    if len(argss) > 0:
      datasetName = argss[0]
    else:
      Script.showHelp()

    result = fc.updateDataset(datasetName)

    if not result['OK']:
      gLogger.error("Failed to update dataset %s: %s" % (datasetName, result['Message']))
      DIRAC.exit(-1)
    else:
      gLogger.notice("Successfully updated dataset", datasetName)
      DIRAC.exit()

if __name__ == '__main__':
  main()
