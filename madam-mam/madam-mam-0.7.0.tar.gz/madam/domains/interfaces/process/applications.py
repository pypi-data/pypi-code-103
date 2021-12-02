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
from typing import Optional

from madam.domains.entities.application import Application


class ApplicationProcessManagerInterface(abc.ABC):
    """
    ApplicationProcessManagerInterface class
    """

    @abc.abstractmethod
    def run(self, application: Application, config: Optional[dict] = None) -> None:
        """
        Run application process with process config depending on implementation

        :param application: Application instance
        :param config: Configuration of process (default=None)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def wait(self, application: Application, ignore_failure: bool = False) -> None:
        """
        Wait application process to terminate

        :param application: Application instance
        :param ignore_failure: set process status as complete even if process fails (default=False)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def abort_container(self, id: str) -> None:  # pylint: disable=redefined-builtin
        """
        Abort application process container

        :param id: Process container ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_container(self, id: str) -> None:  # pylint: disable=redefined-builtin
        """
        Delete application process container by id

        :param id: Process container ID
        :return:
        """
        raise NotImplementedError
