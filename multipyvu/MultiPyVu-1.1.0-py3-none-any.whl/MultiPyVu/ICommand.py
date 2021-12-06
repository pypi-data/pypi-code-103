# -*- coding: utf-8 -*-
"""
This provides an interface for MultiVu commands (CommandTemperature,
                                                 CommandField,
                                                 and CommandChamber)

It requires ABCplus (Abstract Base Class plus), which is found here:
    https://pypi.org/project/abcplus/

Created on Tue May 18 12:59:24 2021

@author: djackson
"""

import os
import distutils.sysconfig
from abc import ABC, abstractmethod


class ICommand(ABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'convert_result')
            and callable(subclass.convert_result) and

            hasattr(subclass, 'prepare_query')
            and callable(subclass.prepare_query) and

            hasattr(subclass, '_convert_state_dictionary')
            and callable(subclass._convert_state_dictionary) and

            hasattr(subclass, 'get_state_server')
            and callable(subclass.get_state_server) and

            hasattr(subclass, 'set_state_server')
            and callable(subclass.set_state_server) and

            hasattr(subclass, 'state_code_dict')
            and callable(subclass.state_code_dict)

            or NotImplemented)

    def _get_pywin32_version(self):
        '''
        Get the version number for pywin32

        Returns
        -------
        pywin32 version number.

        '''
        pth = distutils.sysconfig.get_python_lib(plat_specific=1)
        pth = os.path.join(pth, "pywin32.version.txt")
        with open(pth) as ver_file_obj:
            version = ver_file_obj.read().strip()
        return int(version)

    @abstractmethod
    def convert_result(self, result):
        raise NotImplementedError

    @abstractmethod
    def prepare_query(self, *args):
        raise NotImplementedError

    @abstractmethod
    def _convert_state_dictionary(self, statusNumber):
        raise NotImplementedError

    @abstractmethod
    def get_state_server(self, statusCode, stateValue):
        raise NotImplementedError

    @abstractmethod
    def set_state_server(self, arg_string: str):
        raise NotImplementedError

    @abstractmethod
    def state_code_dict(self):
        raise NotImplementedError
