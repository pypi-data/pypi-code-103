import os
from typing import Callable, Dict, Any, Iterable, List, Tuple, Union, Sequence
import math
import json
import logging

from scipy import stats
import numpy as np
import numba
import h5py
from actomyosin_analyser.file_io.data_reader import DataReader
from . import geometry
from .abstract_analyser import AbstractAnalyser
from .filament_center_of_mass import FilamentCenterOfMassGetter
from .polymer_density import GridGenerator, PolymerDensityGetter
from .mean_squared_displacement import compute_msd, MeanSquaredDisplacement
from .._version import get_version
from ..file_io.state_exporter import StateExporter
from ..model.bead import Filament


_VERSION = get_version()
logger = logging.getLogger(__name__)

Dataset = h5py.Dataset
_FilamentT = Tuple[np.ndarray, np.ndarray]
_FilamentsT = numba.typed.List  # [_FilamentT]


class Analyser(AbstractAnalyser):
    """
    The ``Analyser`` class defines the user interface to the analysis tools
    of the ``actomyosin_analyser`` package. Use the methods of an
    ``Analyser`` instance to run the analysis on your data.
    Reading of the raw data is delegated to the ``DataReader`` provided when
    creating the instance of the ``Analyser``.
    More on the :class:`~actomyosin_analyser.file_io.data_reader.DataReader` class
    can be found in its documentation.
    """

    def __init__(self, data_reader: DataReader, analysis_file: str):
        """
        Create an instance of the ``Analyser`` class. Provide an instance
        of a ``DataReader`` that handles reading the raw data (``DataReader``
        has to be implemented depending on the format of your data), and
        the path to an analysis file (hdf5 format, usual file extension is `.h5`).

        :param data_reader: Instance of a :class:`~actomyosin_analyser.file_io.data_reader.DataReader`
        :param analysis_file: Path to the analysis file
           (usually `"some/folder/analysis.h5"` in the examples).
        """
        _data_root = os.path.split(analysis_file)[0]
        if len(_data_root) == 0:
            _data_root = '.'
        super().__init__(_data_root)
        self.data_reader = data_reader
        self.analysis_file = analysis_file
        self._offset_filaments = None
        self._particle_positions = None
        self._analysis_parameter_file = os.path.join(self.blob_root, 'parameters.json')

    def _get_analysis_dataset(self,
                              dset_name: str,
                              compute_function: Callable[[Any], np.ndarray],
                              **keyword_arguments: Any) -> np.ndarray:
        kwargs_as_json = None
        if keyword_arguments:
            kwargs_as_json = Analyser._keyword_arguments_to_json_string(keyword_arguments)
            dset_name += '_' + kwargs_as_json
        if os.path.exists(self.analysis_file):
            with h5py.File(self.analysis_file, 'r') as fp:
                if dset_name in fp:
                    dataset = fp[dset_name]
                    if keyword_arguments:
                        kwargs = json.loads(dataset.attrs['parameters'])
                        if kwargs != keyword_arguments:
                            msg = "DataSet '{}' has matching name, but loaded parameters are different!"
                            msg = msg.format(dataset.name)
                            raise RuntimeError(msg)
                    return np.array(dataset)
        data = compute_function(**keyword_arguments)
        with h5py.File(self.analysis_file, 'a') as fp:
            fp[dset_name] = data
            fp[dset_name].attrs['ACTOMYOSIN_ANALYSER_VERSION'] = _VERSION
            if kwargs_as_json is not None:
                fp[dset_name].attrs['parameters'] = kwargs_as_json
        return data

    def _get_nested_analysis_dataset(self, group_name: str,
                                     compute_function: Callable[[Any], np.ndarray],
                                     **keyword_arguments: Any) -> np.ndarray:
        if not keyword_arguments:
            msg = "keyword_arguments can not be empty for Analyser._get_nested_analysis_dataset. "
            msg += "If you have no keywords, use Analyser._get_analysis_dataset instead!"
            raise KeyError(msg)
        kwargs_as_json = Analyser._keyword_arguments_to_json_string(keyword_arguments)
        h = kwargs_as_json

        with h5py.File(self.analysis_file, 'a') as fp:
            if group_name in fp:
                group = fp[group_name]
            else:
                group = fp.create_group(group_name)

            if h in group:
                dset = group[h]
                kwargs = json.loads(dset.attrs['parameters'])
                for_comparison = keyword_arguments.copy()
                for k in for_comparison.keys():
                    value = for_comparison[k]
                    if isinstance(value, tuple):
                        for_comparison[k] = 'hashed_tuple_' + str(hash(value))
                if kwargs != for_comparison:
                    msg = "DataSet '{}' has matching name, but loaded parameters are different!".format(
                        dset.name)
                    raise RuntimeError(msg)
                return np.array(dset)

            data = compute_function(**keyword_arguments)
            group[h] = data
            group[h].attrs['parameters'] = kwargs_as_json
            group[h].attrs['ACTOMYOSIN_ANALYSER_VERSION'] = _VERSION
        return data

    def _get_parameter(self, parameter_name,
                       compute_function: Callable[[], Any]) -> Any:
        if os.path.exists(self._analysis_parameter_file):
            with open(self._analysis_parameter_file, 'rt') as fh:
                parameters = json.load(fh)
        else:
            parameters = {}
        if parameter_name in parameters:
            return parameters[parameter_name]
        par = compute_function()
        parameters[parameter_name] = par
        with open(self._analysis_parameter_file, 'wt') as fp:
            json.dump(parameters, fp)
        return par

    def get_offset_filaments(self) -> int:
        return self._get_parameter('offset_filaments',
                                   self._determine_offset_filaments)

    def _determine_offset_filaments(self) -> int:
        if self._offset_filaments is not None:
            return self._offset_filaments
        self._offset_filaments = self.data_reader.get_n_non_filament_particles()
        return self._offset_filaments

    def get_filaments(self, save: bool = False) -> List[List[Filament]]:
        return self._get_filaments_from_analysis_file_or_data_reader(save)

    def get_trajectories_filaments(self, minimum_image: bool) -> np.ndarray:
        """
        Load complete trajectory of all filaments.
        Filaments are represented by multiple coordinates,
        which corresponds to coordinates of beads in bead chains (e.g. from simulations
        with the ``bead_state_model`` framework)
        , or start and end points
        of segments in segment representations of filaments (e.g. from simulations with
        the ``cytosim`` framework).
        Which coordinates belong to which filament can be figured out with the return
        value of the ``get_filaments`` method.

        This can be very
        memory intensive for ``bead_state_model`` data, when executed for the first time,
        depending of the number of particles and recorded frames.
        When this method is executed,  it will save the trajectory to the analysis file,
        which has the benefit of much quicker and way less memory intensive execution
        on the next call. However, this additional data saved to the analysis file
        might double the storage space needed, since it will inflate the analysis file
        to a similar size of the raw data file.
        If you only want use a small subset of frames, and you want to save storage space,
        use the method get_positions_of_filaments_at_frames.

        :param minimum_image: Set ``True`` to project coordinates that exceed
           the simulation box back into the simulation box.
        :return: Numpy array with 3 dimensions:
           (number of frames, number of filament particles, xyz-coordinates).
        """
        return self._get_analysis_dataset('trajectories_filaments',
                                          self._get_trajectories_filament,
                                          minimum_image=minimum_image)

    def get_trajectories_non_filament(self, minimum_image: bool) -> np.ndarray:
        """
        Get trajectories on non-filament particles. These are all particles
        that are not part of filaments. For example passive beads of
        a microrheology experiment/simulation. The result does not contain
        information of the particle species.

        :param minimum_image: Set ``True`` to project coordinates that exceed
           the simulation box back into the simulation box.
        :return: Numpy array with 3 dimensions:
           (number of frames, number of particles, xyz-coordinates).
        """
        return self._get_analysis_dataset('trajectories_non_filament',
                                          self._get_trajectories_non_filament,
                                          minimum_image=minimum_image)

    def get_positions_of_filaments_at_frames(
            self,
            frames: Sequence[int],
            minimum_image: bool = False
    ) -> np.ndarray:
        """
        Same as method ``get_trajectories_filaments``, but for a subset of frames,
        rather than for all frames.
        See documentation of method
        :py:meth:`~actomyosin_analyser.analysis.analyser.Analyser.get_trajectories_filaments`.

        :param frames: Selected subset of frames.
        :param minimum_image: Set ``True`` to project coordinates that exceed
           the simulation box back into the simulation box.
        :return: Numpy array with 3 dimensions:
           (number of selected frames, number of filament particles, xyz-coordinates).
        """
        positions = self._load_positions_of_filaments_at_frames(frames, minimum_image)
        if positions is not None:
            return positions
        positions = self.data_reader.get_filament_coordinates(minimum_image)[frames]
        self._save_particle_positions_at_frames(frames, positions, minimum_image)
        return positions

    def export_state(self, frame: int):
        """
        Export the state of the system at a single frame. The state includes
        information of all filament coordinates, links between filament beads, and
        positions of all external particles.
        State data is written to folder `analysis_blobs/state` placed next to the
        analysis_file (specified during creation of the ``Analyser`` instance).

        :param frame: Selected frame.
        """
        state_exporter = StateExporter(self)
        state_exporter.export(frame)

    def _load_positions_of_filaments_at_frames(
            self,
            frames,
            minimum_image
    ) -> Union[None, np.ndarray]:
        if self._contains_data_set('trajectories_filaments', minimum_image=minimum_image):
            return self.get_trajectories_filaments(minimum_image)[frames]
        positions = []
        for f in frames:
            p = self._load_positions_of_filaments_at_single_frame(f, minimum_image)
            if p is None:
                return None
            positions.append(p[np.newaxis])
        return np.concatenate(positions)

    def _contains_data_set(self, group_label: str, **kwargs) -> bool:
        if not os.path.exists(self.analysis_file):
            return False
        with h5py.File(self.analysis_file, 'r') as h5f:
            if kwargs:
                kwargs_as_json = Analyser._keyword_arguments_to_json_string(kwargs)
                group_label += kwargs_as_json
            return group_label in h5f

    def _save_particle_positions_at_frames(
            self,
            frames: Sequence[int],
            positions: np.ndarray,
            minimum_image: bool
    ):
        for i, f in enumerate(frames):
            p = positions[i]
            self._save_particle_positions_at_single_frame(f, p, minimum_image)

    def _save_particle_positions_at_single_frame(
            self,
            frame: int,
            positions: np.ndarray,
            minimum_image: bool
    ):
        label = "filament_positions_at_frame"
        if minimum_image:
            label = 'minimum_image_' + label
        with h5py.File(self.analysis_file, 'a') as h5f:
            if label in h5f:
                group = h5f[label]
            else:
                group = h5f.create_group(label)
            group[str(frame)] = positions

    def _load_positions_of_filaments_at_single_frame(
            self,
            frame: int,
            minimum_image: bool
    ) -> Union[np.ndarray, None]:
        if not os.path.exists(self.analysis_file):
            return None
        label = "filament_positions_at_frame"
        if minimum_image:
            label = 'minimum_image_' + label
        with h5py.File(self.analysis_file, 'r') as h5f:
            if label not in h5f:
                return None
            group = h5f[label]
            if str(frame) not in group:
                return None
            return group[str(frame)][:]

    def get_filament_center_of_mass_msds(self, skip: int) -> MeanSquaredDisplacement:
        """
        Get mean-squared displacements (MSDs) of the centers of mass of all filaments.
        Resulting ensemble MSD is average over individual filament center of mass MSDs.

        :param skip: Initial frames to be skipped, in case the state is not in the desired
           state from the start. Set to 0 if no frames are to be skipped.
        :return: ``MeanSquaredDisplacement`` instance; a dataclass with 4 attributes:
           ``lag`` (in frames), ``lag_time``, ``msd``, ``variance_of_msd``.
        """
        dataset_name = 'filament_center_of_mass_msds'
        keyword_args = {'skip': skip}
        msd_array = self._get_nested_blob_analysis_dataset(
            dataset_name,
            self._compute_filament_center_of_mass_msds,
            keyword_args
        )
        msd = MeanSquaredDisplacement.from_array(msd_array)
        time = self.get_time()
        msd.lag_time = time[msd.lag.astype(int)]
        return msd

    def _compute_filament_center_of_mass_msds(self, skip: int) -> np.ndarray:
        fcom_getter = FilamentCenterOfMassGetter(self)
        fcom_trajectories = fcom_getter.get()
        fcom_traj_array = fcom_trajectories.as_array()[skip:]
        box = self.read_simulation_box()
        msd = compute_msd(fcom_traj_array, box)
        return msd.as_array()

    def get_msd_ensemble(self, particle_indices: List[int], skip=0) -> np.ndarray:
        return self._get_nested_analysis_dataset('msd_ensemble', self._compute_msd_ensemble,
                                                 particle_indices=tuple(particle_indices),
                                                 skip=skip)

    def get_msd(self, particle_indices: List[int], non_filament: bool = False, skip=0) -> List[MeanSquaredDisplacement]:
        if non_filament:
            method = self.get_msd_single_particle_non_filament
        else:
            method = self.get_msd_single_particle
        msds = []
        for i in range(len(particle_indices)):
            msds.append(method(particle_indices[i], skip))
        return msds

    def get_msd_single_particle(self, particle_index: int, skip: int) -> MeanSquaredDisplacement:
        msd_array = self._get_nested_analysis_dataset('msd_filament', self._compute_msd,
                                                      particle_index=particle_index,
                                                      skip=skip)
        return MeanSquaredDisplacement.from_array(msd_array)

    def get_msd_single_particle_non_filament(self, particle_index: int, skip: int) -> MeanSquaredDisplacement:
        msd_array = self._get_nested_analysis_dataset('msd_non_filament', self._compute_msd_non_filament,
                                                      particle_index=particle_index,
                                                      skip=skip)
        return MeanSquaredDisplacement.from_array(msd_array)

    def get_polymer_density(
            self,
            grid: GridGenerator,
            frames: Sequence[int],
            bandwidth: Union[float, None] = None
    ) -> Tuple[float, np.ndarray]:
        """
        Get the polymer density in the simulation box. Density is estimated
        at points on a grid. Estimation is done via scipy's gaussian_kde function.
        If no bandwidth is specified, bandwidth is generated automatically during
        evaluation of the density at the first frame. Bandwidth has to
        be identical across frames, in order for the densities to be comparable
        across frames.

        :param grid: Instance of :class:`~actomyosin_analyser.analysis.polymer_density.GridGenerator`
           specifying the grid at which the density gets evaluated.
        :param frames: Selected frames.
        :param bandwidth: Bandwidth used for Gaussian kernel density estimation (see scipy documentation).
        :return: Tuple containing (1) the used bandwidth and
           (2) the density evaluated at grid points.
        """
        density_getter = PolymerDensityGetter(grid, self)
        bandwidth, density = density_getter.get(frames, bandwidth)
        return bandwidth, density

    def get_densities_gaussian_kde_scipy(
            self, frame: int,
            bandwidth: Union[float, None] = None
    ) -> stats.kde.gaussian_kde:
        positions = self.get_positions_of_filaments_at_frames([frame], minimum_image=True)[0]
        if bandwidth is None:
            kde = stats.gaussian_kde(positions.T)
        else:
            kde = stats.gaussian_kde(positions.T, bw_method=bandwidth)
        return kde

    def get_links(self, frame: int) -> np.ndarray:
        return self.data_reader.get_filaments(frame)[1]

    def get_link_count(self) -> np.ndarray:
        return self._get_blob_analysis_dataset('link_count', self.data_reader.get_motor_count)

    def get_time(self) -> np.ndarray:
        return self._get_blob_analysis_dataset('time', self.data_reader.read_time)

    def get_contour_lengths(self) -> np.ndarray:
        return self._get_analysis_dataset('contour_lengths',
                                          self._compute_contour_lengths)

    def get_end_to_end_distances(self, t_frame: int, n_beads: int) -> np.ndarray:
        """
        Get end-to-end distances of filaments with n_beads at frame t_frame.
        """
        return self._get_nested_blob_analysis_dataset('end_to_end_distances',
                                                      self._compute_end_to_end_distances,
                                                      {'t': t_frame, 'n_beads': n_beads})

    def get_end_to_end_vectors(self) -> np.ndarray:
        """
        Get end-to-end vectors for all filaments at all frames. 
        
        :return: Array with 3 dimensions: (1) time frame (2) filament ID (3) XYZ coordinates.
        """
        return self._get_analysis_dataset('end_to_end_vectors', self._get_end_to_end_vectors)

    def get_time_in_steps(self) -> np.ndarray:
        return self._get_analysis_dataset('time_in_steps', self._get_time_in_steps)

    def get_energies_stretch_and_bend(self) -> np.ndarray:
        """
        For data of a ``bead_state_model`` simulation, get bending and stretching energy of filaments.
        For other sources of data, you need to implement your own method to compute energies.

        :return: Numpy array with 2 dimensions:
           (number of frames, energy (2 separate columns for stretch and bend))
        """
        energies = self._get_analysis_dataset('energies', self._compute_energies_stretch_and_bend)
        return energies

    def _get_time_in_steps(self):
        return self.data_reader.read_time_as_step_indices()

    def _get_trajectories_non_filament(self, minimum_image: bool) -> np.ndarray:
        pos = self.data_reader.get_non_filament_coordinates(minimum_image)
        return pos

    def _get_trajectories_filament(self, minimum_image: bool):
        pos = self.data_reader.read_particle_positions(minimum_image)
        offset = self.get_offset_filaments()
        return pos[:, offset:]

    def _convert_binning_parameters_to_lists(self, n_bins, ranges):
        if ranges is None:
            ranges = self.data_reader.read_box_size()
        if isinstance(ranges, np.ndarray):
            range_x = ranges[0].tolist()
            range_y = ranges[1].tolist()
            range_z = ranges[2].tolist()
        else:
            range_x = list(ranges[0])
            range_y = list(ranges[1])
            range_z = list(ranges[2])
        if isinstance(n_bins, np.ndarray):
            n_bins = n_bins.tolist()
        n_bins = list(n_bins)
        return n_bins, range_x, range_y, range_z

    def _compute_msd(self, particle_index: int, skip: int) -> np.ndarray:
        coords = self.get_trajectories_filaments(minimum_image=False)[skip:, particle_index]
        return compute_msd(coords).as_array()

    def _compute_msd_non_filament(self, particle_index: int, skip: int) -> np.ndarray:
        traj = self.get_trajectories_non_filament(minimum_image=False)[skip:, particle_index]
        return compute_msd(traj).as_array()

    def _compute_msd_ensemble(self, particle_indices: Tuple[int], skip: int):
        coords = self.get_trajectories_filaments()[skip:, particle_indices]
        return compute_msd(coords).as_array()

    def _compute_densities(self,
                           particle_types: List[str],
                           range_x: List[float],
                           range_y: List[float],
                           range_z: List[float],
                           n_bins: List[int],
                           count: bool) -> np.ndarray:
        wx = (range_x[1] - range_x[0]) / n_bins[0]
        wy = (range_y[1] - range_y[0]) / n_bins[1]
        wz = (range_z[1] - range_z[0]) / n_bins[2]
        V = wx * wy * wz

        positions = self.data_reader.read_particle_positions(minimum_image=True)
        pmap, ptypes = self.data_reader.read_particle_types()

        shape = (len(positions), n_bins[0], n_bins[1], n_bins[2])
        densities = np.full(shape, np.nan)

        for t in range(positions.shape[0]):
            pos_t = positions[t]
            ptypes_t = ptypes[t]
            mask = np.zeros_like(ptypes_t, dtype=bool)
            for pt in particle_types:
                mask += (ptypes_t == pmap[pt])
            selected_particles = pos_t[mask]
            bin_indices = Analyser._coordinates_to_bin_indices(selected_particles,
                                                               range_x, wx,
                                                               range_y, wy,
                                                               range_z, wz)
            for i in range(shape[1]):
                for j in range(shape[2]):
                    for k in range(shape[3]):
                        count_ijk = ((bin_indices[:, 0] == i) &
                                     (bin_indices[:, 1] == j) &
                                     (bin_indices[:, 2] == k)).sum()
                        densities[t, i, j, k] = count_ijk
        if count:
            densities = densities.astype(int)
        else:
            densities = densities / V

        return densities

    def _compute_end_to_end_distances(self, t: int, n_beads: int) -> np.ndarray:
        coordinates = self.get_trajectories_filaments(minimum_image=True)[t]
        filaments, _ = self.data_reader.get_filaments(t)
        box = self.read_simulation_box()

        e2e = []
        for fil in filaments:
            if len(fil.items) != n_beads:
                continue
            e2e.append(self._compute_e2e_single_filament(coordinates, fil, box))
        return np.array(e2e)

    def _get_end_to_end_vectors(self) -> np.ndarray:
        raise NotImplementedError
        coordinates = self.get_trajectories_filaments()
        filaments = self.data_reader.get_filaments_all()

    def _compute_e2e_single_filament(self, coordinates: np.ndarray, filament, box) -> float:
        offset_filaments = self.get_offset_filaments()
        fcoords = coordinates[np.array(filament.items) + offset_filaments]
        v_segments = geometry.get_minimum_image_vector(fcoords[:-1], fcoords[1:], box)
        e2e = np.sum(v_segments, axis=0)
        return math.sqrt(e2e[0] ** 2 + e2e[1] ** 2 + e2e[2] ** 2)

    def _compute_contour_lengths(self) -> np.ndarray:
        coordinates = self.get_trajectories_filaments()
        box = self.read_simulation_box()

        filaments = self.get_filaments()

        contour_lengths = np.full((len(coordinates), len(filaments[0])), np.nan)

        for t in range(len(coordinates)):
            fil_t = filaments[t]
            for f, fil in enumerate(fil_t):
                fcoords = coordinates[t, fil.items]
                v_segments = geometry.get_minimum_image_vector(fcoords[:-1], fcoords[1:], box)
                d = np.sqrt(np.sum(v_segments ** 2, 1))
                lc = np.sum(d)
                contour_lengths[t, f] = lc

        return contour_lengths

    def read_simulation_box(self):
        box = self.data_reader.read_box_size()
        box = np.array([box[1, 0] - box[0, 0],
                        box[1, 1] - box[0, 1],
                        box[1, 2] - box[0, 2]])
        return box

    def _compute_energies_stretch_and_bend(self) -> np.ndarray:
        coordinates = self.get_trajectories_filaments()
        box = self.read_simulation_box()

        filaments = self.get_filaments()
        filaments_as_tuples = Analyser._convert_nested_filaments_to_tuples(filaments)

        return Analyser._numba_compute_energies_stretch_and_bend(box, coordinates,
                                                                 filaments_as_tuples)

    @staticmethod
    def _convert_nested_filaments_to_tuples(filaments) -> numba.typed.List:
        filaments_as_tuples = numba.typed.List()
        for f_frame in filaments:
            filaments_as_tuples_single_frame = numba.typed.List()
            for f in f_frame:
                filaments_as_tuples_single_frame.append((
                    np.array(f.items).astype('uint32'),
                    np.array(f.motors).astype('uint32')))
            filaments_as_tuples.append(filaments_as_tuples_single_frame)
        return filaments_as_tuples

    @staticmethod
    @numba.njit
    def _numba_compute_energies_stretch_and_bend(
            box, coordinates,
            filaments: numba.typed.List  # List[_FilamentsT]
    ):
        energies = np.zeros((len(coordinates), 2))
        for t in range(len(coordinates)):
            fil_t = filaments[t]
            energies_t = np.zeros((len(fil_t), 2))
            for f, fil in enumerate(fil_t):
                coords_t = coordinates[t]
                fcoords = coords_t[fil[0]]
                v_segments = geometry.get_minimum_image_vector(
                    fcoords[:-1], fcoords[1:], box)
                segment_lengths = np.sqrt(np.sum(v_segments ** 2, 1))

                e_stretch = np.sum((segment_lengths - 1) ** 2)

                cos_theta = ((v_segments[1:] * v_segments[:-1]).sum(1)
                             / segment_lengths[1:] / segment_lengths[:-1])

                e_bend = np.sum(np.arccos(cos_theta) ** 2)

                energies_t[f, 0] = e_stretch
                energies_t[f, 1] = e_bend

            energies[t] = np.sum(energies_t, axis=0)
        return energies

    @staticmethod
    def _keyword_arguments_to_json_string(keyword_arguments: Dict[str, Any]) -> str:
        """
        Note that tuples get hashed. This is to avoid containers with thousands of values
        to become part of the json string, which will be used as key to retrieve
        data from file. Make sure you provide containers with countless items as tuples.
        """
        if not keyword_arguments:
            return ''
        sorted_dict = {}
        for key in sorted(keyword_arguments.keys()):
            value = keyword_arguments[key]
            if isinstance(value, tuple):
                value = 'hashed_tuple_' + str(hash(value))
            sorted_dict[key] = value
        return json.dumps(sorted_dict)

    @staticmethod
    def _get_voxel_mask(bin_indices, grid_range, indices, shape) -> np.ndarray:
        i, j, k = indices
        mask_i = ((np.abs((bin_indices[:, 0]) - i) <= grid_range[0]) |
                  ((-np.abs(bin_indices[:, 0] - i) % shape[0]) <= grid_range[0]))
        mask_j = ((np.abs((bin_indices[:, 1]) - j) <= grid_range[1]) |
                  ((-np.abs(bin_indices[:, 1] - j) % shape[1]) <= grid_range[1]))
        mask_k = ((np.abs((bin_indices[:, 2]) - k) <= grid_range[2]) |
                  ((-np.abs(bin_indices[:, 2] - k) % shape[2]) <= grid_range[2]))
        mask_ijk = (
                mask_i & mask_j & mask_k
        )
        return mask_ijk

    @staticmethod
    def _coordinates_to_bin_indices(coordinates: np.ndarray,
                                    range_x: List[float], width_x: float,
                                    range_y: List[float], width_y: float,
                                    range_z: List[float], width_z: float) -> np.ndarray:
        bin_indices = np.full((len(coordinates), 3), -1, dtype=int)
        for i, (range_i, width) in enumerate(zip([range_x, range_y, range_z],
                                                 [width_x, width_y, width_z])):
            mask = (coordinates[:, i] >= range_i[0]) & (coordinates[:, i] <= range_i[1])
            bin_indices[mask, i] = (coordinates[mask, i] - range_i[0]) // width
        return bin_indices

    def _get_filaments_from_analysis_file_or_data_reader(self, save: bool) -> List[List[Filament]]:
        if os.path.exists(self.analysis_file):
            with h5py.File(self.analysis_file, 'r') as fp:
                if 'filaments' in fp:
                    n_frames = len(self.get_time())
                    return Analyser._load_filaments_from_h5_group(fp['filaments'],
                                                                  n_frames)
        filaments = self.data_reader.get_filaments_all()
        if save:
            with h5py.File(self.analysis_file, 'a') as fp:
                group = fp.create_group('filaments')
                Analyser._write_filaments_to_h5_group(group, filaments)
        return filaments

    @staticmethod
    def _load_filaments_from_h5_group(group: h5py.Group, n_frames: int) -> List[List[Filament]]:
        filaments = []
        for f in range(n_frames):
            filaments_f = Analyser._load_filaments_from_h5_group_single_frame(group[str(f)])
            filaments.append(filaments_f)
        return filaments

    @staticmethod
    def _load_filaments_from_h5_group_single_frame(group: h5py.Group) -> List[Filament]:
        items = group['items'][:]
        motors = group['motors'][:]
        filament_tuples = Analyser._parse_items_and_motors_arrays_to_filament_tuples(items, motors)
        filaments = [Filament(list(ftuple[0]), list(ftuple[1])) for ftuple in filament_tuples]
        return filaments

    @staticmethod
    @numba.njit
    def _parse_items_and_motors_arrays_to_filament_tuples(
            items: np.ndarray, motors: np.ndarray
    ) -> _FilamentsT:
        tuples = numba.typed.List()
        assert len(items) == len(motors)
        _invalid = np.iinfo(items.dtype).max
        for i in range(len(items)):
            items_i = items[i]
            items_i = items_i[items_i != _invalid]
            motors_i = motors[i]
            motors_i = motors_i[motors_i != _invalid]
            tuples.append((items_i, motors_i))
        return tuples

    @staticmethod
    def _write_filaments_to_h5_group(group: h5py.Group, filaments: List[List[Filament]]):
        for frame in range(len(filaments)):
            filaments_t = filaments[frame]
            typed_list = numba.typed.List()
            [typed_list.append((np.array(f.items).astype('uint32'),
                                np.array(f.motors).astype('uint32'))) for f in filaments_t]
            group_t = group.create_group(str(frame))
            Analyser._write_filaments_to_h5_group_single_frame(group_t, typed_list)

    @staticmethod
    def _write_filaments_to_h5_group_single_frame(
            group: h5py.Group, filaments: _FilamentsT):
        max_idx, max_items, max_motors = Analyser._get_maximum_items_and_value_for_filaments(filaments)

        items, motors = Analyser._create_filament_item_and_motor_arrays(len(filaments),
                                                                        max_idx,
                                                                        max_items,
                                                                        max_motors)

        Analyser._fill_filament_item_and_motor_arrays(filaments, items, motors)

        group.create_dataset('items', data=items, compression='lzf')
        group.create_dataset('motors', data=motors, compression='lzf')

    @staticmethod
    @numba.njit
    def _fill_filament_item_and_motor_arrays(
            filaments: _FilamentsT,
            items: np.ndarray, motors: np.ndarray):
        for i, (items_i, motors_i) in enumerate(filaments):
            items[i, :len(items_i)] = items_i
            motors[i, :len(motors_i)] = motors_i

    @staticmethod
    @numba.njit
    def _get_maximum_items_and_value_for_filaments(
            filaments: _FilamentsT
    ) -> Tuple[int, int, int]:
        max_items = 0
        max_idx = 0
        max_motors = 0
        for items_i, motors_i in filaments:
            max_idx_f = max(items_i)
            if max_idx_f > max_idx:
                max_idx = max_idx_f
            if len(items_i) > max_items:
                max_items = len(items_i)
            if len(motors_i) > max_motors:
                max_motors = len(motors_i)
        return max_idx, max_items, max_motors

    @staticmethod
    def _create_filament_item_and_motor_arrays(
            n_filaments: int, max_idx: int,
            max_items: int, max_motors: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        dtype = 'uint32'
        _invalid = np.iinfo(dtype).max
        if max_idx > _invalid:
            raise ValueError("can't handle indices larger than "
                             f"{_invalid}, which is the maximum "
                             "for 32 bit unsigned integers")

        items = np.full((n_filaments, max_items), _invalid, dtype=dtype)
        motors = np.full((n_filaments, max_motors), _invalid, dtype=dtype)
        return items, motors
