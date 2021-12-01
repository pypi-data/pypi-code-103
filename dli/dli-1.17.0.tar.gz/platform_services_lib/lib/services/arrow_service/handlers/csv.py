#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import io
import logging
import dataclasses
import itertools
import os
import pandas
import pandas.io.parsers
import pyarrow
import numpy
import re
from typing import Iterator, Pattern, Optional, Dict
from pyarrow import RecordBatchStreamWriter, RecordBatch

from ..handlers.dequeue_file import DequeueFile
from ...arrow_service.exceptions import (NoFilesInDataset, NonCsvFilesInDataset)
from ....services.exceptions import ServiceException, SchemaMismatchException
from ....adapters.s3_io_adapters import ServiceIO
from ....services.arrow_service.handlers.stream_errors import (handle_arrow_stream_errors)


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Config:
    # Chunk size is the number of rows read per chunk.
    # TODO scott: what is the optimal chunk size? It's hard to guess
    # as each .csv file can have a different number of columns.
    # For Storm data:
    # chunk size 1000 body buffer size 2097152 time > 4 minutes, memory usage
    # is low.
    # chunk size 10000 body buffer size 2097152 time 0:03:04.3, 0:03:34.2,
    # memory usage <= 227 MB.
    # chunk size 10000 body buffer size 12582912 time 0:02:52.0, 0:02:57.9,
    # memory usage <= 232 MB
    # chunk size 100000 body buffer size 2097152 time 0:02:51.3, 0:02:53.8,
    # memory usage > 500 MB!
    chunk_size: int = int(os.environ.get('CSV_CHUNK_SIZE', 5000))
    header_buffer_size: int = int(
        os.environ.get('CSV_HEADER_BUFFER_SIZE', 1024)
    )
    body_buffer_size: int = int(
        os.environ.get('CSV_BODY_BUFFER_SIZE', 2097152)
    )


