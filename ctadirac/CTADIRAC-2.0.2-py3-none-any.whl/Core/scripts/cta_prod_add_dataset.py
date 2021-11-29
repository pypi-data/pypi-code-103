#!/usr/bin/env python

__RCSID__ = "$Id$"

import json

import DIRAC
from DIRAC.Core.Base import Script
from DIRAC import gLogger


Script.setUsageMessage("""
Add a dataset from a query specified in a json file, e.g.:

{"MCCampaign': "PROD5b",
"particle": "proton",
"site": "Paranal"}

Usage:
   %s <datasetName> <json file with dataset query dict>
""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

def main():
  fc = FileCatalogClient()
  argss = Script.getPositionalArgs()
  if len(argss) == 2:
    datasetName = argss[0]
    inputJson = argss[1]
  else:
    Script.showHelp()

  # read the meta data query from json file
  f = open(inputJson)
  MDdict = json.load(f)
  f.close()

  datasetPath = '/' + datasetName
  res = (fc.addDataset({datasetPath: MDdict}))

  if not res['OK']:
    gLogger.error("Failed to add dataset %s: %s" % (datasetName, res['Message']))
    DIRAC.exit(-1)

  if datasetName in res['Value']['Failed']:
    gLogger.error("Failed to add dataset %s: %s" % (datasetName, res['Value']['Failed'][datasetName]))
    DIRAC.exit(-1)

  gLogger.notice("Successfully added dataset", datasetName)
  DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()