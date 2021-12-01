#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import datetime
import logging
import os
from collections import defaultdict, Mapping
from typing import Iterator, Optional, Iterable, Dict, List, NewType
from urllib.parse import urlparse
from dateutil.parser import isoparse
from flask import current_app

try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import inject
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function): # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper

from ...adapters.s3_io_adapters import ServiceIO
from ...handlers.s3_dataset_handler import S3DatasetHandler
from ...handlers.s3_partition_handler import get_partitions_in_filepath, meets_partition_params
from ...services.exceptions import UnsupportedDatasetLocation, UnableToAccessDataset
from ...services.dlc_service import DlcService

logger = logging.getLogger(__name__)

# overwrite this in app.py with your choice of handler e.g.
# injector.binder.bind(DISPATCHER, to=ConsumptionDatasetHandler)
DISPATCHER = NewType('DISPATCHER', S3DatasetHandler)


class FileService:

    __HADOOP_FILES = {
        '_success'
    }

    @inject
    def __init__(
        self,
        dlc_service: DlcService
    ):
        self.dlc_service = dlc_service
        self.stream_handlers = {
            's3': current_app.injector.get(DISPATCHER),
        }
        logger.debug('FileService constructor')

    def __del__(self):
        """Destructor."""
        logger.debug('Destructor called on FileService')

    def get_handler(self, dataset):
        access_denied_message = (
            'You do not have access to this dataset. You must '
            'request access to the dataset\'s package.'
        )
        if 'location' not in dataset['attributes']:
            raise UnableToAccessDataset(details=access_denied_message)

        # If there is a 'location' key in the Catalogue response, then we expect it will contain
        # a type key.
        location_type: str = list(dataset['attributes']['location'].keys())[0].lower()

        if location_type == 'other':
            # Support old Catalogue behaviour where they return 'other' to mean access denied.
            raise UnableToAccessDataset(details=access_denied_message)

        # Retrieve the handler for this location type e.g. if the location is s3 then return the
        # s3 handler.
        if location_type in self.stream_handlers:
            return self.stream_handlers[location_type]
        else:
            supported_locations = ','.join(self.stream_handlers.keys()).lower()

            raise UnsupportedDatasetLocation(
                details=(
                    f'Only {supported_locations} currently '
                    'supports downloads via consumption. '
                    f'{location_type} is not currently supported'
                )
            )

    def get_files_from_datafile(
        self, datafile_id: str,
        paths: Optional[Iterable[str]] = None,
        partitions: Optional[Iterable] = None,
        order_by_latest: Optional[bool] = None,
        skip_hidden_files: Optional[bool] = False,
        skip_special_hadoop_files: Optional[bool] = False,
    ):
        """
        For a dataset_id returns a iterating response of Boto
        ObjectSummary objects. Can return a single file if
        path filter is an absolute path pointing at a specific file

        :param: datafile_id - the id of the datafile
        :kwarg: paths - a partial or complete path to a file or a
                              folder within a datafile
        :kwarg: partitions - a set of conditions to be met in the path
                     on comparison to each key=value pair related by key
                     e.g. `key` > 5 where key=4 in the object path is True
                     e.g. `key` < 4 where key=5 in the object path is False
        """
        logger.debug('get_files_from_datafile')
        datafile = self.dlc_service.get_datafile(datafile_id)
        dataset = self.dlc_service.get_dataset(
            datafile['properties']['datasetId']
        )

        return self._get_files(
            dataset=dataset,
            datafile=datafile,
            paths=paths,
            partitions=partitions,
            order_by_latest=order_by_latest,
            skip_hidden_files=skip_hidden_files,
            skip_special_hadoop_files=skip_special_hadoop_files,
        )

    # TODO merge with _get_files
    def get_files_from_dataset(
        self,
        dataset: Dict,
        paths: Optional[Iterable[str]] = None,
        partitions: Optional[Iterable] = None,
        order_by_latest: Optional[bool] = None,
        skip_hidden_files: Optional[bool] = False,
        skip_special_hadoop_files: Optional[bool] = False,
    ) -> Iterator[ServiceIO]:
        """
        For a dataset_id returns a iterating response of Boto
        ObjectSummary objects. Can return a single file if
        path filter is an absolute path pointing at a specific file

        :param: datafile_id - the id of the datafile
        :kwarg: paths - a partial or complete path to a file or a
                                 folder within a datafile
        :kwarg: partitions - a set of conditions to be met in the path
                         on comparison to each key=value pair related by key
                         e.g. `key` > 5 where key=4 in the object path is True
                         e.g. `key` < 4 where key=5 in the object path is False
        """
        logger.debug(
            'get_files_from_dataset',
        )

        yield from self._get_files(
            dataset=dataset,
            paths=paths,
            partitions=partitions,
            order_by_latest=order_by_latest,
            skip_hidden_files=skip_hidden_files,
            skip_special_hadoop_files=skip_special_hadoop_files,
        )

    def get_partitions_from_dataset(
        self,
        dataset: dict,
    ) -> Dict[str, list]:

        if not isinstance(dataset, Mapping):
            raise TypeError()
        logger.debug('get_partitions_from_dataset')
        partitions: Dict[str, list] = defaultdict(lambda: [])
        all_split = (
            get_partitions_in_filepath(f.path) for f in
            self.get_files_from_dataset(
                dataset,
            )
        )

        for file_path_splits in all_split:
            key_values = file_path_splits

            for k, v in key_values:
                partitions[k].append(v)

        for k in partitions.keys():
            partitions[k] = sorted(list(set(partitions[k])))

        return partitions

    @staticmethod
    def __filter_by_datafile(
        input_paths: Iterator[ServiceIO], datafile: dict
    ) -> Iterator[ServiceIO]:
        logger.debug('filter_by_datafile')
        filter_paths = [
            urlparse(f['path']).path.lstrip('/')
            for f in datafile['properties']['files']
        ]

        yield from FileService.__filter_by_paths(input_paths, filter_paths)

    # XXX Todo optimise this to be called first to filter paths
    # perhaps return some sort of q object?
    @staticmethod
    def __filter_by_paths(
        input_paths: Iterator[ServiceIO], filter_paths
    ) -> Iterator[ServiceIO]:
        logger.debug('filter_by_paths')
        for path in input_paths:
            if any([
                path.path.startswith(p) for p in filter_paths
            ]):
                yield path

    @staticmethod
    def __filter_by_partitions(
        input_paths: Iterator[ServiceIO], partitions
    ) -> Iterator[ServiceIO]:
        logger.debug('filter_by_partitions')
        for path in input_paths:
            if meets_partition_params(path.path, partitions):
                yield path

    def _get_files(
        self,
        dataset: Dict,
        datafile: Optional[Dict] = None,
        paths: Optional[Iterable[str]] = None,
        partitions: Optional[Iterable] = None,
        order_by_latest: Optional[bool] = None,
        skip_hidden_files: Optional[bool] = False,
        skip_special_hadoop_files: Optional[bool] = False,
    ) -> Iterator[ServiceIO]:
        logger.debug(
            '_get_files',
            extra={
                'order_by_latest': order_by_latest,
            }
        )

        handler = self.get_handler(dataset)

        # Common-prefixes level filtering
        result = handler.handle(
            dataset,
        )

        # Note: The order of operations below should be filter out files
        # before doing a sort because sort is expensive and some s3 listings
        # contain a lot of metadata (which is a waste to try to partition
        # or to even find the dates of the S3 files).

        # File-level filters
        if skip_hidden_files:
            logger.debug('skip_hidden_files')
            # [DL-4545][DL-4536] Do not read into files or directories that
            # are cruft from Spark which Spark will ignore on read,
            # e.g. files/dirs starting with `.` or `_` are hidden to Spark.

            def mis_hidden_file(path: str):
                attrs = dataset.get("attributes", None)
                if attrs:
                    content_type = attrs.get("content_type", "Structured")
                else:
                    content_type = "Structured"

                if (
                        path.startswith('.') or
                        path.startswith('_') or
                        (path == 'metadata' and content_type != "Unstructured") or
                        (
                            path.startswith('as_of_') and
                            path.endswith('=latest')
                        )
                ):
                    logger.debug(
                        f"skip_hidden_file: '{path}'",
                        extra={'path': path}
                    )
                    return True
                else:
                    return False

            result = (
                r for r in result
                if not any(mis_hidden_file(p) for p in r.path.split('/'))
            )

        if skip_special_hadoop_files:
            logger.debug('skip_special_hadoop_files')

            def is_special_hadoop_file(path: str):
                if os.path.basename(path).lower() in self.__HADOOP_FILES:
                    logger.warning(
                        f"skip_special_hadoop_file: '{path}'",
                        extra={'path': path}
                    )
                    return True
                else:
                    return False

            result = (
                r for r in result  # type: ignore
                if not is_special_hadoop_file(r.path)
            )

        if datafile:
            # When we are passed a datafile, we only get the files specified
            # in the datafile.
            result = self.__filter_by_datafile(result, datafile)

        if paths:
            result = self.__filter_by_paths(result, paths)

        if partitions:
            result = self.__filter_by_partitions(result, partitions)

        if order_by_latest is None:
            pass
        elif order_by_latest is True:
            result = FileService.order_by_latest(result, direction='desc')
        elif order_by_latest is False:
            result = FileService.order_by_latest(result, direction='asc')

        yield from result

    @staticmethod
    def order_by_latest(input_paths: Iterator[ServiceIO], direction='desc'
                        ) -> Iterator[ServiceIO]:
        reverse = True if direction == 'desc' else False

        logger.debug(
            'order_by_latest',
            extra={
                'direction': direction,
                'reverse': reverse,
            }
        )

        if reverse:
            # Use list so we do not break iterator when we sort.
            input_paths_list: List[ServiceIO] = list(input_paths)
            # Sort in-place to avoid allocating more objects in Python free-list.
            input_paths_list.sort(
                key=FileService._get_created_at,
                reverse=reverse
            )

            return iter(input_paths_list)
        else:
            return input_paths

    @staticmethod
    def _get_created_at(service_io_obj: ServiceIO):
        partitions = {
            k.lower(): v for k, v in dict(
                get_partitions_in_filepath(service_io_obj.path)
            ).items()
        }

        chronological_partitions = {
            'year', 'month', 'day'
        }

        if partitions:
            as_of = next(
                (v for k, v in partitions.items()
                 if k.startswith('as_of_')),
                None
            )

            if as_of:
                try:
                    as_of = isoparse(as_of)
                    return (
                        3,
                        as_of,
                        service_io_obj.path
                    )
                except ValueError:
                    pass

            # If no as_of key, fallback on chronological_partitions
            if any(
                i in chronological_partitions for i in partitions.keys()
            ):
                year = int(partitions.get('year', 1))
                month = int(partitions.get('month', 1))
                day = int(partitions.get('day', 1))

                return (
                    2,
                    datetime.datetime(year, month, day),
                    service_io_obj.path
                )

        # If no partitions order by S3 dateting
        if 'last_modified' in service_io_obj.metadata:
            # Secondary sort to rely on the object's S3 metadata
            # if partitions can not be found
            return (
                1,
                service_io_obj.metadata['last_modified'],
                service_io_obj.path
            )
        else:
            # order by path and hope for the best
            return (
                0,
                # Dummy date
                datetime.datetime.min,
                service_io_obj.path
            )