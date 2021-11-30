#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
import six

# DIRAC imports
from DIRAC.Core.Base import Script
import DIRAC

Script.parseCommandLine(ignoreErrors=True)

from DIRAC import gLogger
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

def main():

  fcc = FileCatalogClient()
  dirac = Dirac()
  resJDL = dirac.getJobJDL(os.environ['JOBID'])

  # get list of input files
  #idata = ['/vo.cta.in2p3.fr/MC/PROD5b/Paranal/gamma/sim_telarray/2446/Log/000xxx/gamma_40deg_180deg_run104___cta-prod5b-paranal_desert-2147m-Paranal-dark.log_hist.tar',
  #'/vo.cta.in2p3.fr/MC/PROD5b/Paranal/gamma/sim_telarray/2446/Log/000xxx/gamma_40deg_180deg_run613___cta-prod5b-paranal_desert-2147m-Paranal-dark.log_hist.tar']

  idata = resJDL['Value']['InputData']
  if isinstance(idata, six.string_types):
    idata = []
    if 'LFN' in resJDL['Value']['InputData']:
      idata.append(resJDL['Value']['InputData'].split('LFN:')[1])
    else:
      idata.append(resJDL['Value']['InputData'])
  else:
    idata = resJDL['Value']['InputData']

  for lfn in idata:
    gLogger.notice("Checking input Log file:\n %s " % lfn)
    file_name = os.path.basename(lfn)
    code = os.system("tar -xvf " + file_name)
    if code!=0:
       gLogger.error("Unable to untar Log file:\n %s" % file_name)
       DIRAC.exit(-1)
    code = os.system("ls scratch" )
    if code!=0:
       gLogger.error("scratch directory not found")
       DIRAC.exit(-1)
    os.system("gunzip -r scratch" )
    res = list(os.popen("grep camera_CTA-LST -r scratch | grep file | wc -l"))
    if res[0].strip()!='4':
      data_lfn = lfn.replace("Log","Data").replace("log_hist.tar","simtel.zst")
      gLogger.error("Buggy Data file:\n %s" % data_lfn)
      gLogger.notice("Setting nsb=-1")
      res = fcc.setMetadata(data_lfn,{'nsb': -1})
      if not res['OK']:
        return res

    code = os.system("rm -Rf scratch")
    if code!=0:
      gLogger.error("Unable to remove scratch directory")
      DIRAC.exit(-1)
    code = os.system("rm " + file_name)
    if code!=0:
     gLogger.error("Unable to remove Log file:\n %s" % file_name)
     DIRAC.exit(-1)

  DIRAC.exit()

if __name__ == '__main__':
  main()