class CsvHandler:

    __file_extension_regex: Pattern[str] = re.compile(r'^.+\.(\w+)$')

    __pandas_supported_compression: Dict[str, str] = {
        # Note: The gzip file extension '.gz' is inconsistently named 'gzip'
        # in the pandas compression parameters, so we have to convert the name.
        'gz': 'gzip',
        'bz2': 'bz2',
        'zip': 'zip',
        'xz': 'xz',
    }

    @staticmethod
    def _extract_file_extension(path: str) -> Optional[str]:
        match = CsvHandler.__file_extension_regex.search(path)
        return match.group(1) if match else None

    def __init__(self, files: Iterator[ServiceIO],
                 order_by_latest: Optional[bool] = None, **kwargs):
        self.config = Config(**kwargs)
        self.order_by_latest = order_by_latest

        logger.debug('CSV handler constructor')

        initial_file = None

        if order_by_latest is True:
            # The parquet schema handling depends on us knowing which
            # is the latest .parquet file. The list of files has to
            # be ordered in some way (ascending or descending),
            # it cannot be un-ordered.
            logger.debug(
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
            logger.debug(
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

        try:
            initial_file = next(files)
        except StopIteration:
            raise NoFilesInDataset(
                'No data in dataset. Unable to stream.'
            )

        extension = CsvHandler._extract_file_extension(initial_file.path)
        # If the extension is:
        # 1. just '.csv',
        # 2. or is an unsupported file type,
        # 3. or there is no extension
        # then pass None as the compression type so that read_csv handles the
        # file as a plain csv file.
        logger.debug(
            f"Extracted file extension '{extension}'",
            extra={
                'extension': extension,
                'path': initial_file.path,
            }
        )

        self.validate_file_extension(initial_file)

        compression = \
            CsvHandler.__pandas_supported_compression.get(str(extension))

        logger.debug(
            'File extension maps to pandas file compression type '
            f"'{compression}'",
            extra={
                'compression': compression,
                'path': initial_file.path,
            }
        )

        try:
            # The gzip code attempts to scan the header one character at a
            # time looking for the end of header marker. This results in over
            # 85 requests to S3. Instead use a buffer because it will request
            # large chunks instead of individual characters, the result will be
            # cached and returned directly on subsequent reads.
            buf = io.BufferedReader(
                initial_file,
                buffer_size=self.config.header_buffer_size
            )

            df: pandas.DataFrame = pandas.read_csv(
                # Pandas will perform automatic on-the-fly decompression
                # based on file extension. Pandas versions > 0.18.1 supports
                # gzip, bz2, zip and xz.
                buf,
                # We are telling pandas to ignore blank lines at the start of a
                # file (sometimes these are introduced into .csv when a data
                # scientist has performed a manual edit on a file).
                skip_blank_lines=True,
                # The header is on the first line of data in the file (after
                # skipping blank lines).
                header=0,
                # Only read the header row from the data file, then stop
                # reading as we only need the header.
                nrows=0,
                compression=compression,
            )

            logger.debug(
                'Header parsed by pandas',
                extra={
                    'extension': extension,
                    'compression': compression,
                    'path': initial_file.path,
                }
            )

            # Detach the underlying stream otherwise your BufferedIOBase
            # object closes the file when it goes out of scope.
            # https://stackoverflow.com/a/8631332
            buf.detach()
            # Remember to rewind the stream! The side-effect of Pandas
            # reading the first line from the stream is that it leaves the
            # pointer pointing to the end of the line. You must manually
            # reset to the start of the file after reading the header so that
            # subsequent calls to the same file will behave as expected.
            initial_file.seek(0)
            logger.debug('seek is back to the start of the file')

        except (OSError, UnicodeDecodeError) as e:
            message = 'Error for initial file. ' \
                      'Unable to stream.'
            logger.warning(
                message,
                exc_info=e,
                extra={'path': initial_file.path}
            )
            raise NonCsvFilesInDataset(
                'Non csv file found in dataset. Path: '
                f'{initial_file.path}'
            ) from e

        except Exception as e:
            message = 'The file is corrupt, ' \
                      'not a .csv like file or cannot be read. ' \
                      'Please report the problem to the datalake ' \
                      'platform team at DataLake-Support_L1@ihsmarkit.com. ' \
                      'Please include the full error message including ' \
                      'the request_id.'
            logger.exception(message)
            raise ServiceException(message) from e

        # For the type of the column to be string as types in a .csv may not
        # be consistent across files.
        fields = [
            (column_name, pyarrow.string())
            for column_name in list(df.columns)
        ]

        logger.debug(
            'Column names read from .csv header row (cast to string)',
            extra={'columns': fields}
        )

        self.schema: pyarrow.Schema = pyarrow.schema(fields).remove_metadata()
        logger.debug(
            'Parquet columns mapped to pyarrow schema names',
            extra={
                'schema_names': self.schema.names
            }
        )
        logger.debug(
            'Parquet columns mapped to pyarrow schema types',
            extra={
                'schema_names': self.schema.types
            }
        )

        self._initial_file = initial_file

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

    @staticmethod
    def validate_file_extension(s3_file: ServiceIO):
        if '.csv' not in s3_file.path:
            logger.warning(
                'Non csv file found in dataset.',
                extra={
                    'path': s3_file.path,
                }
            )
            raise NonCsvFilesInDataset(
                f'Non csv file found in dataset. Path: {s3_file.path}'
            )

    @staticmethod
    def _validate_file_size(s3_file: ServiceIO):
        """File size must be greater than zero."""
        if hasattr(s3_file, 'size'):
            return s3_file.size > 0
        else:
            return False

    def _get_row_chunks_from_files(self) -> Iterator[pandas.DataFrame]:
        """Returns a lazy iterator which gets batches multiple files into
        chunks of N lines . """
        for file_number, file in enumerate(self._files):
            if not self._validate_file_size(file):
                # Skip zero size files.
                logger.warning(
                    'File has been skipped, CSV file size is 0 bytes.',
                    extra={'path': file.path}
                )
                continue
            self.validate_file_extension(file)

            logger.debug(
                f"Iterating over file number '{file_number}'",
                extra={
                    'path': file.path,
                    'file_number': file_number
                }
            )

            for idx, file_reader in enumerate(self._get_row_chunks_from_file(file)):
                for chunks in file_reader:
                    chunk = pyarrow.RecordBatch.from_pandas(
                        chunks, preserve_index=False
                    )

                    current_csv_schema = chunk.schema.remove_metadata()

                    # If the current schema is not a subset
                    # TODO scott: we should also be able to work with
                    # transposed columns. This will also be necessary
                    # for when it is additive but they have added a
                    # column in the middle instead of at the end!
                    is_schema_ok = (
                        current_csv_schema.names ==
                        self.schema.names[:len(current_csv_schema)]
                    )
                    if not is_schema_ok:
                        raise SchemaMismatchException(
                            'Tried to process a file with a schema that does '
                            'not match the schema of the latest. We '
                            'require that all .csv files have an additive '
                            'schema.'
                            "\n\nLatest file's schema:"
                            f"\n\n{self.schema.remove_metadata().names}"
                            "\n\nLatest file's path:"
                            f'\n\n{self._initial_file.path}'
                            f"\n\nCurrent file's schema:"
                            f"\n\n{current_csv_schema.names}"
                            "\n\nCurrent file's path:"
                            f'\n\n{file.path}'
                        )

                    unused_fields = list(self.schema)[len(current_csv_schema):]
                    columns = list(chunk.columns)

                    for field in unused_fields:
                        # TODO scott: This may need a change if we have
                        # transposed columns, as we would need to append
                        # in a specific order.
                        columns.append(
                            # Append and empty array of the correct type and
                            # size to fill in the missing column.
                            pyarrow.array(
                                numpy.empty(chunk.num_rows, dtype=object),
                                field.type
                            )
                        )

                    pandas_chunk = RecordBatch.from_arrays(
                        columns, schema=self.schema
                    ).to_pandas()

                    yield file, pandas_chunk
            # The side-effect of Pandas reading the first line from the
            # stream is that it leaves the pointer pointing to the end of the
            # line. You must manually reset to the start of the file after
            # reading the header so that subsequent calls to the same file
            # will behave as expected.
            logger.debug('Seek to start of the file...')
            file.seek(0)
            logger.debug('Seek completed')

    def _get_row_chunks_from_file(self, file: ServiceIO):
        """Returns a lazy iterator which gets batches a single file into
        chunks of N lines . """

        extension = CsvHandler._extract_file_extension(file.path)
        # If the extension is:
        # 1. just '.csv',
        # 2. or is an unsupported file type,
        # 3. or there is no extension
        # then pass None as the compression type so that read_csv handles the
        # file as a plain csv file.
        logger.debug(
            f"Extracted file extension '{extension}'",
            extra={
                'extension': extension,
                'path': file.path,
            }
        )

        compression = \
            CsvHandler.__pandas_supported_compression.get(str(extension))

        logger.debug(
            'File extension maps to pandas file compression type '
            f"'{compression}'",
            extra={
                'extension': extension,
                'compression': compression,
                'path': file.path,
            }
        )

        chunks: pandas.io.parsers.TextFileReader = pandas.read_csv(
            # Pandas will perform automatic on-the-fly decompression based on
            # file extension. Pandas versions > 0.18.1 supports gzip, bz2,
            # zip and xz.
            # The gzip code attempts to scan the header one character at a
            # time looking for the end of header marker. This results in over
            # 85 requests to S3. Instead use a buffer because it will request
            # large chunks instead of individual characters, the result will be
            # cached and returned directly on subsequent reads.
            io.BufferedReader(file, buffer_size=self.config.body_buffer_size),
            # Force all column types to be string. We should NOT allow pandas
            # to infer the type as there are cases where the first file we
            # read does not have a large enough sample of data and so infers
            # the wrong type e.g. the data it sees in column 0 in the first
            # file only contains integers so it infers integer, but the
            # second file contains strings (or another type like floats). The
            # process would fail when trying to combine the separate
            # DataFrames because of the different types.
            dtype=str,
            # We are telling pandas to ignore blank lines at the start of a
            # file (sometimes these are introduced into .csv when a data
            # scientist has performed a manual edit on a file).
            skip_blank_lines=True,
            # The header is on the first line of data in the file (after
            # skipping blank lines).
            header=0,
            # Allows us to iterate through a very large file lazily rather
            # than reading the entire file into memory. The file is chunked
            # into N rows.
            chunksize=self.config.chunk_size,
            compression=compression,
        )
        logger.debug(
            'pandas has chunked the file with chunk_size '
            f"'{self.config.chunk_size}'",
            extra={
                'extension': extension,
                'compression': compression,
                'path': file.path,
                'chunk_size': self.config.chunk_size,
            }
        )
        yield chunks

    def handle(self, nrows=None) -> Iterator[bytes]:
        chunks_per_file = self._get_row_chunks_from_files()

        sink = DequeueFile()
        rows_iterated = 0

        try:
            with handle_arrow_stream_errors(
                RecordBatchStreamWriter(sink, self.schema)
            ) as writer:
                for idx, (file, chunk) in enumerate(chunks_per_file):
                    rows, cols = chunk.shape

                    logger.debug(
                        f"Iterating over CSV chunk number '{idx}'",
                        extra={
                            'chunk_number': idx,
                            'shape': (rows, cols),
                            'rows_iterated': rows_iterated,
                        }
                    )

                    if nrows and (rows_iterated + rows) > nrows:
                        logger.debug('Truncating.')
                        truncated_chunk = chunk.head(nrows - rows_iterated)

                        batch = RecordBatch.from_pandas(
                            df=truncated_chunk, schema=self.schema
                        )

                        writer.write_batch(batch)
                        yield from sink.dequeue()
                        break
                    else:
                        logger.debug('Record batch from pandas')
                        batch = RecordBatch.from_pandas(
                            df=chunk, schema=self.schema
                        )

                        logger.debug('write batch')
                        writer.write_batch(batch)

                        logger.debug('sink dequeue')
                        yield from sink.dequeue()
                        rows_iterated = rows_iterated + rows

                logger.debug('Completed iteration.')
        finally:
            yield from sink.dequeue()
