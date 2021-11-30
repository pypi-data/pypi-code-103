#!/usr/bin/env python
'''
Move a dataset distributed on a number of production SEs
('DESY-ZN-Disk', 'LPNHE-Disk', 'CNAF-Disk', 'CYF-STORM-Disk','LAPP-Disk', 'CEA-Disk', 'CC-IN2P3-Disk', 'LANCASTER-Disk', 'POLGRID-Disk')
to a given SE to be passed as an argument, e.g. CC-IN2P3-Tape

    J. Bregeon, L. Arrabito November 2020
    bregeon@in2p3.fr, arrabito@in2p3.fr
'''

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base import Script
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from DIRAC.TransformationSystem.Utilities.ReplicationTransformation import createDataTransformation


Script.setUsageMessage(
  '\n'.join(
      [
          __doc__.split('\n')[1],
          'Usage:',
          '  %s <dataset name> <dest SE>' %
          Script.scriptName,
          'Optional arguments:',
          '  <group size>: size of the transformation (default=1)',
          '  <tag>: tag added to the transformation name',
          '\n\ne.g: %s Prod4_Paranal_gamma_North_20deg_SSTOnly_MC0 CC-IN2P3-Tape 100 v1' %
          Script.scriptName,
      ]))

Script.parseCommandLine(ignoreErrors=True)

def get_dataset_info(dataset_name):
  """ Return essential dataset information
      Name, number of files, total size and meta query
  """
  fc = FileCatalogClient()
  res = fc.getDatasets(dataset_name)
  if not res['OK']:
    gLogger.error(res['Message'])
    DIRAC.exit(-1)
  dataset_dict = res['Value']
  res = dataset_dict['Successful'][dataset_name][dataset_name]
  number_of_files = res['NumberOfFiles']
  meta_query = res['MetaQuery']
  total_size = res['TotalSize']
  return (dataset_name, number_of_files, total_size, meta_query)


#########################################################
def main():
  argss = Script.getPositionalArgs()
  if len(argss) < 2:
    Script.showHelp()
  dataset_name = argss[0]
  dest_se = argss[1]
  extra_tag = ""
  group_size = 1
  if len(argss) > 2:
    group_size = argss[2]
  if len(argss) == 4:
    extra_tag = '_' + argss[3]

  # Check input data set information
  name, n_files, size, meta_query = get_dataset_info(dataset_name)
  gLogger.notice('Found dataset %s with %d files.' % (name, n_files))
  gLogger.notice(meta_query)
  # choose a metaKey
  for k,v in meta_query.items():
    meta_key = k
    meta_value = v
  tag = dataset_name + extra_tag

  do_it = True
  # To do: replace hard coded SE with SE read from CS
  source_se = ['DESY-ZN-Disk', 'LPNHE-Disk', 'CNAF-Disk', 'CYF-STORM-Disk',
             'LAPP-Disk', 'CEA-Disk', 'CC-IN2P3-Disk', 'POLGRID-Disk', 'LANCASTER-Disk']

  # create Transformation
  res = createDataTransformation(flavour='Moving',
                                     targetSE=dest_se,
                                     sourceSE=source_se,
                                     metaKey=meta_key,
                                     metaValue=meta_value,
                                     extraData=meta_query,
                                     extraname=tag,
                                     groupSize=int(group_size),
                                     plugin='Broadcast',
                                     tGroup=None,
                                     tBody=None,
                                     enable=do_it,
                                     )
  if not res['OK']:
    gLogger.error(res["Message"])
    DIRAC.exit(-1)

  DIRAC.exit()

#########################################################
if __name__ == '__main__':
  main()