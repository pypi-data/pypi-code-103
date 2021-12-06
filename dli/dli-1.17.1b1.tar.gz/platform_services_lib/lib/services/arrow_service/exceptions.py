#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

from ..exceptions import ServiceException


class NoFilesInDataset(ServiceException):
    pass


class UnsupportedDatasetFormat(ServiceException):
    pass


class NonParquetFilesInDataset(ServiceException):
    pass


class NonCsvFilesInDataset(ServiceException):
    pass
