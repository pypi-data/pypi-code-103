"""
This is a python translation of the Magventure part of the MAGIC toolbox (https://github.com/nigelrogasch/MAGIC).

MagicPy
Copyright (C) 2021  Ole Numssen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
import time
import warnings

import serial
import numpy as np


class MagVenture:
    """
    Class to manage communication with an Magventure TMS stimulator connected to a serial port.
    
    Example:    

    > m = MagVenture('/dev/ttyS4')
    > m.connect()
    > m.arm()
    > m.set_amplitude(50)
    > m.fire()
    > m.disarm()
    > m.disconnect()
    
    

    Attributes
    ----------
    
    port : serial.Serial()
           Information about the serial connection. 
    """

    def __init__(self, portid, flush_before_cmd=True, wait_s=1, wait_l=1):
        """


        Parameters
        ----------
        portid : str
            Name of serial port to which the stimulator is connected.
        flush_before_cmd : bool
            Discard old device responds before sending the next command.
        wait_s : int
            Waittime for reading response from stimulator. Increase in case of communication problems.
        wait_l : int
            Waittime for reading response from stimulator for status2() . Increase in case of communication problems.

        """

        p = serial.Serial()
        p.port = portid
        p.baudrate = 38400

        p.bytesize = serial.EIGHTBITS
        p.parity = serial.PARITY_NONE
        p.stopbits = serial.STOPBITS_ONE
        p.timeout = 3

        self.port = p
        self.coil_types = {62: 'MCF-B65'}
        self.show_coil_hint = True
        self.flush_before_cmd = flush_before_cmd
        self.sleep_short = wait_s
        self.sleep_long = wait_l

    @staticmethod
    def calc_crc(cmd):
        """
        Computes CRC code needed for the MagVenture device to accept the command.

        Parameters
        ----------
        cmd : list of str
              The command that should be send to the stimulator as bytestring. E.g.: ['01','02']               

        Returns
        -------
        Str : The CRC in hexstring.

        """
        scale = 16  # equals to hexadecimal
        num_of_bits = 8
        polytocheck = []
        for stream in cmd:
            # for each byte, convert to bin and remove the leading '0b'.
            # fill with zeros to num_of_bits
            # and reverse
            polytocheck += list(bin(int(stream, scale))[2:].zfill(num_of_bits)[::-1])

        genpoly = [1, 0, 0, 1, 1, 0, 0, 0, 1]  # Dallas/Maxim generator polynomial
        polytocheck += list('00000000')  # Pad with zeros to take care of short commands. 
        counter = len(genpoly)
        reg = polytocheck[0:counter]

        # the CRC code itself
        for j in range(counter, len(polytocheck)):
            if reg[0] == '1':
                reg = [str(int(a) ^ int(cmd)) for (a, cmd) in zip(list(reg), genpoly)]
            reg = reg[1:] + [polytocheck[j]]
        if reg[0] == '1':
            reg = [str(int(a) ^ int(cmd)) for (a, cmd) in zip(list(reg), genpoly)]

        return hex(int(''.join(reg[::-1][:8]), 2))[2:]

    def connect(self, force=False):
        """
        Opens or reopens the desired port.

        Parameters
        ----------
        force : bool
            Reopen if already open. Default is False.

        """
        if self.port.is_open and force:
            self.port.close()
            self.port.open()
        elif not self.port.is_open:
            self.port.open()
        else:
            raise ConnectionError(f'Port {self.port.port} is already connected.')

    def disconnect(self):
        """
        Closes the port.

        """
        if not self.port.is_open:
            raise ConnectionError("Port is already closed")
        else:
            self.port.close()

    def get_status(self):
        """
        Gets the status of the stimulator.

        Returns
        -------
        device_response : dict
            The response sent back from the device.
        error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '01'
        command_id = '00'
        command_bytes = command_id
        resp_len_exp = 13
        get_response = True

        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def set_amplitude(self, a_amp, b_amp=None, get_response=False):
        """
        Sets the amplitude in standard or twin mode. If only one amplitude (a_amp) is given,
        standard mode is selected. If both amplitudes (a_amp, b_amp) are given, Dual/ Twin Mode
        is selected.

        Parameters
        ----------
        a_amp : int
             Indicates A amplitude in percentage in Standard Mode
            Default is set to 'None'
        b_amp : int, optinal
            Indicates B amplitude in percentage in Dual/ Twin Mode (otherwise only A amplitude required)
            Default is None
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
        device_response : dict
            The response sent back from the device
        error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        assert 0 <= a_amp <= 100
        if b_amp is None:
            command_length = '02'
            command_id = '01'
            amp = hex(a_amp)
            command_bytes = [command_id, amp]

        else:
            assert 0 <= b_amp <= 100
            command_length = '03'
            command_id = '01'
            amp1 = hex(a_amp)
            amp2 = hex(b_amp)
            command_bytes = [command_id, amp1, amp2]

        return self.process_command(command_length, command_bytes, get_response=get_response)

    def arm(self, get_response=False):
        """
        Enables the stimulator.

        Parameters
        ----------
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
        device_response : dict
            The response sent back from the device.
        error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '02'
        command_id = '02'
        value = '01'
        command_bytes = [command_id, value]

        # the X100 returns 3 responses: status, coil info, status -> 3*8
        resp_len_exp = 24
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        return device_response, error

    def disarm(self, get_response=False):
        """
        Disables the sitmulator.

        Parameters
        ----------
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
        device_response : dict
            The response sent back from the device.
        error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '02'
        command_id = '02'
        value = '00'
        command_bytes = [command_id, value]

        return self.process_command(command_length, command_bytes, get_response=get_response)

    def fire(self, get_response=False):
        """
        Fires a single pulse. Note that this is sent through the serial port and thus has a high jitter.
        If you need precise pulse timing, you need to send TTL pulse triggers to the stimulators Trigger-in port.

        Parameters
        ----------
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '02'
        command_id = '03'
        value = '01'
        command_bytes = [command_id, value]

        return self.process_command(command_length, command_bytes, get_response=get_response)

    def send_train(self, get_response=False):
        """
        Sends a train of pulses to the specified port.

        Parameters
        ----------
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '01'
        command_id = '04'
        command_bytes = command_id
        resp_len_exp = 17

        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def get_status2(self):
        """
        Gets the second status (Status2) of the stimulator.


        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        command_length = '01'
        command_id = '05'
        command_bytes = command_id
        resp_len_exp = 19
        get_response = True
        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def set_train(self, reprate, n_pulses, n_trains, iti, get_response=False):
        """
        Sets train parameters. A train is a sequence of multiple pulses in a specific rate. Multiple trains (of the
        same type) can be sent successively.

        Parameters
        ----------
        reprate : int
            Number of pulses per second.
        n_pulses : int
            Number of pulses in each train.
        n_trains: int
            Total amount of trains per sequence.
        iti : int
            Time interval between two trains in seconds.
            This is the time period between the last pulse in the first train and the first pulse in the next train.
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        if reprate not in list(np.arange(.1, 1, .1)) + list(range(1, 101)):
            raise ValueError(f'reprate {reprate} is not within (.1, .2, .3, ..., 1, 2, 3, 100)')

        if np.remainder(n_pulses, 1) or n_pulses <= 0:
            raise ValueError(f'n_pulses={n_pulses} must be a positive tnteger')

        if n_pulses not in list(range(1, 100)) + list(range(1000, 2000, 100)):
            raise ValueError(f'n_pulses={n_pulses} not within (1, 2, 3, ..., 100) or (1000, 1100, 1200, ..., 2000')

        if np.remainder(n_trains, 1) or n_trains <= 0:
            raise ValueError(f'n_trains={n_trains} must be a positive integer.')

        if n_trains not in range(1, 501):
            raise ValueError(f'n_trains={n_trains} not within (1, ..., 500).')

        if iti <= 0:
            raise ValueError(f'The inter train interval "iti={iti}" must be positive.')

        if iti not in np.arange(.1, 120.1, .1):
            raise ValueError(f'iti={iti} not in (.1, .2, ..., 119.9, 120).')

        command_length = '09'
        command_id = '06'

        reprate_l, reprate_m = self.hexlm(reprate, 10)
        n_pulses_l, n_pulses_m = self.hexlm(n_pulses)
        n_trains_l, n_trains_m = self.hexlm(n_trains)
        iti_l, iti_m = self.hexlm(iti, 10)

        command_bytes = [command_id, reprate_m, reprate_l, n_pulses_m, n_pulses_l,
                         n_trains_m, n_trains_l, iti_m, iti_l]

        return self.process_command(command_length, command_bytes, get_response=get_response)

    def set_page(self, page, get_response=False):
        """
        Configures the desired page.

        Parameters
        ----------
        page : str
            Which page to configure.
            One of 'Main','Train','Trig','Config','Protocol'.
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        if page == 'Main':
            page_n = '01'

        elif page == 'Train':
            page_n = '02'

        elif page == 'Trig':
            page_n = '03'

        elif page == 'Config':
            page_n = '04'

        elif page == 'Protocol':
            page_n = '07'
        else:
            raise ValueError(f'Invalid page name {page}')

        command_length = '03'
        command_id = '07'
        nabyte = '00'
        command_bytes = [command_id, page_n, nabyte]

        return self.process_command(command_length, command_bytes, get_response=get_response)

    def settrig_chargedelay(self, trig_in_delay, trig_out_delay, charge_delay, get_response=False):
        """
        Sets trigger and charge delay.

        Parameters
        ----------
        trig_in_delay : int
            Trigger-in delay in millliseconds.
        trig_out_delay: int
            Trigger-out delay in milliseconds.
        charge_delay: int
            Time in milliseconds to make the device wait before recharging.
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """

        if get_response:
            self.connect()

        if np.remainder(trig_in_delay, 1) or trig_in_delay < 0:
            raise ValueError(f'trig_in_delay={trig_in_delay} must be a positive integer.')
        elif trig_in_delay > 65535:  # Must fit into a four digit hex number
            raise ValueError(f'trig_in_delay={trig_in_delay} out of bounds. Max value is 65535.')

        if np.remainder(trig_out_delay, 1):
            raise ValueError(f'trig_out_delay={trig_out_delay} must be an integer.')
        elif trig_out_delay > 65535:
            raise ValueError(f'trig_out_delay={trig_out_delay} out of bounds. Max value is 65535.')

        if np.remainder(charge_delay, 1) or charge_delay < 0:
            raise ValueError(f'charge_delay={charge_delay} must be a positive integer.')
        elif charge_delay > 65535:
            raise ValueError(f'charge_delay={charge_delay} out of bounds. Max value is 65535.')

        command_length = '09'
        command_id = '08'

        trig_in_delay_l, trig_in_delay_m = self.hexlm(trig_in_delay, 10)

        trig_out_delay = trig_out_delay * 10
        if trig_out_delay >= 0:
            trig_out_delay_l, trig_out_delay_m = self.hexlm(trig_in_delay)
        else:
            # What's the usecase of this? o_0
            complement = 65535 + trig_out_delay
            trig_out_delay_l, trig_out_delay_m = self.hexlm(complement)

        charge_delay_l, charge_delay_m = self.hexlm(charge_delay)

        nabyte1 = '00'
        nabyte2 = '00'

        command_bytes = [command_id, trig_in_delay_m, trig_in_delay_l, trig_out_delay_m, trig_out_delay_l,
                         charge_delay_m, charge_delay_l, nabyte1, nabyte2]

        return self.process_command(command_length, command_bytes, get_response=get_response)

    def set_mode(self, mode, current_dir, n_pulses_per_burst, ipi, baratio=1, get_response=False):
        """
        Sets the stimulation mode. This includes current directions, burst_pulses, and others.
        Note that you can use burst_pulses to send out multiple single pulses as a burst for each trigger-in.

        Parameters
        ----------
        mode : str
            Working mode, one of 'Standard','Power','Twin','Dual'
        current_dir : str
            Current direction of the stimulation. One of 'Normal', 'Reverse'.
        n_pulses_per_burst : int
            Biphasic pulses (= burst) per trigger in.
            Can be one of 2,3,4,5.
        ipi : int
            The inter pulse interval defines the duration between the beginning of the first pulse to the beginning of
            the second pulse in a burst.
        baratio: int
            When working in Twin Mode, the amplitude of the two pulses A and B are
            controlled in an adjustable ratio between 0.2-5.0. "Pulse B" is now adjusted to a selected
            percent ratio proportional to "Pulse A".
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        if mode.lower() == 'standard':
            mode_n = '00'
        elif mode.lower() == 'power':
            mode_n = '01'
        elif mode.lower() == 'twin':
            mode_n = '02'
        elif mode.lower() == 'dual':
            mode_n = '03'
        else:
            raise ValueError(f"mode={mode} unknown. Must be one of 'Standard','Power','Twin','Dual'.")

        command_length = '0B'
        command_id = '09'
        set_val = '01'
        raw_info, error = self.get_status_set_get()

        if error != 0:
            raise ValueError('Could not retrieve status from stimulator.')

        model = raw_info['Model']
        waveform = raw_info['Waveform']

        burst_pulse_index = self.parse_pulses_per_burst(n_pulses_per_burst)
        ipi_l, ipi_m = self.parse_ipi(ipi)
        baratio_l, baratio_m = self.parse_baratio(baratio)
        current_dir_index = self.parse_current_dir(current_dir)

        if self.flush_before_cmd:
            self.port.flushInput()

        command_bytes = [command_id, set_val, model, mode_n, current_dir_index, waveform, burst_pulse_index,
                         ipi_m, ipi_l, baratio_m, baratio_l]
        resp_len_exp = 14

        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def get_mode(self):
        """
        Gets stimulator mode information.

        Returns
        -------
         mode : str
            The stimulators mode, one of 'Standard', 'Power', 'Twin', 'Dual.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id, set_val, model, mode, current_dir, waveform, burst_pulses,
                         ipi_m, ipi_l, baratio_m, baratio_l]

        device_response, error = self.process_command(command_length, command_bytes, get_response=True, resp_len_exp=14)

        return device_response['Mode'], error

    def set_waveform(self, waveform, current_dir=None, n_pulses_per_burst=None, ipi=None, baratio=None,
                     get_response=False):
        """
        Sets the waveform.

        If current_dir, n_pulses_per_burst, ipi, baratios is not set it is read from the stimulator.
        This takes some time, so better set arguments accordingly.

        Parameters
        ----------
        waveform: str
            defines the desired waveform. Valid inputs in magventure:
            'Monophasic','Biphasic','HalfSine','BiphasicBurst'
        current_dir: str
            defines current direction of the device in the current status.
            Valid inputs in magventure:'Normal','Reverse'
        n_pulses_per_burst: int
            Biphasic Burst index in the current status of the device which can
            be 2,3,4, or 5 pulses in each stimulation
        ipi: int
            represents Inter Pulse Interval of the current status of the device
            which defines the duration between the beginning of the first pulse to the beginning of
            the second pulse.
        baratio: int
            when working in Twin Mode, the amplitude of the two pulses A and B are
            controlled in an adjustable ratio between 0.2-5.0. "Pulse B" is now adjusted to a selected
            percent ratio proportional to "Pulse A".
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
                Non-zero value indicates error code, or zero on success.
        """

        if waveform == 'Monophasic':
            waveform_n = '00'
        elif waveform == 'Biphasic':
            waveform_n = '01'
        elif waveform == 'HalfSine':
            waveform_n = '02'
        elif waveform == 'BiphasicBurst':
            waveform_n = '03'
        else:
            raise ValueError(f"waveform_n={waveform} invalid. Must be one of 'Monophasic', 'Biphasic',"
                             f"'HalfSine', 'BiphasicBurst")

        command_length = '0B'
        command_id = '09'
        set_val = '01'

        raw_info, error = self.get_status_set_get()
        if error != 0:
            raise ValueError('Could not retrieve status from stimulator.')

        model = raw_info['Model']
        mode = raw_info['Mode']

        current_dir_index = self.parse_current_dir(current_dir)
        burst_pulse_index = self.parse_pulses_per_burst(n_pulses_per_burst)
        ipi_l, ipi_m = self.parse_ipi(ipi)
        baratio_l, baratio_m = self.parse_baratio(baratio)

        if self.flush_before_cmd:
            self.port.flushInput()

        command_bytes = [command_id, set_val, model, mode, current_dir_index,
                         waveform_n, burst_pulse_index, ipi_m, ipi_l, baratio_m, baratio_l]
        resp_len_exp = 14
        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def parse_ipi(self, ipi):
        if ipi is None:
            ipi, _ = self.get_ipi()
            if ipi == '':
                warnings.warn('Cannot get IPI values. Setting to 100')
            ipi = 100
        if ipi < 10 or ipi > 100:
            raise ValueError(f'ipi={ipi} has to be within (10, 100) msec.')
        ipi_l, ipi_m = self.hexlm(ipi, 10)
        return ipi_l, ipi_m

    def get_waveform(self):
        """
        Gets the waveform from stimulator..

        Returns
        -------
         waveform : str
            The device' waveform.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """

        self.disconnect()
        self.connect()

        command_length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id, set_val, model, mode, current_dir,
                         waveform, burst_pulses, ipi_m, ipi_l, baratio_m, baratio_l]

        get_response = True
        resp_len_exp = 14
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        device_response = device_response['Waveform']

        return device_response, error

    def set_current_dir(self, current_dir, n_pulses_per_burst=None, ipi=None, baratio=None, get_response=False):
        """
        Sets the current direction.

        Parameters
        ----------
        current_dir : str
            Current direction of the stimulator, one of 'Normal', 'Reverse'.
        n_pulses_per_burst : int
            Biphasic pulses (= burst) per trigger in.
            Can be one of 2,3,4,5.
        ipi : int
            The inter pulse interval defines the duration between the beginning of the first pulse to the beginning of
            the second pulse in a burst.
        baratio : int
            When working in Twin Mode, the amplitude of the two pulses A and B are
            controlled in an adjustable ratio between 0.2-5.0. "Pulse B" is now adjusted to a selected
            percent ratio proportional to "Pulse A".
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """

        command_length = '0B'
        command_id = '09'
        set_val = '01'

        raw_info, error = self.get_status_set_get()
        if error != 0:
            raise ValueError('Could not retrieve information from stimulator.')

        model = raw_info['Model']
        mode = raw_info['Mode']
        waveform = raw_info['Waveform']

        ipi_l, ipi_m = self.parse_ipi(ipi)
        baratio_l, baratio_m = self.parse_baratio(baratio)
        current_dir_index = self.parse_current_dir(current_dir)
        burst_pulse_index = self.parse_pulses_per_burst(n_pulses_per_burst)

        if self.flush_before_cmd:
            self.port.flushInput()

        command_bytes = [command_id, set_val, model, mode,
                         current_dir_index, waveform, burst_pulse_index, ipi_m, ipi_l, baratio_m, baratio_l]
        resp_len_exp = 14

        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def get_current_dir(self):
        """
        Gets the current direction.


        Returns
        -------
         device_response : str
            The current direction, one of 'Normal' or 'Reversed'.
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id, set_val, model, mode, current_dir, waveform, burst_pulses, ipi_m, ipi_l, baratio_m,
                         baratio_l]

        get_response = True
        resp_len_exp = 14
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        device_response = device_response['CurrentDirection']

        return device_response, error

    def set_burst(self, n_pulses_per_burst, current_dir=None, ipi=None, baratio=None, get_response=False):
        """
        Sets the number of pulses per burst.

        If current_dir, ipi, or baratio is not set it is read from the stimulator.
        This takes some time, so better set arguments accordingly.

        Parameters
        ----------
        current_dir: str
            defines current direction of the device in the current status.
            Valid inputs in magventure:'Normal','Reverse'
        n_pulses_per_burst: int
            Biphasic Burst index in the current status of the device which can
            be 2,3,4, or 5 pulses in each stimulation
        ipi: int
            represents Inter Pulse Interval of the current status of the device
            which defines the duration between the beginning of the first pulse to the beginning of
            the second pulse.
        baratio: int
            when working in Twin Mode, the amplitude of the two pulses A and B are
            controlled in an adjustable ratio between 0.2-5.0. "Pulse B" is now adjusted to a selected
            percent ratio proportional to "Pulse A".
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '0B'
        command_id = '09'
        set_val = '01'

        raw_info, error = self.get_status_set_get()
        if error != 0:
            raise ValueError('Could Not Retrieve Required Info From the Device')

        model = raw_info['Model']
        mode = raw_info['Mode']
        waveform = raw_info['Waveform']

        ipi_l, ipi_m = self.parse_ipi(ipi)
        baratio_l, baratio_m = self.parse_baratio(baratio)
        current_dir_index = self.parse_current_dir(current_dir)
        burst_pulse_index = self.parse_pulses_per_burst(n_pulses_per_burst)

        if self.flush_before_cmd:
            self.port.flushInput()

        command_bytes = [command_id, set_val, model, mode, current_dir_index, waveform,
                         burst_pulse_index, ipi_m, ipi_l, baratio_m, baratio_l]

        resp_len_exp = 14
        return self.process_command(command_length, command_bytes,
                                    get_response=get_response, resp_len_exp=resp_len_exp)

    def parse_current_dir(self, current_dir):
        if current_dir is None:
            current_dir, _ = self.get_current_dir()
        if current_dir.lower() == 'normal':
            current_dir_index = '00'
        elif current_dir.lower() == 'reversed':
            current_dir_index = '01'
        elif current_dir in ['00', '01']:
            current_dir_index = current_dir
        else:
            raise ValueError(f"current_dir={current_dir} invalid. Must be one of 'Normal','Reversed'.")
        return current_dir_index

    def get_burst(self):
        """
        Sets the train parameters.

        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
                Non-zero value indicates error code, or zero on success.
        """

        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id, set_val, model, mode, current_dir, waveform,
                         burst_pulses, ipi_m, ipi_l, baratio_m, baratio_l]

        get_response = True
        resp_len_exp = 14
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        device_response = device_response['BurstPulsesIndex']
        return device_response, error

    def set_ipi(self, ipi, current_dir=None, n_pulses_per_burst=None, baratio=None, get_response=False):
        """
        Sets the interpulse interval.

        If current_dir, n_pulses_per_burst, or baratio is not set it is read from the stimulator.
        This takes some time, so better set arguments accordingly.

        Parameters
        ----------
        ipi: float
            Inter pulse interval in ms,  which defines the duration between
            the beginning of the first pulse to the beginning of the second pulse.
        current_dir: str
            Current direction of the stimulator, one of 'Normal', 'Reverse'.
        n_pulses_per_burst: int
            Biphasic Burst index in the current status of the device which can
            be 2, 3, 4, or 5 pulses in each stimulation.
        baratio: int
            when working in Twin Mode, the amplitude of the two pulses A and B are
            controlled in an adjustable ratio between 0.2-5.0. "Pulse B" is now adjusted to a selected
            percent ratio proportional to "Pulse A".
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
                Non-zero value indicates error code, or zero on success.
        """
        command_length = '0B'
        command_id = '09'
        set_val = '01'

        raw_info, error = self.get_status_set_get()
        if error != 0:
            raise ValueError('Could Not Retrieve Required Info From the Device')

        model = raw_info['Model']
        mode = raw_info['Mode']
        waveform = raw_info['Waveform']

        ipi_l, ipi_m = self.parse_ipi(ipi)
        baratio_l, baratio_m = self.parse_baratio(baratio)
        current_dir_index = self.parse_current_dir(current_dir)
        burst_pulse_index = self.parse_pulses_per_burst(n_pulses_per_burst)

        if self.flush_before_cmd:
            self.port.flushInput()

        command_bytes = [command_id, set_val, model, mode, current_dir_index,
                         waveform, burst_pulse_index, ipi_m, ipi_l, baratio_m, baratio_l]
        resp_len_exp = 14

        return self.process_command(command_length, command_bytes,
                                    get_response=get_response, resp_len_exp=resp_len_exp)

    def parse_baratio(self, baratio):
        if baratio is None:
            baratio, _ = self.get_baratio()

        return self.hexlm(baratio, 100)

    def get_ipi(self):
        """
        Gets interpulse interval msec.

        Returns
        -------
         interpulse interva, : float
            The interpulse in msec
         error : bool
            Non-zero value indicates error code, or zero on success.
        """

        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id,
                         set_val,
                         model,
                         mode,
                         current_dir,
                         waveform,
                         burst_pulses,
                         ipi_m,
                         ipi_l,
                         baratio_m,
                         baratio_l]

        get_response = True
        resp_len_exp = 14
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        return device_response['IPIvalue'], error

    def set_baratio(self, baratio, current_dir=None, n_pulses_per_burst=None, ipi=None, get_response=False):
        """
        Sets the B/A Ratio

        If current_dir, n_pulses_per_burst, or ipi is not set it is read from the stimulator.
        This takes some time, so better set arguments accordingly.

        Parameters
        ----------
        baratio : int
            When working in Twin Mode, the amplitude of the two pulses A and B are
            controlled in an adjustable ratio between 0.2-5.0. "Pulse B" is now adjusted to a selected
            percent ratio proportional to "Pulse A".
        current_dir : str
            Current direction of the stimulator, one of 'Normal', 'Reverse'.
        n_pulses_per_burst : int
            Biphasic pulses (= burst) per trigger in.
            Can be one of 2,3,4,5.
        ipi : float
            represents Inter Pulse Interval which defines the duration between
            the beginning of the first pulse to the beginning of the second pulse.
        get_response : bool
            Whether to request a response from the stimulator. Default: False.
            
        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
            Non-zero value indicates error code, or zero on success.
        """

        command_length = '0B'
        command_id = '09'
        set_val = '01'

        raw_info, error = self.get_status_set_get()
        if error != 0:
            raise ValueError('Could Not Retrieve Required Info From the Device')

        model = raw_info['Model']
        mode = raw_info['Mode']
        waveform = raw_info['Waveform']

        ipi_l, ipi_m = self.parse_ipi(ipi)
        baratio_l, baratio_m = self.parse_baratio(baratio)
        current_dir_index = self.parse_current_dir(current_dir)
        burst_pulse_index = self.parse_pulses_per_burst(n_pulses_per_burst)

        if self.flush_before_cmd:
            self.port.flushInput()

        command_bytes = [command_id, set_val, model, mode, current_dir_index, waveform,
                         burst_pulse_index, ipi_m, ipi_l, baratio_m, baratio_l]
        resp_len_exp = 14

        return self.process_command(command_length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def parse_pulses_per_burst(self, n_pulses_per_burst):
        if n_pulses_per_burst is None:
            n_pulses_per_burst, _ = self.get_burst()
        if n_pulses_per_burst == 2:
            burst_pulse_index = '03'
        elif n_pulses_per_burst == 3:
            burst_pulse_index = '02'
        elif n_pulses_per_burst == 4:
            burst_pulse_index = '01'
        elif n_pulses_per_burst == 5:
            burst_pulse_index = '00'
        elif n_pulses_per_burst in ['00', '01', '02', '03']:
            burst_pulse_index = n_pulses_per_burst
        else:
            raise ValueError(f"n_pulses_per_burst={n_pulses_per_burst} invalid. Must be one of 2, 3, 4, 5")
        return burst_pulse_index

    def get_baratio(self):
        """
        Gets the B/A Ratio

        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
                Non-zero value indicates error code, or zero on success.
        """

        if self.flush_before_cmd:
            self.port.flushInput()

        command_length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id, set_val, model, mode, current_dir, waveform,
                         burst_pulses, ipi_m, ipi_l, baratio_m, baratio_l]

        get_response = True
        resp_len_exp = 14
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        return device_response['BA_Ratio'], error

    def process_command(self, command_length, command_bytes, resp_len_exp=8, get_response=False):
        """
        Prepares the command to be sent to the stimulator.
        Start and end bytes are added, the crc for the command_bytes are computed,
        and everything is sent to the stimulator.

        Parameters
        ----------
        command_length : str
            Length of command to be sent to the stimulator, in bytes.

        command_bytes : list of str or str
            Stimulator command as bytestring list.

        resp_len_exp : int
            Length of stimulator response that one expects.

        get_response : bool or int
            Whether to request a response from the stimulator. Default: False.
            get_response = 2 or 3 returns raw_response.

        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if not self.port.is_open:
            self.connect()

        if type(command_bytes) is not list:
            command_bytes = [command_bytes]

        start_byte = 'FE'
        end_byte = 'FF'
        check_sum = self.calc_crc(command_bytes)

        if len(check_sum) == 1:
            check_sum = '0' + check_sum

        # send everything to the stimulator
        print(f"Before: {self.port.in_waiting}")
        print([int(i, 16) for i in [start_byte, command_length] +
               command_bytes + [check_sum, end_byte]])
        self.port.write(
            bytearray([int(i, 16) for i in [start_byte, command_length] +
                       command_bytes + [check_sum, end_byte]]))

        device_response, device_response_raw, error = None, None, None
        if get_response:
            if get_response == 2:
                time.sleep(self.sleep_long)
            else:
                time.sleep(self.sleep_short)
            read_data = self.port.read(resp_len_exp)
            while self.port.in_waiting > 0:
                read_data += self.port.read()

            if len(read_data) == resp_len_exp:
                device_response, device_response_raw = self.parse_response(read_data)
                error = 0
            elif len(read_data) == 0:
                device_response = 'Empty'
                error = 1
            elif len(read_data) < resp_len_exp:
                device_response = 'Too short'
                error = 1
            elif len(read_data) > resp_len_exp:
                device_response, device_response_raw = self.parse_response(read_data, only_last=False)
                error = 1

        if get_response in [2, 3]:
            device_response = device_response_raw

        return device_response, error

    def parse_response(self, read_data, only_last=True):
        """
        Parses the stimulator response.


        Parameters
        ----------
        read_data : bytes
            Bytestring. The raw response from the stimulator.
        only_last : bool
            Return only the last response if multiple responses are in read_data.
            If not, returns turn into lists of dict.


        Returns
        -------
         info : dict or list of dict
            The parsed response sent back from the device.
         info_raw : dict or list of dict
            The raw response sent back from the device.
        """
        # split stimulator response into single responses and add the last byte again
        last_byte = b'\xff'
        read_data_lst = read_data.split(last_byte)[:-1]
        read_data_lst = [resp + last_byte for resp in read_data_lst]
        raw_info_return, info_return = [], []
        for read_data in read_data_lst:
            info_raw = None
            if read_data[2] == 0 or read_data[2] == 5:  # status
                fourth_byte = MagVenture.bin_z(read_data[3])
                mode_bits = int(fourth_byte[6:8], 2)

                mode = MagVenture.parse_mode_bits(mode_bits)

                waveform_bits = int(fourth_byte[4:6], 2)

                waveform = MagVenture.parse_waveform_bit(waveform_bits)

                status_bit = int(fourth_byte[3], 2)
                status = MagVenture.parse_status_bit(status_bit)

                model_bits = int(fourth_byte[0:3], 2)
                model = MagVenture.parse_model_bit(model_bits)

                serial_no = int(hex(read_data[4])[2:] + hex(read_data[5])[2:] + hex(read_data[6])[2:])

                temperature = read_data[7]
                coil_type_no = read_data[8]
                amplitude_a = read_data[9]
                amplitude_b = read_data[10]

                if coil_type_no in self.coil_types.keys():
                    coil_type_no = self.coil_types[coil_type_no]
                elif self.show_coil_hint:
                    print(f"The connected coil type {coil_type_no} is unknown. \n"
                          f"Please consider contacting the software author with this coil type nr ({coil_type_no})\n"
                          f"and the coil name that is currently connected to "
                          f"the stimulator to\nimprove the toolbox."
                          f" Thanks.")
                    self.show_coil_hint = False

                if read_data[2] == 0:
                    info = {'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model,
                            'SerialNo': serial_no,
                            'Temperature': temperature,
                            'coilTypeNo': coil_type_no,
                            'amplitudePercentage_A': amplitude_a,
                            'amplitudePercentage_B': amplitude_b}

                    info_raw = {'Model': MagVenture.hex_z(model_bits),
                                'Mode': MagVenture.hex_z(mode_bits),
                                'Waveform': MagVenture.hex_z(waveform_bits)}

                else:  # read_data[2] == 5:
                    original_amplitude_a = read_data[11]
                    original_amplitude_b = read_data[12]
                    factor_amplitude_a = read_data[13]
                    factor_amplitude_b = read_data[14]

                    page_byte = read_data[15]

                    page = MagVenture.parse_page_bit(page_byte)

                    if read_data[15]:
                        train_orprotocol = 'Running'
                    else:
                        train_orprotocol = 'Stopped'

                    info = {'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model,
                            'Temperature': temperature,
                            'coilTypeNo': coil_type_no,
                            'amplitudePercentage_A': amplitude_a,
                            'amplitudePercentage_B': amplitude_b,
                            'originalAmplitudePercentage_A': original_amplitude_a,
                            'originalAmplitudePercentage_B': original_amplitude_b,
                            'factorAmplitudePercentage_A': factor_amplitude_a,
                            'factorAmplitudePercentage_B': factor_amplitude_b,
                            'Page': page,
                            'trainOrprotocolStatus': train_orprotocol}

            elif read_data[2] in [1, 2, 3, 6, 7, 8]:
                sixth_byte = MagVenture.bin_z(read_data[5])
                mode_bits = int(sixth_byte[6:8])
                mode = MagVenture.parse_mode_bits(mode_bits)

                waveform_bits = int(sixth_byte[4:6])
                waveform = MagVenture.parse_waveform_bit(waveform_bits)

                status_bit = int(sixth_byte[3])
                status = MagVenture.parse_status_bit(status_bit)

                model_bits = int(sixth_byte[0:3])
                model = MagVenture.parse_model_bit(model_bits)

                if read_data[2] == 1:  # Amplitude
                    amplitude_a = read_data[3]
                    amplitude_b = read_data[4]

                    info = {'amplitudePercentage_A': amplitude_a,
                            'amplitudePercentage_B': amplitude_b,
                            'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model}

                elif read_data[2] == 2:  # di/dt
                    di_dt_a = read_data[3]
                    di_dt_b = read_data[4]

                    info = {'didtPercentage_A': di_dt_a,
                            'didtPercentage_B': di_dt_b,
                            'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model}

                elif read_data[2] in [3, 6]:  # Temperature or Original Amplitude
                    temperature = read_data[3]
                    coil_type = read_data[4]

                    info = {'Temperature': temperature,
                            'coilTypeNo': coil_type,
                            'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model}

                elif read_data[2] == 7:  # Amplitude                 Factor
                    factor_amplitude_a = read_data[3]
                    factor_amplitude_b = read_data[4]

                    info = {'factorAmplitudePercentage_A': factor_amplitude_a,
                            'factorAmplitudePercentage_B': factor_amplitude_b,
                            'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model}

                elif read_data[2] == 8:  # Page and Train / Protocol Runnig status
                    page_byte = read_data[3]
                    page = MagVenture.parse_page_bit(page_byte)

                    train_sequence_status = read_data[4]
                    if train_sequence_status == 0:
                        train_sequence = 'Stopped'
                    elif train_sequence_status == 1:
                        train_sequence = 'Running'
                    else:
                        raise ValueError(f"train_sequence_status={train_sequence_status} unknown.")

                    info = {'Page': page,
                            'train_sequence_status': train_sequence,
                            'Mode': mode,
                            'Waveform': waveform,
                            'Status': status,
                            'Model': model}
                else:
                    raise ValueError(f"read_data[2]={read_data[2]} not understood.")

            elif read_data[2] == 4:  # MEP Min Max data

                mep_max_amp = int(MagVenture.bin_z(read_data[3]) +
                                  MagVenture.bin_z(read_data[5]) +
                                  MagVenture.bin_z(read_data[5]) +
                                  MagVenture.bin_z(read_data[6]))
                mep_min_amp = int(MagVenture.bin_z(read_data[7]) +
                                  MagVenture.bin_z(read_data[8]) +
                                  MagVenture.bin_z(read_data[9]) +
                                  MagVenture.bin_z(read_data[10]))
                mep_max_time = int(MagVenture.bin_z(read_data[11]) +
                                   MagVenture.bin_z(read_data[12]) +
                                   MagVenture.bin_z(read_data[13]) +
                                   MagVenture.bin_z(read_data[14]))

                info = {'MEPmaxAmplitude_uV': mep_max_amp,
                        'MEPminAmplitude_uV': mep_min_amp,
                        'MEPmaxTime_uS': mep_max_time}

            elif read_data[2] == 9:  # Get Response
                model_byte = read_data[4]
                mode_byte = read_data[5]
                current_dir_byte = read_data[6]
                waveform_byte = read_data[7]
                burst_pulses_index_byte = read_data[8]
                ipi_index_lsbbyte = read_data[9]
                ipi_index_msbbyte = read_data[10]
                baratio_index_byte = read_data[11]

                mode = MagVenture.parse_mode_bits(mode_byte)

                if current_dir_byte == 0:
                    current_dir = 'Normal'
                elif current_dir_byte == 1:
                    current_dir = 'Reversed'
                else:
                    raise ValueError(f"current_dir_byte={current_dir_byte} unknown.")

                waveform = MagVenture.parse_waveform_bit(waveform_byte)

                if burst_pulses_index_byte == 0:
                    burst_pulses_index = 5
                elif burst_pulses_index_byte == 1:
                    burst_pulses_index = 4
                elif burst_pulses_index_byte == 2:
                    burst_pulses_index = 3
                elif burst_pulses_index_byte == 3:
                    burst_pulses_index = 2
                else:
                    raise ValueError(f"burst_pulses_index_byte{burst_pulses_index_byte} unknown.")

                ipi_index = int(hex(ipi_index_msbbyte)[2:] + hex(ipi_index_lsbbyte)[2:], 16)
                ipi = ''
                ipi_l = ''
                ipi_m = ''
                ipi_flag = False

                if mode == 'Twin' or mode == 'Dual':
                    if 0 <= ipi_index <= 20:
                        ipi = 3000 - ipi_index * 100
                    elif 20 < ipi_index <= 30:
                        ipi = 1000 - (ipi_index - 20) * 50
                    elif 30 < ipi_index <= 70:
                        ipi = 500 - (ipi_index - 30) * 10
                    elif 70 < ipi_index <= 150:
                        ipi = 100 - (ipi_index - 70)
                    elif 150 < ipi_index <= 170:
                        ipi = 20 - (ipi_index - 150) * 0.5
                    elif 170 < ipi_index < 260:
                        ipi = 10 - (ipi_index - 170) * 0.1
                    elif ipi_index == 260:
                        ipi = 1
                    else:
                        raise ValueError(f"ipi_index={ipi_index} not understood.")
                    ipi_flag = True

                elif waveform == 'Biphasic Burst':
                    if 0 <= ipi_index <= 80:
                        ipi = 100 - ipi_index
                    elif 80 < ipi_index <= 100:
                        ipi = 20 - (ipi_index - 80) * 0.5
                    elif 100 < ipi_index <= 195:
                        ipi = 10 - (ipi_index - 100) * 0.1
                    else:
                        raise ValueError(f"ipi_index={ipi_index} not understood.")
                    ipi_flag = True

                baratio = 5 - baratio_index_byte * 0.05
                ipi_real = ipi
                baratio_real = baratio

                if ipi_flag:
                    ipi_l, ipi_m = MagVenture.hexlm(ipi, 10)
                baratio_l, baratio_m = MagVenture.hexlm(baratio, 100)

                info_raw = {'Model': MagVenture.hex_z(model_byte, 2),
                            'Mode': MagVenture.hex_z(mode_byte, 2),
                            'CurrentDirection': MagVenture.hex_z(current_dir_byte, 2),
                            'Waveform': MagVenture.hex_z(waveform_byte, 2),
                            'BurstPulsesIndex': MagVenture.hex_z(burst_pulses_index_byte, 2),
                            'IPIValue_MSB': ipi_m,
                            'IPIValue_LSB': ipi_l,
                            'BARatio_MSB': baratio_m,
                            'BARatio_LSB': baratio_l}

                info = {'Mode': mode,
                        'CurrentDirection': current_dir,
                        'Waveform': waveform,
                        'BurstPulsesIndex': burst_pulses_index,
                        'IPIvalue': ipi_real,
                        'BA_Ratio': baratio_real}
            else:
                raise ValueError(f"read_data[2]={read_data[2]} unknown.")
            raw_info_return.append(info_raw)
            info_return.append(info)

        if only_last:
            return info_return[-1], raw_info_return[-1]
        else:
            return info_return, raw_info_return

    @staticmethod
    def parse_page_bit(page_bit):
        if page_bit == 1:
            page = 'Main'
        elif page_bit == 2:
            page = 'Train'
        elif page_bit == 3:
            page = 'Trig'
        elif page_bit == 4:
            page = 'Config'
        elif page_bit == 6:
            page = 'Download'
        elif page_bit == 7:
            page = 'Protocol'
        elif page_bit == 8:
            page = 'MEP'
        elif page_bit == 13:
            page = 'Service'
        elif page_bit == 15:
            page = 'Treatment'
        elif page_bit == 16:
            page = 'Treat Select'
        else:
            raise ValueError(f"pagebyte={page_bit} not undersood.")
        return page

    @staticmethod
    def parse_status_bit(status_bit):
        if status_bit == 0:
            status = 'Disabled'
        elif status_bit == 1:
            status = 'Enabled'
        else:
            raise ValueError(f"status_bit={status_bit} unknown.")
        return status

    @staticmethod
    def parse_mode_bits(mode_bit):
        if mode_bit == 0:
            mode = 'Standard'
        elif mode_bit == 1:
            mode = 'Power'
        elif mode_bit == 2:
            mode = 'Twin'
        elif mode_bit == 3:
            mode = 'Dual'
        else:
            raise ValueError(f"mode_bits={mode_bit} unknown.")
        return mode

    @staticmethod
    def parse_waveform_bit(waveform_bit):
        if waveform_bit == 0:
            waveform = 'Monophasic'
        elif waveform_bit == 1:
            waveform = 'Biphasic'
        elif waveform_bit == 2:
            waveform = 'Half Sine'
        elif waveform_bit in [11, 3]:
            waveform = 'Biphasic Burst'

        else:
            raise ValueError(f"waveform_bits={waveform_bit} unknown.")
        return waveform

    @staticmethod
    def parse_model_bit(model_bit):
        if model_bit == 0:
            model = 'R30'
        elif model_bit == 1:
            model = 'X100'
        elif model_bit == 2:
            model = 'R30+Option'
        elif model_bit == 3:
            model = 'X100+Option'
        elif model_bit == 4:
            model = 'R30+Option+Mono'
        elif model_bit == 5:
            model = 'MST'
        else:
            raise ValueError(f"model_bits={model_bit} unknown.")
        return model

    def get_raw_info(self):
        """
        Gets all current raw information from device for set commands.


        Returns
        -------
         Information : dict
            Raw information from stimulator.

        """
        if self.flush_before_cmd:
            self.port.flushInput()

        length = '0B'
        command_id = '09'
        set_val = '00'
        model = '00'
        mode = '00'
        current_dir = '00'
        waveform = '00'
        burst_pulses = '00'
        ipi_m = '00'
        ipi_l = '00'
        baratio_m = '00'
        baratio_l = '00'

        command_bytes = [command_id, set_val, model, mode, current_dir, waveform, burst_pulses, ipi_m, ipi_l,
                         baratio_m, baratio_l]

        get_response = 2
        resp_len_exp = 14

        return self.process_command(length, command_bytes, get_response=get_response, resp_len_exp=resp_len_exp)

    def get_status_set_get(self, get_response=False):
        """
        # TODO: remove this and use status2()
        Get info from device in set/get commands

        Parameters
        ----------
        get_response : bool
            Whether to request a response from the stimulator. Default: False.

        Returns
        -------
         device_response : dict
            The response sent back from the device
         error : bool
            Non-zero value indicates error code, or zero on success.
        """
        if get_response:
            self.connect()

        command_length = '01'
        command_id = '00'
        command_bytes = command_id

        get_response = 3
        resp_len_exp = 13
        device_response, error = self.process_command(command_length, command_bytes,
                                                      get_response=get_response, resp_len_exp=resp_len_exp)

        return device_response, error

    @staticmethod
    def hexlm(val, fac=1, z=4):
        """
        Get LSB and MSB from hexified, zeropadded value.

        Parameters
        ----------
        val : float
        fac : int, default: 1
            Multiplication factor
        z : int, default: 4
            Zero padding to z

        Returns
        -------
        LSB : str
        MSB : str
        """

        val *= fac
        val = int(val)
        val = hex(val)[2:].zfill(z)  # zero padded to n digits, 0x remobed
        return val[2:4], val[0:2]  # LSB

    @staticmethod
    def bin_z(val, z=8):
        """
        Integer to binary conversion.
        Includes zero padding and stripping of the '0b' prefix.

        Example:
        MagVenture.bin_z(1,z=8) -> '00000001'
        Parameters
        ----------
        val : int
        z : int, default: 8
            Length of string to pad with zeros.

        Returns
        -------
        bin_val : str
        """
        return bin(val)[2:].zfill(z)

    @staticmethod
    def hex_z(val, z=2):
        return hex(val)[2:].zfill(z)
