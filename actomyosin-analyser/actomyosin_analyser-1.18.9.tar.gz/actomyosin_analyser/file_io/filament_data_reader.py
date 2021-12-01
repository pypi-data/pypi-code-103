import numpy as np
import csv
import glob


class FilamentDataReader:

    def __init__(self, folder):
        self.coord_files = glob.glob(folder + "/filament_coords_*.txt")
        self.coord_files.sort()        
        if len(self.coord_files) == 0:
            raise RuntimeError("No actin coordinates in folder '" + folder + "'")
        self.status_files = glob.glob(folder + "/filament_status_*.txt")
        self.status_files.sort()
        self.lines_in_files = np.ones(len(self.coord_files), dtype=np.int64)
        self.lines_in_files = self.lines_in_files * -1
        self._open_files(0)

    def _open_files(self, i):
        if i >= len(self.coord_files):
            raise RuntimeError("index " + str(i) + " exceeds number of files")
        for j in range(i):
            if (self.lines_in_files[j] == -1):
                message = "Trying to open file " + str(i) + ", but file "\
                          + str(j) + " has never been opened.\n"
                message += "Files need to be opened sequentially to get"
                message += "the mapping of the time_step right."
                raise RuntimeError(message)
        file_handle = open(self.coord_files[i], "r")
        datareader = csv.reader(file_handle)
        self.lists_current_file = []
        for row in datareader:
            if not row:
                self.lists_current_file.append([])
            else:
                self.lists_current_file.append(
                    [float(elem) for elem in row[0].split()])
        self.lists_current_status_file = []
        file_handle_status = open(self.status_files[i], "r")
        datareader_status = csv.reader(file_handle_status)
        for row in datareader_status:
            if not row:
                self.lists_current_status_file.append([])
            else:
                self.lists_current_status_file.append(
                    [int(elem) for elem in row[0].split()])
        self.current_file = i
        self.lines_in_files[i] = len(self.lists_current_file)
        self.first_time_step_of_current_array = np.sum(self.lines_in_files[:i])

    def get_coordinates_at_time_step(self, time_step):
        file_index = self._locate_file_containing_time_step(time_step)
        if (file_index == -1):
            raise RuntimeError("time_step " + str(time_step) + " is out of range")
        if self.current_file != file_index:
            self._open_files(file_index)
        data_array = np.array(
            self.lists_current_file[time_step - self.first_time_step_of_current_array])
        status_array = np.array(
            self.lists_current_status_file[time_step - self.first_time_step_of_current_array])
        return data_array, status_array

    def _locate_file_containing_time_step(self, time_step):
        _sum_lines = 0
        for i in range(len(self.lines_in_files)):
            if (self.lines_in_files[i] == -1):
                self._open_files(i)
            _sum_lines = np.sum(self.lines_in_files[:i + 1])
            if (_sum_lines > time_step):
                return i
        return -1
