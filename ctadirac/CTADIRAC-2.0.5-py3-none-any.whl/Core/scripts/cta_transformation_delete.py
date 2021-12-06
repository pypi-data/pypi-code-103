#!/usr/bin/env python

"""
  Delete a transformation or a list of transformations
"""

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s transID' % Script.scriptName,
                                  '\ne.g: %s 381,382' % Script.scriptName,
                                  'Arguments:',
                                  '  list of transID comma separated',
                                  '  a file containing a list of transID (comma-separated on each line)'
                                  ]))


Script.parseCommandLine()

from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

def main():
    args = Script.getPositionalArgs()
    if (len(args) != 1):
      Script.showHelp()

    # get arguments
    transIDs = []
    for arg in args[0].split(','):
      if os.path.exists(arg):
        lines = open(arg, 'rt').readlines()
        for line in lines:
          for transID in line.split(','):
            transIDs += [int(transID.strip())]
      else:
        transIDs.append(int(arg))

    tc = TransformationClient()

    for transID in transIDs:
      res = tc.deleteTransformation(transID)
      if not res['OK']:
        DIRAC.gLogger.error('Failed to delete transformation %s: %s' % (transID, res['Message']))
        continue
      else:
        DIRAC.gLogger.notice("Successfully deleted transformation %s" % transID)

    DIRAC.exit(0)

if __name__ == "__main__":
  main()