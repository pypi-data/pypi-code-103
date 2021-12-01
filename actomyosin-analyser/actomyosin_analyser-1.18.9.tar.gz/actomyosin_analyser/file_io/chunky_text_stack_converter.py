from typing import Generator, Any, Tuple, List, Union, Dict
import numpy as np
import h5py
import ipdb
from .config_reader_beads import ConfigReaderBeads
from .text_stack_reader import (_FilamentsReader, _Beads, _Filaments)


class ChunkyTextStackConverter:

    def __init__(self, folder: str, chunk=50):
        self.folder = folder
        self.cfg_reader = ConfigReaderBeads(folder + '/config.json')
        self.h5_file = None
        self.freader = _FilamentsReader(folder + '/filaments.txt')
        self.freader.read()
        self.chunk_size = chunk
        self.breader = None

    def convert(self, fname_h5: str):
        self.h5_file = h5py.File(fname_h5)
        self.h5_file.attrs['FORMAT'] = "TEXT_STACK"

        config_content = open(self.folder + "/config.json", 'rt').read()
        self.h5_file.attrs['CONFIG'] = config_content

        filaments_array = self._convert_filaments_to_array()

        dset_filaments = self.h5_file.create_dataset("filaments", data=filaments_array,
                                                     compression='gzip', compression_opts=7)

        n_steps = filaments_array.shape[0]
        n_beads = filaments_array[:, :, 3].sum(1)
        n_beads_max = n_beads.max()

        print('n_steps =', n_steps)

        dset_bead_coords = self.h5_file.create_dataset("bead_coordinates",
                                                       shape=(n_steps, n_beads_max, 3),
                                                       compression='gzip',
                                                       compression_opts=7,
                                                       fillvalue=np.nan,
                                                       dtype='float64')

        dset_bead_links = self.h5_file.create_dataset("bead_links",
                                                      shape=(n_steps, n_beads_max, 3),
                                                      compression='gzip',
                                                      compression_opts=7,
                                                      fillvalue=-1,
                                                      dtype='int32')

        dset_bead_ids = self.h5_file.create_dataset('bead_ids',
                                                    shape=(n_steps, n_beads_max),
                                                    compression='gzip',
                                                    compression_opts=7,
                                                    fillvalue=-1,
                                                    dtype='int32')

        self.breader = _ChunkyBeadsReader(self.folder + '/beads.txt', self.chunk_size, n_beads_max)

        t_steps = []

        ti = 0
        for chunk_arrays in self.breader.read():
            ipdb.set_trace(context=5)
            t = chunk_arrays[0]
            ids = chunk_arrays[1]
            coords = chunk_arrays[2]
            links = chunk_arrays[3]

            t_steps.append(t)

            N = len(t)

            print("at chunk from {} to {}".format(ti, ti + N))

            dset_bead_ids[ti: ti + N] = ids
            dset_bead_coords[ti: ti + N] = coords
            dset_bead_links[ti: ti + N] = links
            ti = ti + N

        self.h5_file["steps"] = np.vstack(t_steps)
        self.h5_file.close()

    def _convert_filaments_to_array(self) -> np.ndarray:
        filaments_dict = self.freader.filaments
        N_max = self._determine_N_max_filaments(filaments_dict)
        filaments_array = np.full((len(filaments_dict.keys()), N_max, 4), -1, dtype=int)
        for i, ti in enumerate(sorted(filaments_dict.keys())):
            filaments = filaments_dict[ti]
            filaments_array[i, :len(filaments.ids), 0] = filaments.ids
            filaments_array[i, :len(filaments.ids), 1] = filaments.firsts
            filaments_array[i, :len(filaments.ids), 2] = filaments.lasts
            filaments_array[i, :len(filaments.ids), 3] = filaments.counts
        return filaments_array

    @staticmethod
    def _determine_N_max_filaments(filaments_dict: Dict[int, _Filaments]) -> int:
        N_max = 0
        for ti in filaments_dict:
            fils = filaments_dict[ti]
            if len(fils.ids) > N_max:
                N_max = len(fils.ids)
        return N_max


class _ChunkyBaseReader:

    def __init__(self, fname, chunksize=50):
        self.chunksize = chunksize
        self.fh = open(fname, 'rt')

    def read(self) -> Generator[List[np.ndarray], None, None]:
        while True:
            chunk_arrays = self._read_chunk()
            if not chunk_arrays:
                break
            yield chunk_arrays

    def _read_chunk(self) -> Union[List[np.ndarray], None]:
        count = 0
        t = []
        N = []
        data = []

        while count < self.chunksize:
            line = self.fh.readline()
            if line is None:
                break
            t_i, N_i = self.parse_step_line(line)
            t.append(t_i)
            N.append(N_i)
            data.append(self.parse_content_following_step_line([self.fh.readline() for i in range(N_i)]))
            count = count + 1
        if count == 0:
            return None
        return [np.array(t)] + self._data_list_to_chunk_array(data)

    def parse_content_following_step_line(self, content_lines) -> Any:
        raise NotImplementedError("Abstract Base Class")

    def _data_list_to_chunk_array(self, data: List[Any]) -> List[np.ndarray]:
        raise NotImplementedError("Abstract Base Class")

    @staticmethod
    def parse_step_line(step_line) -> Tuple[int, int]:
        split = step_line.split("\t")
        t = int(split[0].split("=")[1])
        N = int(split[1].split("=")[1])
        return t, N


class _ChunkyBeadsReader(_ChunkyBaseReader):

    def __init__(self, fname: str, chunksize: int, max_n_beads: int):
        _ChunkyBaseReader.__init__(self, fname, chunksize)
        self.max_n_beads = max_n_beads

    def parse_content_following_step_line(self, lines) -> _Beads:
        N = len(lines)
        ids = np.empty(N, dtype=int)
        x = np.empty(N)
        y = np.empty(N)
        z = np.empty(N)

        links_prev = np.empty(N, dtype=np.int16)
        links_next = np.empty(N, dtype=np.int16)
        links_crossf = np.empty(N, dtype=np.int16)
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

        return b

    def _data_list_to_chunk_array(self, beads_list: List[_Beads]) -> List[np.ndarray]:

        N = len(beads_list)
        coords_array = np.full((N, self.max_n_beads, 3), np.nan)
        link_array = np.full((N, self.max_n_beads, 3), -1, dtype=np.int32)
        bead_ids = np.full((N, self.max_n_beads), -1, dtype=int)

        for i, b in enumerate(beads_list):
            coords_array[i, :len(b.x), 0] = b.x
            coords_array[i, :len(b.x), 1] = b.y
            coords_array[i, :len(b.x), 2] = b.z
            link_array[i, :len(b.x), 0] = b.links_prev
            link_array[i, :len(b.x), 1] = b.links_next
            link_array[i, :len(b.x), 2] = b.links_crossf
            bead_ids[i, :len(b.x)] = b.ids
        return [bead_ids, coords_array, link_array]
