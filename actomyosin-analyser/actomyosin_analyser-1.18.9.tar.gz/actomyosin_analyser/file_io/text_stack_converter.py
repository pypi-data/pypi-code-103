import numpy as np
import h5py
from typing import Tuple, Dict
from .text_stack_reader import TextStackReader, _Beads, _Filaments
from .config_reader_beads import ConfigReaderBeads


class TextStackConverter:

    def __init__(self, folder: str):
        self.folder = folder
        self.ts_reader = TextStackReader(folder)
        self.cfg_reader = ConfigReaderBeads(folder + "/config.json")
        self.h5_file = None

    def convert(self, fname_h5: str):
        self.h5_file = h5py.File(fname_h5)
        self.h5_file.attrs['FORMAT'] = "TEXT_STACK"

        config_content = open(self.folder + "/config.json", 'rt').read()
        self.h5_file.attrs['CONFIG'] = config_content

        bead_ids, bead_array, link_array = self._convert_beads_to_arrays()
        filaments_array = self._convert_filaments_to_array()

        dset_bead_coords = self.h5_file.create_dataset("bead_coordinates", data=bead_array,
                                                       compression='gzip', compression_opts=7)
        dset_bead_links = self.h5_file.create_dataset("bead_links", data=link_array,
                                                      compression='gzip', compression_opts=7)
        dset_filaments = self.h5_file.create_dataset("filaments", data=filaments_array,
                                                     compression='gzip', compression_opts=7)
        dset_bead_ids = self.h5_file.create_dataset("bead_ids", data=bead_ids,
                                                    compression='gzip', compression_opts=7)

        self.h5_file["steps"] =\
            np.array(sorted(self.ts_reader.beads_reader.beads.keys()))

        self.h5_file.close()
        
    def _convert_beads_to_arrays(self) \
        -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        beads_dict = self.ts_reader.beads_reader.beads
        N_max = self._determine_N_max_beads(beads_dict)
        coords_array = np.full((len(beads_dict.keys()), N_max, 3), np.nan)
        link_array = np.full((len(beads_dict.keys()), N_max, 3), -1, dtype=np.int32)
        bead_ids = np.full((len(beads_dict.keys()), N_max), -1, dtype=int)
        for i, ti in enumerate(sorted(beads_dict.keys())):
            beads = beads_dict[ti]
            coords_array[i, :len(beads.x), 0] = beads.x
            coords_array[i, :len(beads.x), 1] = beads.y
            coords_array[i, :len(beads.x), 2] = beads.z
            link_array[i, :len(beads.x), 0] = beads.links_prev
            link_array[i, :len(beads.x), 1] = beads.links_next
            link_array[i, :len(beads.x), 2] = beads.links_crossf
            bead_ids[i, :len(beads.x)] = beads.ids
        return bead_ids, coords_array, link_array
            

    def _convert_filaments_to_array(self) -> np.ndarray:
        filaments_dict = self.ts_reader.filaments_reader.filaments
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
    def _determine_N_max_beads(beads_dict: Dict[int, _Beads]) -> int:
        N_max = 0
        for ti in beads_dict:
            beads = beads_dict[ti]
            if len(beads.x) > N_max:
                N_max = len(beads.x)
        return N_max

    @staticmethod
    def _determine_N_max_filaments(filaments_dict: Dict[int, _Filaments]) -> int:
        N_max = 0
        for ti in filaments_dict:
            fils = filaments_dict[ti]
            if len(fils.ids) > N_max:
                N_max = len(fils.ids)
        return N_max
        
