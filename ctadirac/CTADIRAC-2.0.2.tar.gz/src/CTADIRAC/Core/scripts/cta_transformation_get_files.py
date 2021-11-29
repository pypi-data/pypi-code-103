#!/usr/bin/env python

"""
  Get the files attached to a transformation and optionally update the file status
  Extension of dirac-transformation-get-files with additional options:
  --FileStatus : selection based on the FileStatus
  --TaskStatus : selection based on the TaskStatus
  --setFileStatus : update the FileStatus of the selected files to a new Status
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base import Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

from DIRAC.Core.Base.Script import parseCommandLine
parseCommandLine()

def main():

  Script.registerSwitch('', 'TransID=', '   transformation ID')
  Script.registerSwitch('', 'FileStatus=', '    file status')
  Script.registerSwitch('', 'TaskStatus=', '    task status')
  Script.registerSwitch('', 'setFileStatus=', '    new file status')

  transID = None
  fileStatus = None
  taskStatus = None
  newFileStatus = None

  for switch in Script.getUnprocessedSwitches():
    if switch[0] == 'TransID':
      try:
        transID = int(switch[1])
      except Exception:
        gLogger.fatal('Invalid transID', switch[1])
    elif switch[0] == 'FileStatus':
      fileStatus = switch[1].capitalize()
    elif switch[0] == 'TaskStatus':
      taskStatus = switch[1].capitalize()
    elif switch[0] == 'setFileStatus':
      newFileStatus = switch[1].capitalize()


  if not transID:
    Script.showHelp(exitCode=2)

  tc = TransformationClient()

  condDict = {'TransformationID': transID}

  if fileStatus:
    condDict.update({'Status': fileStatus})

  if taskStatus:
    res = tc.getTransformationTasks({'TransformationID': transID, 'ExternalStatus': taskStatus})

    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(2)

    if len(res['Value']) == 0:
      gLogger.notice("No tasks selected for transformation %s with status %s" % (transID, taskStatus))

    taskIDs = []
    for task in res['Value']:
      taskIDs.append(task["TaskID"])

    condDict.update({'TaskID': taskIDs})

  res = tc.getTransformationFiles(condDict)

  if not res['OK']:
    DIRAC.gLogger.error(res['Message'])
    DIRAC.exit(2)

  if len(res['Value']) == 0:
    gLogger.notice("No files selected for transformation %s with status %s" % (transID, fileStatus))

  transFiles = []
  for transfile in res['Value']:
    transFiles.append(transfile['LFN'])
    gLogger.notice(transfile['LFN'])

  if newFileStatus:
    res = tc.setFileStatusForTransformation(transID, newLFNsStatus=newFileStatus, lfns=transFiles)
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(2)
    gLogger.notice(" %d files set to %s status" % (len(transFiles), newFileStatus))

if __name__ == "__main__":
  main()