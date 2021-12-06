# -*- coding: utf-8 -*-
"""
This has the information required to get and set the chamber state.

Created on Tue May 18 13:14:28 2021

@author: djackson
"""

from enum import IntEnum

from .ICommand import ICommand
from .instrument import Instrument


class CommandChamber(ICommand):
    def __init__(self, instrument: Instrument):
        self.scaffolding = True
        self._mvu = None
        if instrument is not None:
            self.scaffolding = instrument.scaffolding_mode
            self._mvu = instrument.multi_vu
        # State code dictionary
        self.__state_dictionary = {
            0: 'Unknown',
            1: 'Purged and Sealed',
            2: 'Vented and Sealed',
            3: 'Sealed (condition unknown)',
            4: 'Performing Purge/Seal',
            5: 'Performing Vent/Seal',
            6: 'Pre-HiVac',
            7: 'HiVac',
            8: 'Pumping Continuously',
            9: 'Flooding Continuously',
            14: 'HiVac Error',
            15: 'General Failure'
        }

        class modeEnum(IntEnum):
            seal = 0
            purge_seal = 1
            vent_seal = 2
            pump_continuous = 3
            vent_continuous = 4
            high_vacuum = 5
        self.mode = modeEnum
        self.units = ''

        self.set_mode = 1
        self.return_state = 1

    def mode_setting_correct(self,
                             mode_setting: IntEnum,
                             mode_readback):
        if mode_setting == self.mode.seal:
            returnTrue = [self.__state_dictionary[1],
                          self.__state_dictionary[2],
                          self.__state_dictionary[3],
                          ]
            if mode_readback in returnTrue:
                return True
        elif mode_setting == self.mode.purge_seal:
            return (mode_readback == self.__state_dictionary[1])
        elif mode_setting == self.mode.vent_seal:
            return (mode_readback == self.__state_dictionary[2])
        elif mode_setting == self.mode.pump_continuous:
            return (mode_readback == self.__state_dictionary[8])
        elif mode_setting == self.mode.vent_continuous:
            return (mode_readback == self.__state_dictionary[9])
        elif mode_setting == self.mode.high_vacuum:
            return (mode_readback == self.__state_dictionary[7])

    def convert_result(self, response):
        cmd, blank1, blank2, status = response['result'].split(',')
        return status

    def prepare_query(self, mode: IntEnum) -> str:
        try:
            mode = int(mode)
        except ValueError:
            msg = 'mode must be an integer. One could use the .modeEnum'
            raise ValueError(msg)
        return f'{mode}'

    def _convert_state_dictionary(self, status_number):
        return self.__state_dictionary[status_number]

    def get_state_server(self, value_variant, state_variant):
        if self.scaffolding:
            pass
        else:
            # Not sure what users do with the error state info
            error = self._mvu.GetChamber(state_variant)

            self.return_state = int(state_variant.value)

        return '', self.return_state

    def set_state_server(self, arg_string):
        error = 0
        if len(arg_string.split(',')) != 1:
            err_msg = 'Setting the chamber requires 1 input: mode'
            return err_msg
        self.set_mode = int(arg_string)
        if self.set_mode > len(self.mode) - 1:
            err_msg = f'The selected mode, {self.set_mode}, is '
            err_msg += 'out of bounds.  Must be one of the following:'
            for m in self.mode:
                err_msg += f'\n\t{m.value}: {m.name}'
            return err_msg
        if self.scaffolding:
            if self.set_mode == self.mode.seal.value:
                self.return_state = 3
            elif (self.set_mode == self.mode.purge_seal.value
                  or self.set_mode == self.mode.vent_seal.value):
                self.return_state = self.set_mode
            elif self.set_mode == self.mode.pump_continuous.value:
                self.return_state = 8
            elif self.set_mode == self.mode.vent_continuous.value:
                self.return_state = 9
            elif self.set_mode == self.mode.high_vacuum.value:
                self.return_state = 7
            error = 1
        else:
            # The chamber returns '1' if the command was accepted
            error = self._mvu.SetChamber(self.set_mode)
        return error

    def state_code_dict(self):
        return self.__state_dictionary
