#!/usr/bin/env python

"""
  Add files to an existing Transformation
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s TransID infile' % Script.scriptName,
                                  'Arguments:',
                                  '  infile: ascii file with LFNs',
                                  '  transID: Transformation ID',
                                  '\ne.g: %s 381 Paranal_gamma_North.list' % Script.scriptName,
                                  ]))


Script.parseCommandLine()

from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from CTADIRAC.Core.Utilities.tool_box import read_lfns_from_file

def main():
    args = Script.getPositionalArgs()
    if (len(args) != 2):
      Script.showHelp()

    # get arguments
    transID = args[0]
    infile = args[1]
    infileList = read_lfns_from_file(infile)

    tc = TransformationClient()
    res = tc.addFilesToTransformation(transID, infileList)  # Files added here

    if not res['OK']:
      DIRAC.gLogger.error(res['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice("Successfully added %d files to transformation %s" % (len(infileList), transID))
      DIRAC.exit(0)

if __name__ == "__main__":
  main()
