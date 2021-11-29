#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

import os
import logging

from lxml.etree import tostring

from aos_signer.service_config.config_xml_generator import ConfigXMLGenerator

logger = logging.getLogger(__name__)


class ConfigGeneratorException(Exception):
    pass


class ConfigManager:
    SERVICE_XML_FILENAME = 'config.xml'

    def __init__(self, path):
        self._config_file_name = os.path.join(path, self.SERVICE_XML_FILENAME)

    def remove(self):
        if os.path.exists(self._config_file_name):
            os.remove(self._config_file_name)

    def generate(self, file_details):
        config_generator = ConfigXMLGenerator()
        with open(self._config_file_name, "wb") as fp:
            fp.write(tostring(config_generator.generate(file_details=file_details)))
