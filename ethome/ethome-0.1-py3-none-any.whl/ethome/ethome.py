import os
import sys
import h5py
import argparse
import bvhtoolbox
import numpy as np
import pandas as pd
import sklearn as sk
import scipy.io as sio
import scipy.signal as scs
from device import Device
from utilities import npybvh
from DataBase import DataBase
from numpy.fft import fft, ifft, fft2, ifft2, fftshift
from utilities.mvnx import MVNX
import warnings

"""This aims to be a library designed to take human-based behavioural data 
(namely movement plus gaze data - people can file Pull Requests if they want to
 add other behavioural outputs later).

The Ethome class is based around the HDF5 file format specification - our aim 
with this is to make this as standards-compliant as possible, therefore not 
deviating from the standardised methods unless otherwise required.

The Ethome should be able to have the following, in order of priority:
- Device class should be able to save any arbitrary array size into itself
- synchronisation method based on dynamic time warping / cross-correlation?

O - a method of saving data into HDF5 (effectively just a wrapper around h5py 
functionality) (already done, save_dataset in device.py)

O - a method of returning data from HDF5 (effectively just a wrapper around h5py
 functionality) (already done, init in DataBase)

- a manual synchronisation method that takes a frame number and allows
 alignment based on the frame number

- a subsampling method to match the frequencies of the gaze and suit recordings
(use scipy.signal.resample)

- a method of exporting from Ethome format to CSV

o - an input method for intaking BVH files into Ethome format # started
o - Argparse methods for  CLI interaction and instantiation # started
- add quaternion calculations
"""


class Ethome(DataBase):
    """
    This is the base class to contain the custom Ethome structure.
    """

    def __init__(self,
                 annotation=None,
                 identifier=0,
                 frequency=60,
                 **kwargs):
        kwargs.update({"frequency": frequency})
        super().__init__(**kwargs)
        self.__devices = []
        # if annotation is not None:
        #     self.__annotation = annotation
        # self.__identifier = identifier
        # self.__external_link = {}

    def add_devices(self, **kwargs):
        
        for key, value in kwargs.items():
            if not isinstance(value, Device):
                raise ValueError(f"{key} is not a \"Device\" subclass")
            if key not in self.__devices:
                self.__devices.append(key)
        
        self.__dict__.update(kwargs)

    @property
    def devices(self):
        return self.__devices
    
    @property
    def annotation(self):
        return self.__annotation

    @property
    def identifier(self):
        return self.__identifier

    def sync_streams(self, *args):
        """
        A function utilising standardised numpy cross-correlations
        to synchronise behaviour streams together
        """
        try:
            if len(locals()) < 3:
                return np.correlate([arg for arg in args])
        except Exception as e:
            warnings.warn("you need more than one input argument to sync")
    
    def generate_reference_vector(self):
        device_vectors = []
        for device in self.__devices:
            device_vectors.append(self.device.times)
        for device in device_vectors:
            return max(len(device)) # need to fix the Device generate_time_vector first

    def save_all(self, filename):
        self.save_devices_dataset(filename)
        self.save_dataset(filename)

    def save_dataset(self, filename):
        *filepath, filename = filename.split(os.sep)
        filepath = os.sep.join(filepath)
        if filepath:
            orig_dir = os.getcwd()
            os.chdir(filepath)
        additional_dict = {
            "attrs": {
                "identifier": identifier
            },
            "dataset": {
                "annotation": annotation
            }
        }
        if self.__external_link:
            additional_dict["externalLink"] = self.__external_link
        self._save_dataset(
            f"Ethome_{filename}",
            **additional_dict
        )
        if filepath:
            os.chdir(orig_dir)

    def save_devices_dataset(self, filename):
        *filepath, filename = filename.split(os.sep)
        filepath = os.sep.join(filepath)
        if filepath:
            orig_dir = os.getcwd()
            os.chdir(filepath)
        for device in self.__devices:
            self.__external_link.update({device: f"{device}_{filename}"})
            self.__dict__[device].save_dataset(f"{device}_{filename}")
        if filepath:
            os.chdir(orig_dir)

    def list_folders(self, data):
        for _file in data:
            return None

    def load_data(self, data):
        if data.endswith('.mat'):
            try:
                sio.loadmat(data)
            except NotImplementedError:
                warnings.warn("MAT could not be loaded. Are you using pre-7.3 version?")
        else:
            _file = h5py.File(data, 'r')
            self.data = _file

    def resample_device(self, frequency, *args):
        """Use Scipy's resample function to resample an arbitrary
        number of devices to a set frequency
        """
        resampled_arrays = []
        for arg in args:
            if isinstance(arg, (np.ndarray, np.generic)):
                resampled_arrays.append(scs.resample(arg, frequency))
            else:
                raise TypeError("Not a Numpy array")
                pass
        self.frequency = frequency
        return resampled_arrays

    @staticmethod
    def parse_args(argv=None):
        # untested, will need to try it out
        parser = argparse.ArgumentParser(description="Ethome format for Human \
                                                      Behavioural Recordings")
        parser.add_argument('path', metavar="path", type=str, help="Filepath \
                                                        to existing recording")
        parser.add_argument('frequency', type=int, help="Sampling Frequency of \
                                                         recordings (Hz)")


if __name__ == "__main__":
    e = Ethome()
    e.parse_args()

