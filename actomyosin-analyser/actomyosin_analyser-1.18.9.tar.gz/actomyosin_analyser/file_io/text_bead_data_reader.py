import numpy as np
import glob
import os
from ..model.bead_states import BeadStates


class TextBeadDataReader:

    def __init__(self, folder):
        self.coord_files = glob.glob(folder + "/bead_coords_*.txt")
        self.coord_files.sort()
        if len(self.coord_files) == 0:
            raise RuntimeError("No actin coordinates in folder '" + folder + "'")
        self.link_files = glob.glob(folder + "/bead_links_*.txt")
        self.link_files.sort()
        self.lines_in_files = np.ones(len(self.coord_files), dtype=np.int64)
        self.lines_in_files = self.lines_in_files * -1

        for i in range(len(self.coord_files)):
            coord_file = self.coord_files[i]
            fname, ext = os.path.splitext(coord_file)
            if os.path.isfile(fname + ".npy"):
                self.coord_files[i] = fname + ".npy"

        for j in range(len(self.link_files)):
            link_file = self.link_files[j]
            fname, ext = os.path.splitext(link_file)
            if os.path.isfile(fname + ".npy"):
                self.link_files[j] = fname + ".npy"

        self._open_files(0)

    def _open_files(self, i):
        if i >= len(self.coord_files):
            raise RuntimeError("index " + str(i) + " exceeds number of files")
        for j in range(i):
            if (self.lines_in_files[j] == -1):
                message = "Trying to open file " + str(i) + ", but file " \
                          + str(j) + " has never been opened.\n"
                message += "Files need to be opened sequentially to get"
                message += "the mapping of the time_step right."
                raise RuntimeError(message)
        if TextBeadDataReader._is_npy_file(self.coord_files[i]):
            self.array_current_file = np.load(self.coord_files[i])
        else:
            self.array_current_file = np.genfromtxt(self.coord_files[i])
        if TextBeadDataReader._is_npy_file(self.link_files[i]):
            self.array_current_links = np.load(self.link_files[i])
        else:
            self.array_current_links = np.genfromtxt(self.link_files[i], dtype=int)
        self.current_file = i
        self.lines_in_files[i] = self.array_current_file.shape[0]
        self.first_time_step_of_current_array = np.sum(self.lines_in_files[:i])

    def get_system_state_at_time_step(self, time_step):
        file_index = self._locate_file_containing_time_step(time_step)
        if (file_index == -1):
            raise RuntimeError("time_step " + str(time_step) + " is out of range")
        if self.current_file != file_index:
            self._open_files(file_index)
        coords_array = self.array_current_file[time_step - self.first_time_step_of_current_array]
        links_array = self.array_current_links[time_step - self.first_time_step_of_current_array]
        bead_links = BeadStates(links_array)
        return coords_array, bead_links

    def _locate_file_containing_time_step(self, time_step):
        _sum_lines = 0
        for i in range(len(self.lines_in_files)):
            if (self.lines_in_files[i] == -1):
                self._open_files(i)
            _sum_lines = np.sum(self.lines_in_files[:i + 1])
            if (_sum_lines > time_step):
                return i
        return -1

    def convert_text_files_to_npy(self):
        for txt_file in self.coord_files:
            fname, ext = os.path.splitext(txt_file)
            if ext != ".txt":
                continue
            a = np.loadtxt(txt_file)
            np.save(fname + ".npy", a)

        for txt_file in self.link_files:
            fname, ext = os.path.splitext(txt_file)
            if ext != ".txt":
                continue
            a = np.loadtxt(txt_file, dtype=int)
            np.save(fname + ".npy", a)

    def _is_npy_file(f):
        fname, ext = os.path.splitext(f)
        if ext == ".npy":
            return True
        return False
