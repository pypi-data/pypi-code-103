#!/usr/bin/env python

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base import Script

Script.setUsageMessage("""
Get statistics for datasets corresponding to the dataset name (may contain wild card)
if no dataset is specified it gives the list of available datasets
Usage:
   %s <dataset>

""" % Script.scriptName)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


def print_dataset_list(dataset_list):
  dataset_list.sort()
  print('\nAvailable datasets are:\n')
  for dataset_name in dataset_list:
    gLogger.notice(dataset_name)
  gLogger.notice('\n')


def get_list_of_datasets(tag=''):
  fc = FileCatalogClient()
  dataset_tag = '*%s*' % tag
  res = fc.getDatasets(dataset_tag)
  if not res['OK']:
    gLogger.error(res['Message'])
    DIRAC.exit(-1)
  dataset_dict = res['Value']
  dataset_list = list()
  for dataset_name in dataset_dict['Successful'][dataset_tag].keys():
    dataset_list.append(dataset_name)
  return dataset_list


def get_dataset_info(dataset_name):
  fc = FileCatalogClient()
  res = fc.getDatasets(dataset_name)
  if not res['OK']:
    gLogger.error("Failed to get datasets")
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

  if len(argss) == 0:
    dataset_list = get_list_of_datasets()
    print_dataset_list(dataset_list)
    DIRAC.exit()
  elif len(argss) == 1:
    dataset_name = argss[0]
    dataset_list = list()
    if dataset_name.find('*') > 0:
      dataset_list = get_list_of_datasets(dataset_name)
    else:
      dataset_list.append(dataset_name)
    print_dataset_list(dataset_list)

  # Results
  gLogger.notice('Datasets details')
  if len(dataset_list) == 1:
    name, n_files, size, mq = get_dataset_info(dataset_list[0])
    gLogger.notice('MetaQuery')
    gLogger.notice(str(mq))
  gLogger.notice('|_. Name |_. N files |_. Size(TB) |')
  dataset_list.sort()
  total_size = 0.
  total_n_files = 0
  for dataset_name in dataset_list:
    name, n_files, size, mq = get_dataset_info(dataset_name)
    # # convert total size in TB
    size_TB = size / 1e12
    gLogger.notice('|%s|%d|%.2f|' % (name, n_files, size_TB))
    total_size += size_TB
    total_n_files += n_files
  gLogger.notice('| Total | %d | %.2f |' % (total_n_files, total_size))
  DIRAC.exit()

if __name__ == '__main__':
  main()