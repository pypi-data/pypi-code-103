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

import abc
from typing import Any


class ConfigRepositoryInterface(abc.ABC):

    _config: dict

    @abc.abstractmethod
    def __init__(self, path: str) -> None:
        """
        Load config file in self._config

        :param path: Path of config file
        :return:
        """
        raise NotImplementedError

    def get_root_key(self, name: str) -> Any:
        """
        Get value of root key

        :param name: Name of root key
        :return:
        """
        return self._config[name]
