from typing import Tuple, Dict, List, Any, Union
import os
import json
import numpy as np
import h5py
import readdy
import toml

from .components import Filament, LinksArray
from .periodic_boundaries import get_minimum_image_projection

_FILAMENT_PARTICLES = ['tail', 'core', 'head', 'motor']


class DataReader:
    
    def __init__(self, data_file: str, links_file: str=None, parameter_file: str=None,
                 n_parts: int=0):
        self._particle_list_read_from = None
        self._particle_list = None
        self.parts = n_parts > 0
        self.n_parts = n_parts
        self._n_frames_per_part = None
        self.data_file = data_file
        self.data_dir = os.path.split(data_file)[0]
        if links_file is None:
            links_file = os.path.join(self.data_dir, 'links.h5')
        self.links_file = links_file
        self._parameter_toml = None
        self._parameter_json = None
        self._get_parameter_file(parameter_file)

    def _get_parameter_file(self, parameter_file):
        if parameter_file is None:
            data_dir = self.data_dir
            if self.parts:
                data_dir = data_dir.format(0)
            parameter_toml = os.path.join(data_dir, 'config.toml')
            if os.path.exists(parameter_toml):
                self._parameter_toml = parameter_toml
            else:
                parameter_json = os.path.join(data_dir, 'parameters.json')
                if os.path.exists(parameter_json):
                    self._parameter_json = parameter_json
                else:
                    raise FileNotFoundError("No parameter file 'config.toml' or 'parameters.json' "
                                            f"found in {self.data_dir}")
        else:
            ext = os.path.splitext(parameter_file)
            if ext == '.toml':
                self._parameter_toml = parameter_file
            elif ext == '.json':
                self._parameter_json = parameter_file
            else:
                raise RuntimeError("Expects .json or .toml file as parameter_file.")

    def read_dt(self) -> float:
        """Read time Step from parameter file."""
        if self._parameter_json:
            return self._read_parameter_json(['dt'])
        return self._read_parameter_toml(['run-parameters', 'dt'])

    def read_n_frames(self) -> int:
        """
        Read number of frames that were recorded of the simulation.
        """
        if not self.parts:
            n_steps = self.read_parameter('n_steps')
            interval = self.read_parameter('observation_interval')
            n_frames = n_steps // interval + 1
            return n_frames
        n = self._read_n_frames_per_part()
        return (n-1) * self.n_parts + 1

    def get_n_non_filament_particles(self) -> int:
        """
        Defer number of non-filament particles from the array of particle types.
        Currently, non-filament particles can't spawn or vanish during simulation,
        they have to be added before the start. Furthermore, they have to be added
        before any filament particles. So the number of non-filament particles 
        can simply be counted, because they have to be the first items of the 
        particle types array.
        """
        map_types, types = self.read_particle_types()
        map_types_inverted = {}
        for label, number in zip(map_types.keys(), map_types.values()):
            map_types_inverted[number] = label
            
        t0 = types[0]        
        for i in range(len(types)):
            if map_types_inverted[t0[i]] in _FILAMENT_PARTICLES:
                return i
        raise RuntimeError("Encountered no filament particles! Something is wrong.")

    def get_non_filament_coordinates(self, minimum_image: bool) -> np.ndarray:
        pos = self.read_particle_positions(minimum_image)
        offset = self.get_n_non_filament_particles()
        return pos[:, :offset]

    def get_filaments(
            self,
            frame_idx: int
    ) -> Tuple[List[Filament], Union[LinksArray, None]]:
        """
        Get filaments at frame ``frame_idx``. Can't handle simulations that were
        split into parts. For split simulations use DataReader.get_filaments_all
        instead.
        """
        if self.parts:
            fil = self.get_filaments_all()[frame_idx]
            return fil, None
        return self._get_filaments(frame_idx)

    def _get_filaments(self, t_idx: int) -> Tuple[List[Filament], LinksArray]:
        links_t = self._read_links(t_idx)
        ids_t = self._read_filament_ids(t_idx)
        tails_t = self._read_filament_tails(t_idx)
        filaments = Filament.generate_filaments_from_link_array(ids_t, tails_t, links_t)
        return filaments, links_t

    def get_filaments_all(self) -> List[List[Filament]]:
        """
        Get filaments for all frames.

        :return: A nested list of Filament instances. The outer list has
                 one item per frame. The inner lists contain one item per
                 filament present in the simulated system at that
                 point in time. The items of these lists are Filament instances,
                 simple data structures that store information like the ordered
                 beads that constitute this filament and which of those beads
                 are motors/cross-links.
        """
        if self.parts:
            return self._get_filaments_all_parts()
        with h5py.File(self.links_file, 'r') as f:
            n_frames = f.attrs['n_datasets']
        return [self.get_filaments(n)[0] for n in range(n_frames)]

    def get_filament_coordinates(self, minimum_image: bool) -> np.ndarray:
        all_particle_coordinates = self.read_particle_positions(minimum_image)
        n_non_filament = self.get_n_non_filament_particles()
        return all_particle_coordinates[:, n_non_filament:]

    def _get_filaments_all_parts(self):
        maps_bead, maps_fil = self._get_maps_for_parts()
        filaments_all = []
        n_frames = (self._read_n_frames_per_part()-1) * self.n_parts + 1
        current_part = self.n_parts-1
        current_map_from = maps_bead[current_part]
        current_map_to = np.full_like(current_map_from, -1)
        for a, b in enumerate(current_map_from):
            current_map_to[b] = a
        assert (current_map_to != -1).all()
        for t in range(n_frames-1, -1, -1):
            p, _ = self._get_part_and_frame(t)
            if p != current_part:
                current_part = p
                current_map_from = maps_bead[current_part]
                current_map_to = np.full_like(current_map_from, -1)
                for a, b in enumerate(current_map_from):
                    current_map_to[b] = a
                assert (current_map_to != -1).all()
                DataReader._apply_map_on_filaments(current_map_to, filaments_all)
            filaments_t, links = self._get_filaments(t)
            DataReader._apply_map_on_filaments(current_map_to, [filaments_t])
            filaments_all.append(filaments_t)
        filaments_all.reverse()
        return filaments_all

    def get_links_all(self) -> List[LinksArray]:
        """
        Get links for all frames.

        :return: List of np.arrays. Each array holds information
                 on how beads are linked (i.e. which beads build up
                 which filament, which filaments are connected via
                 beads). See documentation for more info on LinkArrays.
        """

        if self.parts:
            return self._get_links_all_parts()

        with h5py.File(self.links_file, 'r') as f:
            n_frames = f.attrs['n_datasets']
        return [self.read_links(n) for n in range(n_frames)]
        
    def _get_links_all_parts(self) -> List[LinksArray]:
        maps_bead, _ = self._get_maps_for_parts()
        links_all = []
        n_frames = self.read_n_frames()
        current_part = self.n_parts-1
        current_map_from = maps_bead[current_part]
        current_map_to = np.full_like(current_map_from, -1)
        for a, b in enumerate(current_map_from):
            current_map_to[b] = a
        assert (current_map_to != -1).all()

        for t in range(n_frames-1, -1, -1):
            p, _ = self._get_part_and_frame(t)
            if p != current_part:
                current_part = p
                current_map_from = maps_bead[current_part]
                current_map_to = np.full_like(current_map_from, -1)
                for a, b in enumerate(current_map_from):
                    current_map_to[b] = a
                assert (current_map_to != -1).all()
                links_all = DataReader._apply_map_on_links(current_map_from, current_map_to,
                                                           links_all)
            links = self._read_links(t)
            links = DataReader._apply_map_on_links(current_map_from, current_map_to, [links])[0]
            links_all.append(links)
        links_all.reverse()
        return links_all

    @staticmethod
    def _apply_map_on_filaments(map_beads: np.ndarray, filaments_all: List[List[Filament]]):
        for filaments in filaments_all:
            for fil in filaments:
                fil.items = list(map_beads[fil.items])
                fil.motors = list(map_beads[fil.motors])

    @staticmethod
    def _apply_map_on_links(map_beads_from: np.ndarray, map_beads_to: np.ndarray,
                            links_all: List[LinksArray]) -> List[LinksArray]:
        links_mapped = []

        for links in links_all:
            links_new = links[map_beads_from]
            links_new[links_new != -1] = map_beads_to[links_new[links_new != -1]]
            links_mapped.append(links_new)
            
        return links_mapped
        
    def _get_maps_for_parts(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        maps_bead = []
        maps_fil  = []
        for p in range(self.n_parts):
            map_b = np.load(
                os.path.join(self.data_dir, 'map_beads_previous_part.npy').format(p)
            )
            map_f = np.load(
                os.path.join(self.data_dir, 'map_filaments_previous_part.npy').format(p)
            )
            maps_bead.append(map_b)
            maps_fil.append(map_f)
        return maps_bead, maps_fil

    def get_motor_count(self) -> np.ndarray:
        """
        Get count of motors or cross-links for each frame.
        """
        n_frames = self.read_n_frames()
        counts = np.empty(n_frames, dtype=int)
        if self.parts:
            links = self.get_links_all()
            for f in range(n_frames):
                links_f = links[f]
                counts[f] = (links_f[:, 2] != -1).sum()
            return counts
        for f in range(n_frames):
            links = self.read_links(f)
            counts[f] = (links[:, 2] != -1).sum()
        return counts

    def read_links(self, frame_idx: int) -> LinksArray:
        """
        Read links at frame ``frame_idx``. Can't handle simulation data
        that was split into parts. For split data, use
        DataReader.get_links_all instead.
        """
        if self.parts:
            msg = "This method can't be used for simulation data split into parts. "
            msg += "Use DataReader.get_links_all instead."
            raise RuntimeError(msg)
        return self._read_links(frame_idx)

    def _read_links(self, frame_idx: int) -> LinksArray:
        if self.parts:
            part_idx, frame_idx_local = self._get_part_and_frame(frame_idx)
            links_h5 = h5py.File(self.links_file.format(part_idx), 'r')
            frame_idx = frame_idx_local
        else:
            links_h5 = h5py.File(self.links_file, 'r')
        group = links_h5['links']
        k0 = list(group.keys())[0]
        template = "{:0" + str(len(k0)) + "}"        
        return group[template.format(frame_idx)][:]

    def _read_filament_ids(self, frame: int) -> np.ndarray:
        dataset_name = 'ids'
        return self._read_dataset_from_filaments_group(dataset_name, frame)

    def _read_filament_tails(self, frame: int):
        dataset_name = 'tails'
        return self._read_dataset_from_filaments_group(dataset_name, frame)

    def _read_dataset_from_filaments_group(self, dataset_name: str, frame: int) -> np.ndarray:
        """
        From links file, access the group 'filaments' and retrieve given dataset.
        """
        if self.parts:
            n = self._read_n_frames_per_part()
            p = frame // n
            frame = frame % n
            links_file = self.links_file.format(p)
        else:
            links_file = self.links_file
        with h5py.File(links_file, 'r') as h5f:
            group = h5f['filaments']
            k0 = list(group.keys())[0]
            template = "{:0" + str(len(k0)) + "}"
            return group[template.format(frame)][dataset_name][:]

    def _get_part_and_frame(self, frame_idx: int) -> Tuple[int, int]:
        n_frames_part = self._read_n_frames_per_part()
        if frame_idx == 0:
            return 0, 0
        part_idx = (frame_idx - 1) // (n_frames_part - 1)
        frame_idx_local = 1 + ((frame_idx - 1) % (n_frames_part - 1))
        return part_idx, frame_idx_local
    
    def _read_n_frames_per_part(self):
        if not self.parts:
            raise RuntimeError("This method only works for simulations splitted in parts.")
        if self._n_frames_per_part is not None:
            return self._n_frames_per_part
        n_steps = self.read_parameter('n_steps')
        interval = self.read_parameter('observation_interval')
        n_frames = n_steps // interval + 1
        self._n_frames_per_part = n_frames
        return self._n_frames_per_part

    def read_particle_positions(self, minimum_image=False) -> np.ndarray:
        """
        Reads particle positions from trajectory recording.
        """
        if not self.parts:
            traj = readdy.Trajectory(self.data_file)
            return self._read_particle_positions_single_traj(traj, minimum_image)
        traj = None
        positions = []
        maps = []
        nmax = 0
        n_non_fil = self.get_n_non_filament_particles()
        for p in range(self.n_parts):
            traj = readdy.Trajectory(self.data_file.format(p))
            pos = self._read_particle_positions_single_traj(traj, minimum_image)
            map_bead_idx = np.load(
                os.path.join(self.data_dir, 'map_beads_previous_part.npy').format(p)
            )
            maps.append(map_bead_idx)
            pos_mapped = np.empty_like(pos)
            pos_mapped[:, :n_non_fil] = pos[:, :n_non_fil]
            pos_mapped[:, n_non_fil:] = pos[:, map_bead_idx+n_non_fil]
            # go through previous maps in reverse order
            # to map on same ordering as in very first part
            for map_i in maps[-2::-1]:
                pos_mapped[:, n_non_fil:] = pos_mapped[:, map_i+n_non_fil]
            positions.append(pos_mapped)
            nmax = max(nmax, pos.shape[1])
        n_frames_pp = self._read_n_frames_per_part()
        n_frames = (n_frames_pp-1) * self.n_parts + 1
        pos_all = np.full((n_frames, nmax, 3), np.nan)

        for p in range(self.n_parts):
            posp = positions[p]
            if p == 0:
                pos_all[:n_frames_pp, :posp.shape[1]] = posp
                continue
            pos_all[(n_frames_pp-1) * p + 1: (n_frames_pp-1) * (p+1) + 1, :posp.shape[1]] = posp[1:]

        if minimum_image:
            return pos_all

        pos_all = revert_minimum_image_projection(pos_all, traj.box_size)
            
        return pos_all

    @staticmethod
    def _read_particle_positions_single_traj(
            traj: readdy.Trajectory,
            minimum_image: bool
    ) -> np.ndarray:
        pos_list = traj.read()
        min_id, max_id = DataReader._get_min_max_id(pos_list)
        shape = (len(pos_list), max_id + 1, 3)
        pos = np.full(shape, np.nan)
        for t in range(shape[0]):
            pos_t = pos_list[t]
            for particle in pos_t:
                pos[t, particle.id] = particle.position
        pos = pos[:, min_id:]
        if minimum_image:
            pos[0, :, :] = get_minimum_image_projection(traj.box_size, pos[0, :, :])
            return pos
        pos = revert_minimum_image_projection(pos, traj.box_size)
        return pos

    def _get_index_offset(self):
        try:
            idx_offset = self.read_parameter('filament_handler_idx_offset')
        except KeyError:
            idx_offset = self.read_parameter('filament-handler', 'index_offset')
        return idx_offset

    @staticmethod
    def _get_min_max_id(trajectory_list) -> Tuple[int, int]:
        min_id = np.inf
        max_id = 0
        for traj_t in trajectory_list:
            for particle in traj_t:
                if particle.id > max_id:
                    max_id = particle.id
                if particle.id < min_id:
                    min_id = particle.id
        return min_id, max_id

    def read_particle_types(self) -> Tuple[Dict[str, int], np.ndarray]:
        if self.parts:
            return self._read_particle_types_parts()
        traj = readdy.Trajectory(self.data_file)
        p_type_map = traj.particle_types
        particle_list = traj.read()
        min_id, max_id = DataReader._get_min_max_id(particle_list)
        shape = (len(particle_list), max_id + 1)
        particle_types = np.empty(shape, dtype=int)
        for t in range(shape[0]):
            part_t = particle_list[t]
            for p in part_t:
                particle_types[t, p.id] = p_type_map[p.type]
        return p_type_map, particle_types[:, min_id:]

    def read_time_as_step_indices(self) -> np.ndarray:
        """
        Reads time from trajectory recording.
        """
        if self.parts:
            return self._read_time_as_step_indices_parts()
        traj = readdy.Trajectory(self.data_file)
        pos_list = traj.read()
        nsteps = len(pos_list)
        time = np.empty(nsteps, dtype=int)
        for t in range(nsteps):
            pos_t = pos_list[t]
            time[t] = pos_t[0].t
        return time

    def read_time(self) -> np.ndarray:
        """
        Get array of time in internal units for each recorded frame.
        """
        dt = self.read_dt()
        time_in_steps = self.read_time_as_step_indices()
        return time_in_steps*dt

    def read_box_size(self) -> np.ndarray:
        """
        Read simulation box size.
        """
        if not self.parts:
            b = readdy.Trajectory(self.data_file).box_size
        else:
            b = None
            for i in range(self.n_parts):
                traj = readdy.Trajectory(self.data_file.format(i))
                if b is None:
                    b = traj.box_size
                else:
                    assert (b == traj.box_size).all()
        box_size = np.empty((2, 3))
        box_size[0] = -b/2
        box_size[1] = b/2
        return box_size

    def _read_particle_types_parts(self) -> Tuple[Dict[str, int], np.ndarray]:
        ptype_arrays = []
        nmax_global = 0
        nsteps = 0
        ptype_map = None
        for i in range(self.n_parts):
            traj = readdy.Trajectory(self.data_file.format(i))
            if ptype_map is None:
                ptype_map = traj.particle_types
            else:
                msg = "Every part of the simulation needs to have all "
                msg += "particles defined, even if they are not present anymore. "
                msg += "Maps for particle types differ in your trajectory files."
                assert ptype_map == traj.particle_types, msg
            particle_list = traj.read()
            nmax = 0
            for plist in particle_list:
                nmax = max(nmax, len(plist))
            nmax_global = max(nmax, nmax_global)
            shape = (len(particle_list), nmax)
            nsteps += len(particle_list)
            ptypes = np.full(shape, -1, dtype=int)
            for t in range(shape[0]):
                part_t = particle_list[t]
                for i, p in enumerate(part_t):
                    ptypes[t, i] = ptype_map[p.type]
            ptype_arrays.append(ptypes)
        ptypes_combined = np.full((nsteps, nmax_global), -1, dtype=int)

        start = 0
        for pt in ptype_arrays:
            s = pt.shape
            ptypes_combined[start: s[0]+start, :s[1]] = pt
        return ptype_map, ptypes_combined
            
    def _read_time_as_step_indices_parts(self) -> np.ndarray:
        n_frames_part = self._read_n_frames_per_part()
        time_all = np.full((n_frames_part-1)*self.n_parts+1, -1)
        n_steps = self.read_parameter('n_steps')
        offset = 0
        for i in range(self.n_parts):
            traj = readdy.Trajectory(self.data_file.format(i))
            pos_list = traj.read()
            nframes = len(pos_list)
            time = np.empty(nframes, dtype=int)
            for t in range(nframes):
                pos_t = pos_list[t]
                time[t] = pos_t[0].t
            if n_steps != time[t]:
                msg = "DataReader for reading simulation data split in multiple parts "
                msg += "only works if chunks have equal number of frames, and if the last "
                msg += "frame of the previous chunk is identical with the first frame of the "
                msg += "current chunk. The last frame of the current chunk (part {}) ".format(i)
                msg += "is of step {}, but the part was simulated for {} steps! ".format(time[t],
                                                                                         n_steps)
                msg += "This can lead to non-overlapping chunks/parts!"
                raise RuntimeError(msg)
            time += offset

            if i == 0:
                time_all[:n_frames_part] = time
            else:
                time_all[(n_frames_part-1)*i+1 : (n_frames_part-1)*(i+1)+1] = time[1:]
            offset += n_steps
        return time_all
    
    def read_parameter(self, *args) -> Any:
        if self.parts:
            return self._read_parameter_parts(*args)
        if self._parameter_toml is not None:
            return self._read_parameter_toml(args)
        else:
            return self._read_parameter_json(args)

    def _read_parameter_json(self, args) -> Any:
        return self._read_parameter(self._parameter_json, json.load, args)

    def _read_parameter_toml(self, args) -> Any:
        try:
            value = self._read_parameter(self._parameter_toml, toml.load, args)
        except KeyError:
            try:
                value = self._read_parameter(self._parameter_toml, toml.load,
                                             ['parameters'] + list(args))
            except KeyError:
                value = self._read_parameter(self._parameter_toml, toml.load,
                                             ['run-parameters'] + list(args))
        return value


    @staticmethod
    def _read_parameter(parameter_file: str, load_function, args) -> Any:
        if not os.path.exists(parameter_file):
            param_path = '/'.join(args)
            msg = "parameter file '{}' does not exist, can't read parameter '{}'".format(
                parameter_file,
                param_path
            )
            raise RuntimeError(msg)
        with open(parameter_file, 'rt') as fh:
            params = load_function(fh)
        result = params
        for key in args:
            result = result[key]
        return result

    def _read_parameter_parts(self, *args) -> Any:
        value = None
        for i in range(self.n_parts):
            param_file = self._parameter_json.format(i)
            if not os.path.exists(param_file):
                param_path = '/'.join(args)
                msg = "parameter file '{}' does not exist, can't read parameter '{}'".format(
                    param_file,
                    param_path
                )
                raise RuntimeError(msg)
            with open(param_file, 'rt') as fh:
                params = json.load(fh)
            result = params
            for key in args:
                result = result[key]
            if value is None:
                value = result
            else:
                # make sure this parameter is identical in all parts
                assert value == result
        return value


def revert_minimum_image_projection(positions, box: np.ndarray) -> np.ndarray:
    """
    :param positions: 3-Dimensional numpy array with axes (time, particle number, position)
    :param box: Size of simulation box in (x, y, z) .
    """
    box_indices = np.zeros_like(positions, dtype=int)
    displacements = positions[1:] - positions[:-1]
    boundary_crossings = get_minimum_image_boundary_crossings(displacements, box)
    box_indices[1:] = np.cumsum(boundary_crossings, axis=0)
    reverted_positions = positions + box_indices * box

    return reverted_positions


def get_minimum_image_boundary_crossings(displacements: np.ndarray, box: np.ndarray) -> np.ndarray:
    box_index_changes = np.zeros_like(displacements, dtype=np.int8)
    box_index_changes[displacements > 0.5 * box] = -1
    box_index_changes[displacements < -0.5 * box] = 1
    return box_index_changes
