import numpy as np
import glob


class SegmentDataReader:

    def __init__(self, folder):
        self.files = glob.glob(folder + "actin_coords_*.txt")
        self.files.sort()
        if len(self.files) == 0:
            raise RuntimeError("No actin coordinates in folder '" + folder + "'")
        self.lines_in_files = np.ones(len(self.files), dtype=np.int64)
        self.lines_in_files = self.lines_in_files * -1
        self._open_file(0)

    def _open_file(self, i):
        if i >= len(self.files):
            raise RuntimeError("index " + str(i) + " exceeds number of files")
        for j in range(i):
            if (self.lines_in_files[j] == -1):
                message = "Trying to open file " + str(i) + ", but file "\
                          + str(j) + " has never been opened.\n"
                message += "Files need to be opened sequentially to get"
                message += "the mapping of the time_step right."
                raise RuntimeError(message)
        self.array_current_file = np.genfromtxt(self.files[i])
        if self.array_current_file.ndim == 1:
            self.array_current_file = self.array_current_file.reshape(
                self.array_current_file.shape + (1,))
        self.current_file = i
        self.lines_in_files[i] = self.array_current_file.shape[0]
        self.first_time_step_of_current_array = np.sum(self.lines_in_files[:i])

    def get_coordinates_at_time_step(self, time_step):
        file_index = self._locate_file_containing_time_step(time_step)
        if (file_index == -1):
            raise RuntimeError("time_step " + str(time_step) + " is out of range")
        if self.current_file != file_index:
            self._open_file(file_index)
        return self.array_current_file[time_step - self.first_time_step_of_current_array, :]

    def _locate_file_containing_time_step(self, time_step):
        _sum_lines = 0
        for i in range(len(self.lines_in_files)):
            if (self.lines_in_files[i] == -1):
                self._open_file(i)
            _sum_lines = np.sum(self.lines_in_files[:i + 1])
            if (_sum_lines > time_step):
                return i
        return -1
