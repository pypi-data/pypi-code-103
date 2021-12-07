import logging

from etl.source.base import BaseSource

logger = logging.getLogger(__name__)


class FileSource(BaseSource):

    def read(self):
        source_path = self.settings.FILE_SOURCE_PATH
        logger.info(f'Read data from {source_path}')
        with open(source_path, 'r') as file:
            for i in file:
                yield i
