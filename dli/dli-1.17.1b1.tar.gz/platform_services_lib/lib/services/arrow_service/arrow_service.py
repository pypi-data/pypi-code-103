#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import logging
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import inject
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function): # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper
from typing import Iterator, Dict, Any, Optional, Iterable

from ..consumption_service import FileService
from ..dlc_service import DlcService
from ..arrow_service.handlers.parquet import ParquetHandler
from ..arrow_service.handlers.csv import CsvHandler
from ..arrow_service.exceptions import UnsupportedDatasetFormat


class ArrowService:

    logger = logging.getLogger(__name__)

    @inject
    def __init__(
        self,
        file_service: FileService,
        dlc_service: DlcService,
        **kwargs,
    ):
        self.file_service = file_service
        self.dlc_service = dlc_service

        self.format_handlers: Dict[str, Any] = {
            'parquet': ParquetHandler,
            'csv': CsvHandler
        }

        self.logger.debug(
            'arrow service init',
        )

    # XXX TODO move into dataset class
    def _get_dataset_handler(self, dataset):
        # TODO cache get dataset calls. Each one takes roughly 250ms.
        # Perhaps provide some sort of OO interface like Dataset.from_id()
        # that would keep a class registry of datasets currently loaded.

        data_format = dataset['attributes']['data_format'].lower()
        dataset_name = dataset['attributes']['name']
        dataset_id = dataset['id']

        self.logger.debug(
            'Dataset in handler',
            extra={
                'dataset_name': dataset_name,
                'dataset_id': dataset_id,
                'data_format': data_format,
            }
        )

        try:
            handler_cls = self.format_handlers[data_format]
        except KeyError as e:
            supported_formats = ','.join(self.format_handlers.keys()).lower()
            raise UnsupportedDatasetFormat(
                details=(
                    f'Only {supported_formats} currently '
                    f'supports dataframe streaming via consumption. The '
                    f'dataset {dataset_id} - {dataset_name} is of type: '
                    f'{data_format} and can not be streamed.'
                )
            ) from e

        return handler_cls

    def dataset_to_ipc_arrow_stream(
        self,
        dataset: Dict,
        nrows=None,
        partitions: Optional[Iterable] = None,
        order_by_latest: Optional[bool] = None,
    ) -> Iterator[bytes]:

        self.logger.debug(
            'dataset_to_ipc_arrow_stream',
        )
        # If order_by_latest is True or False then the files should be
        # returned ordered.

        files = self.file_service.get_files_from_dataset(
            dataset, partitions=partitions, order_by_latest=order_by_latest,
            # Hidden files can be needless metadata
            skip_hidden_files=True,
            skip_special_hadoop_files=True,
        )

        handler = self._get_dataset_handler(dataset)
        yield from handler(files=files, order_by_latest=order_by_latest).\
            handle(nrows=nrows)
