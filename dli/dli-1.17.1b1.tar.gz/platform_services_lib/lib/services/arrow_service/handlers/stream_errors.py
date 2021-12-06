#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import logging
from contextlib import contextmanager
from pyarrow import ArrowException
from pyarrow.lib import ArrowNotImplementedError

from ...arrow_service.exceptions import NonCsvFilesInDataset, NonParquetFilesInDataset
from ....services.exceptions import ServiceException, SchemaMismatchException

logger = logging.getLogger(__name__)

# TODO: this seems redundant now we have utils.stream_error_chunker wrapping
# all of our streams. This is called in handle()


@contextmanager
def handle_arrow_stream_errors(writer):
    message = 'Unknown Exception in arrow stream. ' \
              'This could be a problem with the file you are trying ' \
              'to read. Please report the problem to the datalake ' \
              'platform team at DataLake-Support_L1@ihsmarkit.com. ' \
              'Please include the full error message including ' \
              'the request_id.'

    try:
        yield writer
    except NonParquetFilesInDataset:
        logger.warning('NonParquetFilesInDataset')
        raise
    except NonCsvFilesInDataset:
        logger.warning('NonCsvFilesInDataset')
        raise
    except ArrowNotImplementedError as e:
        logger.exception('Arrow not implemented error')
        if ('structs' and 'Parquet files') in e.args[0]:
            raise ServiceException(
                details='The dataset contains a Parquet datafile with '
                        'nested structs, reading from it is not yet '
                        'supported in this version of pyarrow.'
            ) from e
        raise ServiceException(
            details='The dataset contains a datafile '
                    'that cannot be read by pyarrow.'
            ) from e

    # TODO scott: can this ever be reached if we catch it in the handler?
    except ArrowException as e:
        # This will generally happen outside the
        # request context so there's nothing catching
        # the exception and re-logging it in a structured form.

        # This is log level warning rather than error because it can be
        # caused by a csv in a parquet dataset.
        logger.warning(
            'ArrowException while iterating over chunk',
            exc_info=e,
        )
        raise ServiceException(message) from e
    except SchemaMismatchException:
        logger.warning('SchemaMismatchException')
        raise
    except Exception as e:
        logger.exception('Unknown Exception in arrow stream.')
        raise ServiceException(message) from e
    finally:
        logger.debug('Closing writer')
        writer.close()
