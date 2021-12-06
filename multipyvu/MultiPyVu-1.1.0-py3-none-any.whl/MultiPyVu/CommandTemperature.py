# -*- coding: utf-8 -*-
"""
CommandTemperature.py has the information required to get and set the
temperature state.

Created on Tue May 18 13:14:28 2021

@author: djackson
"""

from enum import IntEnum
import time
from threading import Thread, Lock

from .ICommand import ICommand
from .project_vars import MIN_PYWIN32_VERSION
from .instrument import Instrument


class CommandTemperature(ICommand):
    def __init__(self, instrument: Instrument):
        self.scaffolding = True
        self._mvu = None
        if instrument is not None:
            self.scaffolding = instrument.scaffolding_mode
            self._mvu = instrument.multi_vu
        # Temperature state code dictionary
        self.__state_dictionary = {
            1: "Stable",
            2: "Tracking",
            5: "Near",
            6: "Chasing",
            7: "Pot Operation",
            10: "Standby",
            13: "Diagnostic",
            14: "Impedance Control Error",
            15: "General Failure",
        }

        class ApproachEnum(IntEnum):
            fast_settle = 0
            no_overshoot = 1
        self.approach_mode = ApproachEnum
        self.units = 'K'

        self.set_point = 300
        self.set_rate_per_min = 1
        self.set_approach = 1
        self.return_state = 1
        self._thread_running = False
        self.delta_seconds = 0.3

    def convert_result(self, response):
        cmd, t, units, status = response['result'].split(',')
        temperature = float(t)
        return temperature, status

    def prepare_query(self,
                      set_point: float,
                      rate_per_minute: float,
                      approach_mode: IntEnum) -> str:
        try:
            set_point = float(set_point)
        except ValueError:
            err_msg = 'set_point must be a float (set_point = '
            err_msg += "'{set_point}')"
            raise ValueError(err_msg)

        try:
            rate_per_minute = float(rate_per_minute)
            rate_per_minute = abs(rate_per_minute)
        except ValueError:
            err_msg = 'rate_per_minute must be a float '
            err_msg += f'(rate_per_minute = \'{rate_per_minute}\')'
            raise ValueError(err_msg)

        return f'{set_point}, {rate_per_minute}, {approach_mode.value}'

    def _convert_state_dictionary(self, status_number):
        return self.__state_dictionary[status_number]

    def get_state_server(self, value_variant, state_variant):
        if self.scaffolding:
            temperature = self.set_point
        else:
            # Not sure what users do with the error state info
            error = self._mvu.GetTemperature(value_variant, state_variant)

            if self._get_pywin32_version() < MIN_PYWIN32_VERSION:
                # Version 300 and above of pywin32 fixed a bug in which
                # the following two numbers were swapped. So for all prior
                # versions, we need to swap the results.
                (value_variant, state_variant) = (state_variant, value_variant)

            temperature = value_variant.value
            self.return_state = int(state_variant.value)

        return temperature, self.return_state

    def set_state_server(self, arg_string: str):
        error = 0
        if len(arg_string.split(',')) != 3:
            err_msg = 'Setting the temperature requires three numeric inputs, '
            err_msg += 'separated by a comma: '
            err_msg += 'Set Point (K), '
            err_msg += 'rate (K/min), '
            err_msg += 'approach:'
            for mode in self.approach_mode:
                err_msg += f'\n\t{mode.value}: approach_mode.{mode.name}'
            return err_msg
        temperature, rate, approach = arg_string.split(',')
        temperature = float(temperature)
        self.set_rate_per_min = float(rate)
        self.set_approach = int(approach)
        if self.set_approach > len(self.approach_mode) - 1:
            err_msg = f'The approach, {approach}, is out of bounds.  Must be '
            err_msg += 'one of the following'
            for mode in self.approach_mode:
                err_msg += f'\n\t{mode.value}: approach_mode.{mode.name}'
            return err_msg

        if self.scaffolding:
            # stop any other threads
            self._thread_running = False
            time.sleep(2*self.delta_seconds)
            mutex = Lock()
            T = Thread(target=self._simulate_temperature_change,
                       args=(temperature, self.set_rate_per_min, mutex),
                       daemon=True)
            self._thread_running = True
            T.start()
        else:
            self.set_point = temperature
            error = self._mvu.SetTemperature(self.set_point,
                                             self.set_rate_per_min,
                                             self.set_approach)
        return error

    def _simulate_temperature_change(self, temp, rate_per_min, mutex):
        starting_temp = self.set_point
        mutex.acquire()
        self.return_state = 1
        mutex.release()
        delta_seconds = 0.3
        start_time = time.time()
        while time.time() - start_time < 1:
            time.sleep(delta_seconds)
            if not self._thread_running:
                return

        delta_temp = temp - starting_temp
        rate_per_sec = rate_per_min / 60
        rate_per_sec *= -1 if delta_temp < 0 else 1
        rate_time = delta_temp / rate_per_sec
        start_time = time.time()
        mutex.acquire()
        self.return_state = 2
        mutex.release()
        while (time.time() - start_time) < rate_time:
            time.sleep(delta_seconds)
            mutex.acquire()
            self.set_point += delta_seconds * rate_per_sec
            mutex.release()
            if not self._thread_running:
                return

        mutex.acquire()
        self.return_state = 5
        mutex.release()
        start_time = time.time()
        while time.time() - start_time < 5:
            time.sleep(delta_seconds)
            if not self._thread_running:
                return
        mutex.acquire()
        self.set_point = temp
        self.return_state = 1
        mutex.release()

    def state_code_dict(self):
        return self.__state_dictionary
