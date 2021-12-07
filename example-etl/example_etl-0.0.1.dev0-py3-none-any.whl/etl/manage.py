import logging

from stevedore import ExtensionManager

from etl.config import settings
from etl.exceptions import PluginNotFoundError

logger = logging.getLogger(__name__)


class Manage:
    def __init__(self):
        self.source_kls = get_extension('example_etl.source', settings.SOURCE_NAME)
        self.dest_kls = get_extension('example_etl.dest', settings.DEST_NAME)
        self.process_kls = get_extension('example_etl.process', settings.PROCESS_NAME)

        self.processor = self.process_kls(settings)

    def run(self):
        with self.source_kls(settings) as source:
            with self.dest_kls(settings) as dest:
                self.process(source, dest)
        logger.info('Exit example_etl.')

    def process(self, source, dest):
        logger.info('Start process data ......')
        for i in source.read():
            data = self.processor.process(i)
            dest.write(data)

        logger.info('Data processed.')


def get_extension(namespace: str, name: str):
    extension_manager = ExtensionManager(namespace=namespace, invoke_on_load=False)
    for ext in extension_manager.extensions:
        if ext.name == name:
            logger.info(f'Load plugin: {ext.plugin} in namespace "{namespace}"')
            return ext.plugin

    raise PluginNotFoundError(namespace=namespace, name=name)
