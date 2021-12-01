from openbci_stream.utils import HDF5Reader
from matplotlib import pyplot as plt
import numpy as np


filename = 'record-10_28_21-22_10_49.R.h5'

with HDF5Reader(filename) as reader:
    tm = reader.timestamp
    mk = reader.markers
    data = reader.get_data()
    print(reader)


eeg
