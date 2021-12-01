import numpy as np


class TextStackReader:
    def __init__(self, folder):
        self.beads_reader = _BeadsReader(folder + "/beads.txt")
        self.beads_reader.read()
        self.filaments_reader = _FilamentsReader(folder + "/filaments.txt")
        self.filaments_reader.read()


class _BaseReader:

    def __init__(self, fname):
        self.fname = fname
        self.t = None

    def read(self):
        f = open(self.fname, "rt")
        lines = f.readlines()

        t = []
        N = []

        i = 0
        while i < len(lines):
            t_i, N_i = self.parse_step_line(lines[i])
            t.append(t_i)
            N.append(N_i)
            self.parse_content_following_step_line(t_i, lines[i + 1: i + N_i + 1])
            i += N_i + 1
        self.t = np.array(t)

    def parse_content_following_step_line(self, t, content_lines):
        raise NotImplementedError("Abstract Base Class")

    @staticmethod
    def parse_step_line(step_line):
        split = step_line.split("\t")
        t = int(split[0].split("=")[1])
        N = int(split[1].split("=")[1])
        return t, N


class _FilamentsReader(_BaseReader):

    def __init__(self, fname):
        _BaseReader.__init__(self, fname)
        self.filaments = {}

    def parse_content_following_step_line(self, t, lines):
        N = len(lines)
        ids = np.empty(N, dtype=int)
        firsts = np.empty(N, dtype=np.int32)
        lasts = np.empty(N, dtype=np.int32)
        counts = np.empty(N, dtype=np.int32)
        for i, l in enumerate(lines):
            split = l.split("\t")
            ids[i] = int(split[0])
            firsts[i] = int(split[1])
            lasts[i] = int(split[2])
            counts[i] = int(split[3])
        self.filaments[t] = _Filaments(ids, firsts, lasts, counts)


class _BeadsReader(_BaseReader):

    def __init__(self, fname):
        _BaseReader.__init__(self, fname)
        self.beads = {}

    def parse_content_following_step_line(self, t, lines):
        N = len(lines)
        ids = np.empty(N, dtype=int)
        x = np.empty(N)
        y = np.empty(N)
        z = np.empty(N)
        links_prev = np.empty(N, dtype=np.int32)
        links_next = np.empty(N, dtype=np.int32)
        links_crossf = np.empty(N, dtype=np.int32)
        for i, l in enumerate(lines):
            split = l.split("\t")
            ids[i] = int(split[0])
            x[i] = float(split[1])
            y[i] = float(split[2])
            z[i] = float(split[3])
            links_prev[i] = int(split[4])
            links_next[i] = int(split[5])
            links_crossf[i] = int(split[6])
        b = _Beads(ids, x, y, z, links_prev, links_next, links_crossf)
        self.beads[t] = b


class _Filaments:
    def __init__(self, ids: np.ndarray,
                 firsts: np.ndarray, lasts: np.ndarray,
                 counts: np.ndarray):
        self.ids = ids
        self.firsts = firsts
        self.lasts = lasts
        self.counts = counts

    def __str__(self):
        s = "Data for {} filaments."
        return s.format(len(self.ids))

    def __repr__(self):
        return self.__str__()


class _Beads:

    def __init__(self, ids: np.ndarray,
                 x: np.ndarray, y: np.ndarray, z: np.ndarray,
                 links_prev: np.ndarray, links_next: np.ndarray,
                 links_crossf: np.ndarray):
        self.ids = ids
        self.x = x
        self.y = y
        self.z = z
        self.links_prev = links_prev
        self.links_next = links_next
        self.links_crossf = links_crossf

    def __str__(self):
        s = "Actins data consisting of {} beads."
        return s.format(len(self.x))

    def __repr__(self):
        return self.__str__()
