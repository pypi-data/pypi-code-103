import logging

from example_etl.process.base import BaseProcess

logger = logging.getLogger(__name__)


class StripProcess(BaseProcess):
    def process(self, data: str) -> str:
        logger.debug(f'Strip data: "{data}"')
        return data.strip()
