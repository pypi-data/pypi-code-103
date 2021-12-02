# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

"""
Madam config module
"""
import logging

import yaml

from madam.domains.interfaces.repository.config import ConfigRepositoryInterface


class YAMLConfigRepository(ConfigRepositoryInterface):
    """
    Madam YAML config file adapter
    """

    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, path: str):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConfigRepositoryInterface.__init__.__doc__
        )

        logging.debug("load yaml config from %s", path)
        # load madam config
        with open(path, encoding="utf-8") as filehandler:
            self._config = yaml.load(filehandler, Loader=yaml.FullLoader)
