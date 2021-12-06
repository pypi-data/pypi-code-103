import numpy as np
import datetime
import sys
from DataBase import DataBase
from scipy.fft import fft, ifft, fftshift

class Device(DataBase):
    """
        An abstract device class - all equipment that we use for human 
        behavioural recordings, like Motion Capture Suits, Glasses for Gaze 
        recordings, EEG etc. will inherit from this class, so we keep just base 
        methods universal to all devices in here, like syncStreams, 
        generateTimeVector, etc.
        
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_time_vector(self, *args):
        """Takes an arbitrary number of numpy arrays, finds the max 
        across the number of rows, and divides by the sampling frequency
        to generate a time vector.
        """
        holding_list = []
        if self.times:
            #Needs error handling here to check what format the existing time
            #vector is in, and convert if necessary
            return
        if not args:
            raise ValueError("You need to supply a numpy array.")
        for arg in args:
            holding_list.append(arg)
        if not self.data:
            raise ValueError("Must contain data to infer vector from.")
        else:
            self.times = (max(self.data.shape) / self.frequency)
            #assumes the longest axis is your time axis
            # returns the time vector in seconds
        return    

    def FFT_cross_correlate(self, stream1, stream2):
        try:
            assert np.shape(self.stream1[0]) == 1
        except ValueError:
            print('Stream 1 not 1-dimensional array')
        try:
            assert np.shape(self.stream2[0]) == 1
        except ValueError:
            print ('Stream 2 not 1-dimensional array')
        
        f1 = fft(self.stream1)
        f2 = fft(np.flipud(self.stream2))
        cc = np.real(ifft(f1 * f2))
        return fftshift(cc)

    def compute_shift(self, stream1, stream2):
        assert np.shape(self.stream2[0]) == np.shape(self.stream2[0])
        c = self.FFT_cross_correlate( self.stream1, self.stream2)
        assert len(c) == np.shape(self.stream1[0])
        zero_index = int(np.shape(self.stream1[0]) / 2) - 1
        shift = zero_index - np.argmax(c)
        return shift

    def save_dataset(self, filename):
        self._save_dataset(filename)
