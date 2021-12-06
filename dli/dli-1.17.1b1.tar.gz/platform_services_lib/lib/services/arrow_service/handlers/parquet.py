#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import itertools
import os
import logging
import dataclasses
import sys
import numpy
import pyarrow as pa
from typing import Optional, Iterator, List
from pyarrow import (
    RecordBatchStreamWriter, RecordBatch
)
from pyarrow.lib import ArrowException
from pyarrow.parquet import ParquetFile

from ...arrow_service.exceptions import (NoFilesInDataset, NonParquetFilesInDataset)
from ...arrow_service.handlers.dequeue_file import DequeueFile
from ...arrow_service.handlers.stream_errors import handle_arrow_stream_errors
from ....services.exceptions import ServiceException, SchemaMismatchException
from ....adapters.s3_io_adapters import ServiceIO


@dataclasses.dataclass
class Config:
    dd_profiler_enabled: bool = \
        True if os.environ.get('DDTRACE_PROFILER_ENABLED', False) == 'True' \
        else False
    # Overridden in tests to False for ease of testing.
    # In the prod code this is True so that we can free
    # memory as soon as possible.
    close_s3_files: bool = True


class ParquetHandler:

    logger = logging.getLogger(__name__)

    def __init__(self, files: Iterator[ServiceIO],
                 order_by_latest: Optional[bool] = True,
                 **kwargs):
        self.config = Config(**kwargs)

        self.logger.debug(
            'ParquetHandler init',
            extra={
                'config': dataclasses.asdict(self.config),
                'order_by_latest': order_by_latest,
            }
        )
        initial_file = None
        self.initial_file_path = 'not set'

        try:

            if order_by_latest is True:
                # The parquet schema handling depends on us knowing which
                # is the latest .parquet file. The list of files has to
                # be ordered in some way (ascending or descending),
                # it cannot be un-ordered.
                self.logger.debug(
                    'Use the schema from the first file in the list.'
                )
            else:
                # Use the schema from the first file in the list. This
                # will trigger a listing of the files so will be slower
                # to get the first bytes of data back to the client.

                # For the case of order_by_latest None, the default of S3
                # seems to be to return sorted ascending alphabetically,
                # ASSUMPTION this may be close enough. If not, we will have
                # to change the default in dataframe/views.py from None to
                # either True or False.
                self.logger.debug(
                    'Use the schema from the last file in the list.'
                )

                # TODO for the additive schema we need to know the final
                #  file and will use that as the schema for the whole
                #  response. We need to cast to type List to action the
                #  iterator so we can flip the list. Alternative to
                #  caching the whole list is to instead cache only the
                #  S3File of the last file and process that file
                #  immediately (so nginx is able to return quickly),
                #  reading the rest of the files straight from the S3
                #  list not from cache and therefore we can keep `files`
                #  as type iterator. This would also require a crawler to
                #  populate cache with the latest as sorting takes time.
                files = iter(reversed(list(files)))

            # This will raise StopIteration if there are no files in the dataset.
            initial_file = next(files)

            # First time only we get the schema. Unfortunately we need to do
            # this upfront as we need to know the schema before going into the
            # RecordBatchStreamWriter loop.
            self.initial_file_path = initial_file.path
            self.logger.debug(
                'initial_file_path',
                extra={
                    'path': self.initial_file_path,
                }
            )
            self.__validate_file_extension(initial_file)

            initial_parquet_file: ParquetFile = initial_file. \
                to_parquet_file()

        except StopIteration as e:
            message = 'No data in dataset. Unable to stream.'
            self.logger.info(message)
            raise NoFilesInDataset(message) from e

        except (OSError, UnicodeDecodeError, ArrowException) as e:
            message = 'Error for initial file. ' \
                      'Unable to stream.'
            self.logger.warning(
                message,
                exc_info=e,
                extra={'path': self.initial_file_path}
            )
            raise NonParquetFilesInDataset(
                'Non parquet file found in dataset. Path: '
                f'{self.initial_file_path}'
            ) from e

        except NonParquetFilesInDataset:
            raise

        except Exception as e:
            message = 'The file is corrupt, ' \
                      'not a .parquet like file or cannot be read. ' \
                      'Please report the problem to the datalake ' \
                      'platform team at DataLake-Support_L1@ihsmarkit.com. ' \
                      'Please include the full error message including ' \
                      'the request_id.'
            self.logger.exception(message)
            raise ServiceException(message) from e

        # Publicly accessed

        self.schema: pa.Schema = initial_parquet_file.schema.to_arrow_schema()

        self.logger.debug(
            'Parquet columns mapped to pyarrow schema names',
            extra={
                'schema_names': self.schema.names
            }
        )
        self.logger.info(
            'Parquet columns mapped to pyarrow schema types',
            extra={
                'schema_names': self.schema.types
            }
        )

        if order_by_latest is True:
            self._files = itertools.chain([initial_file], files)
        else:
            # The list had been flipped from ascending to descending,
            # so now flip it back. This is clunky and would be better if
            # we only cached the initial schema file.
            self._files = itertools.chain(
                reversed(list(files)),
                [initial_file]
            )

    def __validate_file_extension(self, s3_file: ServiceIO):
        if not s3_file.path.endswith('.parquet'):
            self.logger.warning(
                'Non parquet file found in dataset.',
                extra={
                    'path': s3_file.path,
                }
            )
            raise NonParquetFilesInDataset(
                f'Non parquet file found in dataset. Path: {s3_file.path}'
            )

    @staticmethod
    def _validate_file_size(s3_file: ServiceIO):
        """File size must be greater than zero."""
        if hasattr(s3_file, 'size'):
            return s3_file.size > 0
        else:
            return False

    def _get_record_batches_from_files(self) -> Iterator[RecordBatch]:
        for file_number, s3_file in enumerate(self._files):
            extra_log = {'file_number': file_number, 'path': s3_file.path}

            if not self._validate_file_size(s3_file):
                # Skip zero size files.
                self.logger.warning(
                    'File has been skipped, Parquet file size is 0 bytes.',
                    extra=extra_log
                )
                if self.config.close_s3_files:
                    # Do not hold onto the file contents, close to
                    # free the memory.
                    s3_file.close()
                continue

            self.__validate_file_extension(s3_file)

            parquet_file: ParquetFile = s3_file.to_parquet_file()

            extra_log['num_row_groups'] = parquet_file.num_row_groups

            self.logger.debug(
                f"Reading from parquet, file number '{file_number}'",
                extra=extra_log
            )

            if self.config.dd_profiler_enabled:
                # Log to see the memory usage.
                self.logger.debug(
                    f's3_file size: {sys.getsizeof(s3_file)} bytes '
                    'before closing',
                    extra=extra_log
                )
                self.logger.debug(
                    f'parquet_file size: {sys.getsizeof(parquet_file)}'
                    ' bytes ',
                    extra=extra_log
                )

            current_arrow_schema = parquet_file.schema_arrow.\
                remove_metadata()

            # If the current schema is not a subset
            # TODO scott: we should also be able to work with transposed
            # columns. This will also be necessary for when it is additive
            # but they have added a column in the middle instead of at the end!
            is_schema_ok = (
                list(current_arrow_schema) ==
                list(self.schema)[:len(current_arrow_schema)]
            )
            if not is_schema_ok:
                raise SchemaMismatchException(
                    'Tried to process a file with a schema that does not '
                    'match the schema of the latest. We '
                    'require that all .parquet files have an additive '
                    'schema.'
                    "\n\nLatest file's schema:"
                    f"\n\n{repr(self.schema.remove_metadata())}"
                    "\n\nLatest file's path:"
                    f'\n\n{self.initial_file_path}'
                    f"\n\nCurrent file's schema:"
                    f"\n\n{repr(current_arrow_schema)}"
                    "\n\nCurrent file's path:"
                    f'\n\n{s3_file.path}'
                )
            self.logger.debug('schema OK', extra=extra_log)

            unused_fields: List[pa.Field] = \
                list(self.schema)[len(current_arrow_schema):]
            extra_log['len unused_fields'] = len(unused_fields)

            for row_group_number in range(parquet_file.num_row_groups):

                def get_batches_with_additive_columns() -> List[RecordBatch]:
                    extra_log['row_group_number'] = row_group_number
                    self.logger.debug('Before read_row_group', extra=extra_log)

                    # Content of the row group as a table of columns.
                    row_group: pa.Table = parquet_file. \
                        read_row_group(i=row_group_number)

                    self.logger.debug(
                        'Able to read_row_group from parquet_file',
                        extra=extra_log
                    )

                    if self.config.dd_profiler_enabled:
                        # Log to see the memory usage of each batch.
                        self.logger.debug(
                            f'row_group size: {sys.getsizeof(row_group)} bytes '
                            'before additive schema',
                            extra=extra_log
                        )

                    for field in unused_fields:
                        # TODO scott: This may need a change to set_column if
                        #   we have transposed columns, as we would need to
                        #   append in a specific order.
                        row_group = row_group.append_column(
                            field_=field,
                            # Append and empty array of the correct type and
                            # size to fill in the missing column.
                            column=pa.array(
                                numpy.empty(row_group.num_rows, dtype=object),
                                field.type
                            )
                        )

                    if self.config.dd_profiler_enabled:
                        # Log to see the memory usage of each batch.
                        self.logger.debug(
                            f'row_group size: {sys.getsizeof(row_group)} bytes '
                            'after additive schema',
                            extra=extra_log
                        )

                    self.logger.debug(
                        'Convert row_group to_batches after additive schema',
                        extra=extra_log
                    )

                    return row_group.to_batches()

                # row group no longer referenced after the call so
                # the memory should automatically be freed.
                batches: List[RecordBatch] = \
                    get_batches_with_additive_columns()

                self.logger.debug(
                    'After additive schema to_batches',
                    extra=extra_log
                )

                # At this point we ask for the first batch from the
                # batches iterator, our memory usage to increase massively
                # and does not reduce, even when we leave the outer loop
                # and if we explicitly call gc.collect(1).
                for batch in batches:
                    yield batch
                    if self.config.dd_profiler_enabled:
                        # Log to see the memory usage of each batch.
                        self.logger.debug(
                            f'Batch size: {sys.getsizeof(batch)} bytes',
                            extra=extra_log
                        )

            if self.config.close_s3_files:
                if self.config.dd_profiler_enabled:
                    # Log to see the memory usage of each batch.
                    self.logger.debug(
                        f's3_file size: {sys.getsizeof(s3_file)} bytes before '
                        'closing',
                        extra=extra_log
                    )

                # Do not hold onto the file contents.
                s3_file.close()

                # Log to see the memory usage of each batch.
                self.logger.debug(
                    f'Closed s3_file. Do not hold onto the file contents.',
                    extra=extra_log
                )

    def handle(self, nrows: Optional[int] = None) -> Iterator[bytes]:

        record_batches: Iterator[RecordBatch] = \
            self._get_record_batches_from_files()
        sink = DequeueFile()

        try:
            # double dispatch so that we don't yield in finally
            yield from self._inner_handle(sink=sink, record_batches=record_batches, nrows=nrows)
        except Exception:
            yield from sink.dequeue()
            raise

        yield from sink.dequeue()

    def _inner_handle(
        self,
        sink,
        record_batches: Iterator[RecordBatch],
        nrows: Optional[int] = None,
    ) -> Iterator[bytes]:

        rows_iterated = 0

        self.logger.debug(
            'Handling parquet file',
            extra={'nrows': nrows}
        )

        with handle_arrow_stream_errors(
            RecordBatchStreamWriter(sink, self.schema)
        ) as writer:
            for batch in record_batches:
                if nrows and (rows_iterated + batch.num_rows) > nrows:
                    self.logger.debug(
                        'Truncating last batch',
                        extra={
                            'nrows': nrows,
                            'rows_iterated': rows_iterated,
                            'batch num_rows': batch.num_rows,
                        }
                    )
                    batch_truncated = batch.slice(0, (nrows - rows_iterated))
                    writer.write_batch(batch_truncated)
                    yield from sink.dequeue()
                    rows_iterated = rows_iterated + batch_truncated.num_rows
                    break
                else:
                    writer.write_batch(batch)
                    yield from sink.dequeue()
                    rows_iterated = rows_iterated + batch.num_rows

        self.logger.debug(
            'Completed iteration',
            extra={'nrows': nrows, 'rows_iterated': rows_iterated}
        )

    def __del__(self):
        """Destructor."""
        self.logger.debug('Destructor called on parquet handler')
