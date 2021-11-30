# Handle setting
#
# Author: F. Mertens

import os
import re

from libpipe.settings import BaseSettings


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


class Settings(BaseSettings):

    DEFAULT_SETTINGS = os.path.join(TEMPLATE_DIR, 'default_settings.toml')

    def __init__(self, file, d):
        BaseSettings.__init__(self, file, d)

    def get_target_host(self, in_file):
        host = None
        if self.worker.run_on_file_host and self.worker.run_on_file_host_pattern:
            r = re.search(self.worker.run_on_file_host_pattern, in_file)
            if r is not None:
                host = r.group(1)
        return host


class ImgSettings(Settings):

    DEFAULT_SETTINGS = os.path.join(TEMPLATE_DIR, 'default_img_settings.toml')

    def __init__(self, file, d):
        BaseSettings.__init__(self, file, d)
