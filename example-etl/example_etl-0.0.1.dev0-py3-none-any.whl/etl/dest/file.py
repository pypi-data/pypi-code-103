import logging

from etl.dest.base import BaseDest

logger = logging.getLogger(__name__)


class FileDest(BaseDest):
    file = None

    def setup(self):
        dest_path = self.settings.FILE_DEST_PATH
        logger.info(f'Write data to {dest_path}')
        self.file = open(dest_path, 'w')

    def write(self, data: str):
        self.file.write(data)
        self.file.flush()

    def close(self):
        self.file.close()
