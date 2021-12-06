# -*- coding: utf-8 -*-
"""
This has the information required to get and set the field state.

Created on Tue May 18 13:14:28 2021

@author: djackson
"""

from enum import IntEnum
import time
from threading import Thread, Lock

from .ICommand import ICommand
from .project_vars import MIN_PYWIN32_VERSION
from .instrument import Instrument, MultiVuExeException


class CommandField(ICommand):
    def __init__(self, instrument: Instrument):
        self.instrument = instrument
        self.scaffolding = True
        self._mvu = None
        if instrument is not None:
            self.scaffolding = instrument.scaffolding_mode
            self._mvu = instrument.multi_vu
        # Field state code dictionary
        self.__state_dictionary = {
            1: 'Stable',
            2: 'Switch Warming',
            3: 'Switch Cooling',
            4: 'Holding (driven)',
            5: 'Iterate',
            6: 'Ramping',
            7: 'Ramping',
            8: 'Resetting',
            9: 'Current Error',
            10: 'Switch Error',
            11: 'Quenching',
            12: 'Charging Error',
            14: 'PSU Error',
            15: 'General Failure',
        }

        class ApproachEnum(IntEnum):
            linear = 0
            no_overshoot = 1
            oscillate = 2
        self.approach_mode = ApproachEnum

        # the PPMS is the only flavor which can run persistent
        class drivenEnum(IntEnum):
            persistent = 0
            driven = 1

            @classmethod
            def _missing_(cls, value):
                return drivenEnum.driven
        self.driven_mode = drivenEnum
        self.units = 'Oe'

        self.set_point = 0
        self.set_rate_per_sec = 1
        self.set_approach = 1
        self.set_driven = 1
        self.return_state = 1
        self._thread_running = False
        self.delta_seconds = 0.3

    def convert_result(self, response):
        cmd, h, units, status = response['result'].split(',')
        field = float(h)
        return field, status

    def prepare_query(self,
                      set_point: float,
                      rate_per_sec: float,
                      approach: IntEnum,
                      mode=None) -> str:
        try:
            set_point = float(set_point)
        except ValueError:
            err_msg = f"set_point must be a float (set_point = '{set_point}')"
            raise ValueError(err_msg)

        try:
            rate_per_sec = float(rate_per_sec)
            rate_per_sec = abs(rate_per_sec)
        except ValueError:
            err_msg = 'rate_per_minute must be a float '
            err_msg += f'(rate_per_sec = \'{rate_per_sec}\')'
            raise ValueError(err_msg)

        # driven is default because it is used by all but the PPMS
        mode = self.driven_mode.driven.value if mode is None else mode.value

        return f'{set_point}, {rate_per_sec}, {approach.value}, {mode}'

    def _convert_state_dictionary(self, status_number):
        return self.__state_dictionary[status_number]

    def get_state_server(self, value_variant, state_variant):
        if self.scaffolding:
            field = self.set_point
        else:
            # Not sure what users do with the error state info
            error = self._mvu.GetField(value_variant, state_variant)

            if self._get_pywin32_version() < MIN_PYWIN32_VERSION:
                # Version 300 and above of pywin32 fixed a bug in which
                # the following two numbers were swapped. So for all prior
                # versions, we need to swap the results.
                (value_variant, state_variant) = (state_variant, value_variant)

            field = value_variant.value
            self.return_state = int(state_variant.value)

        return field, self.return_state

    def set_state_server(self, arg_string):
        error = 0
        if len(arg_string.split(',')) != 4:
            err_msg = 'Setting the field requires four numeric inputs, '
            err_msg += 'separated by a comma: '
            err_msg += 'Set Point (Oe), '
            err_msg += 'rate (Oe/sec),'
            err_msg += 'approach (Linear (0); No O\'Shoot (1); Oscillate (2)),'
            err_msg += 'magnetic state (persistent (0); driven (1))'
            return err_msg
            # raise MultiVuExeException(err_msg)
        field, rate, approach, driven = arg_string.split(',')
        field = float(field)
        self.set_rate_per_sec = float(rate)
        self.set_approach = int(approach)
        self.set_driven = int(driven)
        if self.set_approach > len(self.approach_mode) - 1:
            err_msg = f'The approach, {approach}, is out of bounds.  Must be '
            err_msg += 'one of the following'
            for mode in self.approach_mode:
                print(f'\n\t{mode.value}: {mode.name}')
            raise MultiVuExeException(err_msg)

        if self.instrument.name != 'PPMS':
            if self.set_driven == self.driven_mode.persistent:
                err_msg = f'{self.instrument.name} can only drive the magnet '
                err_msg += 'in driven mode.'
                raise MultiVuExeException(err_msg)
        else:
            if self.set_driven > len(self.driven_mode) - 1:
                err_msg = f'The mode, {driven}, is out of bounds.  Must be '
                for mode in self.driven_mode:
                    err_msg += f'\n\t{mode.value}: {mode.name}'
                raise MultiVuExeException(err_msg)

        if self.scaffolding:
            # stop any other threads
            self._thread_running = False
            time.sleep(2*self.delta_seconds)
            mutex = Lock()
            F = Thread(target=self._simulate_field_change,
                       args=(field, self.set_rate_per_sec, mutex),
                       daemon=True)
            self._thread_running = True
            F.start()
        else:
            self.set_point = field
            error = self._mvu.setField(self.set_point,
                                       self.set_rate_per_sec,
                                       self.set_approach,
                                       self.set_driven
                                       )
        return error

    def _simulate_field_change(self, field, rate_per_sec, mutex):
        starting_H = self.set_point
        mutex.acquire()
        self.return_state = 4
        mutex.release()
        start_time = time.time()
        while time.time() - start_time < 1:
            time.sleep(self.delta_seconds)
            if not self._thread_running:
                return

        delta_H = field - starting_H
        rate_per_sec *= -1 if delta_H < 0 else 1
        rate_time = delta_H / rate_per_sec
        start_time = time.time()
        mutex.acquire()
        self.return_state = 6
        mutex.release()
        while (time.time() - start_time) < rate_time:
            time.sleep(self.delta_seconds)
            mutex.acquire()
            self.set_point += self.delta_seconds * rate_per_sec
            mutex.release()
            if not self._thread_running:
                return

        start_time = time.time()
        time.sleep(self.delta_seconds)
        while time.time() - start_time < 5:
            time.sleep(self.delta_seconds)
            if not self._thread_running:
                return
        mutex.acquire()
        self.set_point = field
        self.return_state = 4
        mutex.release()

    def state_code_dict(self):
        return self.__state_dictionary
