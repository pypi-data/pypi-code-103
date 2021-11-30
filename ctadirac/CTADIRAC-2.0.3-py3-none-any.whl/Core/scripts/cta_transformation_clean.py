#!/usr/bin/env python

"""
  Clean an existing Transformation
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s transID' % Script.scriptName,
                                  'Arguments:',
                                  '  transID: Transformation ID',
                                  '\ne.g: %s 381' % Script.scriptName,
                                  ]))


Script.parseCommandLine()

from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

def main():
    args = Script.getPositionalArgs()
    if (len(args) != 1):
      Script.showHelp()

    # get arguments
    transID = args[0]

    tc = TransformationClient()
    res = tc.cleanTransformation(transID)

    if not res['OK']:
      DIRAC.gLogger.error(res['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice("Successfully cleaned transformation %s" % transID)
      DIRAC.exit(0)

if __name__ == "__main__":
  main()