# -*- coding: utf-8 -*-
"""
This is a base class factory method to call lup the specific MultiVu commands

Created on Sat June 12 17:35:28 2021

@author: djackson
"""

import sys

from .instrument import Instrument, MultiVuExeException
from .CommandTemperature import CommandTemperature
from .CommandField import CommandField
from .CommandChamber import CommandChamber

if sys.platform == 'win32':
    try:
        import win32com.client
        import pythoncom
    except ImportError:
        print("Must import the pywin32 module.  Use:  ")
        print("\tconda install -c conda-forge pywin32")
        print("   or")
        print("\tpip install pywin32")
        sys.exit(0)


class CommandMultiVu():
    def __init__(self, instrument: Instrument):
        self.scaffolding = True
        if instrument is not None:
            self.scaffolding = instrument.scaffolding_mode
        t = CommandTemperature(instrument)
        f = CommandField(instrument)
        c = CommandChamber(instrument)
        self.cmd_dict = {'TEMP': t,
                         'FIELD': f,
                         'CHAMBER': c,
                         }

    def _check_command_name(self, input_command):
        if input_command not in self.cmd_dict:
            raise MultiVuExeException(f'Unknown command: "{input_command}".')

    def get_state(self, command) -> str:
        '''
        Gets and returns a query from MultiVu.

        Parameters
        ----------
        command : str
            The name of the command.  Possible choises are the keys
            listed in .cmd_dict.

        Raises
        ------
        MultiVuExeException
            Raises an error if the command is not in the cmd_dict.

        Returns
        -------
        str
            {command?, result_string, units, code_in_words}.

        '''
        self._check_command_name(command)
        mv_command = self.cmd_dict[command]

        if self.scaffolding:
            # these numbers aren't used by the scaffolding
            value_variant = None
            state_variant = None
        else:
            # Setting up a by-reference (VT_BYREF) double (VT_R8)
            # variant.  This is used to get the value.
            value_variant = (win32com.client.VARIANT(pythoncom.VT_BYREF
                                                     | pythoncom.VT_R8, 0.0))
            # Setting up a by-reference (VT_BYREF) integer (VT_I4)
            # variant.  This is used to get the status code.
            state_variant = (win32com.client.VARIANT(pythoncom.VT_BYREF
                                                     | pythoncom.VT_I4, 0))

        result, status_number = mv_command.get_state_server(value_variant,
                                                            state_variant)
        try:
            # Get the translated state code
            code_in_words = mv_command._convert_state_dictionary(status_number)
        except KeyError:
            msg = f'Error in {self.__class__.__name__}:  '
            msg += f'Returning value = {result} and '
            msg += f'status = {status_number}, '
            msg += 'which could mean MultiVu is not running.'
            raise MultiVuExeException(msg)

        result_string = result if type(result) == str else f'{result:.4f}'
        return f'{command}?,{result_string},{mv_command.units},{code_in_words}'

    def set_state(self, command, arg_string):
        '''
        Sets the state for a given command using the arg_string for parameters

        Parameters
        ----------
        command : str
            The name of the command.  Possible choises are the keys
            listed in .cmd_dict.
        arg_string : str
            The arguments that should be passed on to the command.
                TEMP: set point, rate, mode
                FIELD: set point, rate, approach, and magnetic state.
                CHAMBER: mode

        Raises
        ------
        MultiVuExeException
            Raises an error if the command is not in the cmd_dict.

        Returns
        -------
        str
            The SocketMessage.response string.

        '''
        self._check_command_name(command)
        mv_command = self.cmd_dict[command]
        try:
            err = mv_command.set_state_server(arg_string)
        except MultiVuExeException as e:
            raise MultiVuExeException(e.message)
        else:
            if (err == 0 and command != 'CHAMBER'
                    or err == 1 and command == 'CHAMBER'):
                return f'{command} Command Received'
            else:
                msg = f'Error when setting the {command} {arg_string}: '
                msg += f'error = {err}'
                return msg
