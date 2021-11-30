# -*- coding: utf-8 -*-

"""package fft_dev
brief     Mock 3562A device through GPIB-Ethernet adapter.
author    Benoit Dubois
copyright FEMTO Engineering, 2021
licence   GPL 3.0+
"""

import logging
import struct
import time
import numpy as np


class FftParam(object):
    """FftParam class, a container for FFT acquisition parameters.
    """

    def __init__(self):
        """Constructor.
        :returns: ""
        """
        self.function = ""
        self.n_elts = ""
        self.d_elts = ""
        self.channels = ""
        self.domain = ""
        self.volt = ""
        self.unity = ""
        self.unitx = ""
        self.is_float = ""
        self.is_complex = ""
        self.is_log = ""
        self.mode = ""
        self.rfs = ""
        self.ifs = ""
        self.dx = ""
        self.average = ""
        self.sfreq = ""
        self.decades = ""

    def __str__(self):
        """Return string representation of the instance of the class.
        :returns: String representation of the instance (str)
        """
        retval = "Function: code number 1\n"
        retval += "Data contains 3 elements among which 3 are displayed\n"
        retval += "Channel selected: 2\n"
        retval += "Domain type: 1\n"
        retval += "Volt: Vpeak\n"
        retval += "Y-axis units: Yunit\n"
        retval += "X-axis units: Xunit\n"
        retval += "Data type is float: True\n"
        retval += "Log data: True\n"
        retval += "Measurement mode: 1\n"
        retval += "Sampling frequency/2 (real): {:.0f}\n".format(6)
        retval += "Sampling frequency/2 (imag): {:.0f}\n".format(6)
        retval += "Delta X-axis^2: {:.6f}\n".format(1)
        retval += "Number of average: {:.0f}\n".format(1)
        retval += "Measurement starts at: 1 Hz\n"
        retval += "Measurement mades on 5 decades\n"
        return retval


# =============================================================================
class FftStream(object):
    """FftStream class, a container for FFT acquisition data stream.
    """

    def __init__(self, rawdata=None):
        """Constructor.
        :param rawdata: Raw data readed from device (str)
        :returns: None
        """
        self.param = FftParam()
        self.xdata = np.reshape([0, 1, 2], (1, -1)).T
        self.ydata = np.reshape([0, 2, 4], (1, -1)).T


# =============================================================================
class Fft3562aDevMock():
    """Class mocking Fft3562aDevPrologix class.
    """

    def __init__(self, ip, port, gpib_addr):
        """Constructor.
        :returns: None
        """
        pass

    def connect(self):
        """Connection process.
        :returns: None
        """
        pass

    def write(self, data):
        logging.info("write: " + str(data))

    def clear_hpib_interface(self):
        """Clear the HPIP interface (see p.8 of programming guide).
        :returns: None
        """
        pass

    def reset_3562(self):
        """Reset for 3562A analyzer.
        :returns: None
        """
        pass

    def get_id(self):
        """Returns identification string of device.
        :returns: identification string of device (str)
        """
        return "3562A"

    def dump_data_state(self):
        """Acquires internal state of FFT analyzer.
        Data are transfered from device in ASCII format.
        :returns: Data representing state of analyzer (str)
        """
        logging.info("Dump device state")
        logging.info("Dump --> Ok")
        return ""

    def dump_data_trace(self):
        """Acquires data trace displayed on FFT analyzer. Data are transfered
        from device in ANSI or ASCII format.
        :returns: Data representing active trace on analyzer display (str)
        """
        logging.info("Dump data trace")
        time.sleep(1.0)
        logging.info("Dump --> Ok")
        return ""

    @staticmethod
    def scale_data(data, data_range):
        """Scale data with the formula (see p.57 of programming guide):
            scaled_data = -4/3 * data * data_range * 32768 / 26028.55
        which can be simplified for implementation in the folowing manner:
            scaled_data = -131072 / 78085.65 * data * data_range
        :param data: array of value (np.array)
        :param data_range: range setting for the channel (float)
        :reeturns: scaled data value (np.array)
        """
        scaled_data = -131072 / 78085.65 * data * data_range
        return scaled_data

    def dump_time_capture(self):
        """Acquire time capture file of FFT analyzer (ie raw data).
        Data are transfered from device in ANSII format.
        For more informations, see p.67 3562A programming guide.
        :returns: Time capture from analyzer (str)
        """
        logging.info("Dump time capture")
        time.sleep(1.0)
        logging.info("Dump --> Ok")
        return ""
