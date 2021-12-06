import os
import h5py
import numpy as np
import pandas as pd
import scipy.io as sio

class DataBase():
    def __init__(self, 
                 data_file=None,
                 data=None, 
                 times=None, 
                 labels=None, 
                 frequency=60):
        if data_file:
            try:
                _file = sio.loadmat(data_file)
                self.__data = _file["data"]
                self.__times = _file["times"]
                self.__labels = _file["labels"]
                self.__frequency = _file["frequency"]
            except NotImplementedError:
                _file = h5py.File(data_file, "r")
                self.__data = _file["data"][()]
                self.__times = _file["times"][()]
                self.__labels = _file.attrs["labels"]
                self.__frequency = _file.attrs["frequency"]
                _file.close()
        else:
            self.__data = np.asanyarray(data)
            self.__times = np.asanyarray(times)
            self.__labels = np.asanyarray(labels)
            self.__frequency = np.asanyarray(frequency)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    @property
    def times(self):
        return self.__times

    @times.setter
    def times(self, times):
        self.__times = times

    @property
    def labels(self):
        return self.__labels

    @labels.setter
    def labels(self, labels):
        self.__labels = labels

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, frequency):
        self.__frequency = frequency

    def _save_dataset(self, filename, matlab=False, **kwargs):
        if os.path.exists(filename):
            print(f"File {filename} already exists")
            ans_count = 0
            while ans_count < 3:
                ans = input(f"Overwrite {filename}? [y/N]: ")
                ans = ans.strip().lower()
                if not ans or ans == "n":
                    return
                elif ans == "y":
                    print(f"Overwriting {filename}...")
                else:
                    print(f"Runtime issue")
                ans_count += 1
        if matlab:
            data_dict = {
                "data": self.__data,
                "times": self.__times,
                "labels": self.__labels,
                "frequency": self.__frequency
            }
            if "attrs" in kwargs:
                data_dict.update(kwargs["attrs"])
            if "dataset" in kwargs:
                data_dict.update(kwargs["dataset"])
            sio.savemat(filename, data_dict)
            return

        _file = h5py.File(filename, "w")
        if isinstance(self.__data, dict):
            for key, value in self.__data.items():
                _file.create_dataset(key, data=value)
        else:
            _file.create_dataset("data", data=np.asanyarray(self.__data))
        _file.create_dataset("times", data=np.asanyarray(self.__times))
        _file.attrs["labels"] = self.__labels
        _file.attrs["frequency"] = self.__frequency
        if "attrs" in kwargs:
            for key, value in kwargs["attrs"].items():
                _file.attrs[key] = value
        if "dataset" in kwargs:
            for key, value in kwargs["dataset"].items():
                _file.create_dataset(key, data=value)
        if " externalLink" in kwargs:
            for key, value in kwargs["dataset"].items():
                _file[key] = h5py.ExternalLink(value, "/")
        _file.close()

    def CSV_to_H5(self, filename):
        df = pd.read_csv(filename)
        return df.to_hdf()