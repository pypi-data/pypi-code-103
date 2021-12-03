import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import Union, Dict, Any, Optional, List, Tuple

import numpy as np
import toml

from bead_state_model.base_setup_handler import BaseSetupHandler
from bead_state_model.components import Filament
from bead_state_model.data_reader import DataReader
from bead_state_model.system_setup import system_setup, simulation_setup, add_filaments_from_file, add_filaments

_ParticleName = str
_DiffusionConst = float
_ParticleCoordinates = np.ndarray
_Box = Union[np.ndarray, List[float], Tuple[float, float, float]]


@dataclass
class SimulationParameters:
    """
    A container for simulation parameters. Parameters include general
    system parameters like the ``box_size`` of the simulation box,
    but most parameters are specific for polymers and their reactions.

    By default, all reactions are disabled. To enable them, specify a positive
    parameter. E.g., to enable motor binding, set ``rate_motor_bind=0.5``.

    Attributes:
        box_size: Size of simulation box.
        k_bend: Force constant of angular springs, determines the bending
                stiffness of polymers.
        k_stretch: Force constant of linear springs, influences the segment
                   length (distance between consecutive beads of bead chains).
        n_beads_max: Maximum number of beads. External particles are included in this count.
                     When this number is exceeded (e.g. if you have polymerization enabled
                     with a positive ``rate_attach`` and polymers grew too large), the
                     simulation aborts with an error. You can safely choose a large value
                     here usually. However, when you have systems with volatile particle
                     numbers, where it's hard to predict the number of particles in your
                     simulation, the limit specified here might save you from saving gigantic
                     amounts of data to your hard drives.
        diffusion_const: Diffusion constant of beads in the polymer bead chains.
        min_network_distance: This is the minimum number of edges in the graph of bonds of polymers
                              connected by cross-links/motors, that is required for two beads
                              to be valid candidates for cross-link/motor binding.
                              See documentation (:ref:`Reactions`) for details.
        rate_motor_step: Rate (per motor pair) for motor steps to occur. Motors can only perform
                         steps in the direction of the head bead of a bead chain.
        rate_motor_bind: Rate for motor binding. This rate only comes to bear, if the spatial distance
                         requirement (``reaction_radius_motor_binding``) and the graph distance
                         requirement (``min_network_distance``) is fulfilled between two core beads
                         of two bead chains.
        rate_motor_unbind: Rate (per motor pair) for unbinding of a motor pair.
        reaction_radius_motor_binding: The distance between two core beads must not be larger than the
                                       here specified value to allow for motor formation.
                                       It should be a value of around 1, since beads of the bead chains
                                       have a diameter of 1. Default is 1.05.
        rate_attach: Rate at which new beads are added to bead chains. Beads are added at the side of the head bead.
        rate_detach: Rate at which beads are removed from the bead chains. Beads are removed at the side of the
                     tail bead.
        k_repulsion: Force constant for repulsion between beads of bead chains. This repulsion prohibits
                     polymers from moving through each other and allows for entanglement in networks.
        n_max_motors: The maximum number of motors can be limited with this parameter. If a positive integer
                      limit is specified here, the effective ``rate_motor_bind`` is reduced linearly down
                      to a value of 0 when ``n_max_motors`` are present in the simulation.
    """

    box_size: _Box
    k_bend: float
    k_stretch: float
    n_beads_max: int
    diffusion_const: float = 1.0
    min_network_distance: int = 6
    rate_motor_step: float = 0.0
    rate_motor_bind: float = 0.0
    rate_motor_unbind: float = 0.0
    reaction_radius_motor_binding: float = 1.05
    rate_attach: float = 0.0
    rate_detach: float = 0.0
    k_repulsion: float = 80.0
    n_max_motors: Optional[int] = None

    @staticmethod
    def load_parameters_from_generated_network(
            config_file: str
    ) -> Tuple[_Box, float, float]:
        with open(config_file, 'rt') as fp:
            network_config = json.load(fp)
        k_bend = network_config['k_bend']
        k_stretch = network_config['k_stretch']
        box = np.array(network_config['box'])
        return box, k_stretch, k_bend

    @staticmethod
    def load_parameters_from_simulation_toml(
            config_file: str
    ) -> 'SimulationParameters':
        with open(config_file, 'rt') as fp:
            config = toml.load(fp)
        config['parameters']['box_size'] = [float(value) for value in config['parameters']['box_size']]
        return SimulationParameters(**config['parameters'])


class Simulation:

    def __init__(
            self,
            output_folder: str,
            parameters: Union[SimulationParameters, Dict[str, Any]],
            kernel: str = 'SingleCPU',
            non_filament_particles: Optional[Dict[_ParticleName, _DiffusionConst]] = None,
            interaction_setup_handler: Optional[BaseSetupHandler] = None
    ):
        """
        Use this class to configure and run simulations.

        :param output_folder: Output data is written to this folder.
        :param parameters: Specifies parameters for the simulation.
        :param kernel: Can be either 'SingleCPU' (no multithreading) or 'CPU' (multithreading enabled).
        :param non_filament_particles: A dictionary to specify external particles. This is useful to define
                                       passive particles, e.g. a passive microsphere for microrheology.
                                       For more elaborate setups (particles under influence of potentials/reactions)
                                       use ``interaction_setup_handler`` parameter.
        :param interaction_setup_handler: Provide an instance of an :class:`~bead_state_model.BaseSetupHandler`,
                                          to handle arbitrary setups of particles/potentials.
                                          See documentation of :class:`~bead_state_model.BaseSetupHandler`
                                          for more information.
        """
        self._filaments_were_added = False
        self.output_folder = output_folder
        self._run_parameters = None  # type: Union[None, Dict[str, Any]]
        os.makedirs(output_folder, exist_ok=True)
        if isinstance(parameters, dict):
            self._parameters = SimulationParameters(**parameters)
        else:
            self._parameters = SimulationParameters(**asdict(parameters))

        self._system, self._filament_handler = system_setup(**asdict(self._parameters))

        if non_filament_particles:
            for name, diffusion_const in non_filament_particles.items():
                self._system.add_species(name, diffusion_const)

        if interaction_setup_handler:
            interaction_setup_handler(self._system)
        self._interaction_setup_handler = interaction_setup_handler

        self.readdy_simulation = simulation_setup(self._system, self._filament_handler, kernel)
        self._configure_output_files()

    def _configure_output_files(self):
        self._filament_handler.output_file = os.path.join(self.output_folder, 'links.h5')
        self.readdy_simulation.output_file = os.path.join(self.output_folder, 'data.h5')
        if os.path.exists(self._filament_handler.output_file):
            os.remove(self._filament_handler.output_file)
        if os.path.exists(self.readdy_simulation.output_file):
            os.remove(self.readdy_simulation.output_file)

    def add_non_filament_particles(self, **particles: _ParticleCoordinates):
        """
        Add particles at explicit coordinates. This method has to be called **BEFORE**
        any filaments are added through method ``add_filaments`` or ``add_filament_via_arrays``.
        Map names of particles to arrays of shape (N, 3). This would create N particles at the specified locations.
        E.g. ``sim.add_non_filament_particles(microsphere=np.zeros((1, 3)))`` to create one particle of name
        ``'microsphere'`` at location ``[0, 0, 0]``.
        **Particles have to be defined before!** I.e., particle names have to match those you specified
        through either the ``non_filament_particles`` argument when you created the ``Simulation`` instance,
        or through the provided ``interaction_setup_handler``.
        """
        if self._filaments_were_added:
            raise RuntimeError("You need to add all non-filament particles before adding filament particles.")
        for name in particles:
            coords = particles[name]
            assert coords.ndim == 2, ("External particle coordinates has to be an array "
                                      "with two axes: (number of particles, xyz coordinates")
            for c in coords:
                self._filament_handler.add_non_filament_particle(name, c)

    def add_non_filament_topology(
            self,
            topology_name: str,
            particle_types: List[str],
            coordinates: np.ndarray,
            graph_edges: List[Tuple[int, int]]
    ):
        """
        Add topologies. This method has to be called **BEFORE**
        any filaments are added through method ``add_filaments`` or ``add_filament_via_arrays``.
        The arguments of this function are identical to that of that of
        ``readdy.ReactionDiffusionSystem.add_topology``, plus the additional ``graph_edges`` argument.
        ``graph_edges`` has to be a list of index tuples, that are passed to ``graph.add_edge`` method
        readdy provides for topology graphs.
        """
        top = self.readdy_simulation.add_topology(topology_name, particle_types, coordinates)
        graph = top.get_graph()
        for e in graph_edges:
            graph.add_edge(*e)

        self._filament_handler.add_non_filament_particle_number(len(coordinates))


    def add_filaments(self, filament_init_file: Union[str, None]):
        """
        Add filaments from file.

        :param filament_init_file: Either a ``.txt`` file that was generated through tools in
                                   :mod:`bead_state_model.network_assembly`, or a ``.h5`` file
                                   that is the output of a previous simulation (usually named
                                   ``data.h5``).
        """
        self._filaments_were_added = True
        if filament_init_file is None:
            raise NotImplementedError("Currently you have to provide a file with initial filaments."
                                      " If you want to start with empty simulation boxes, use the "
                                      "lower level functions system_setup and simulation_setup, or"
                                      "make a feature request on gitlab.")

        ext = os.path.splitext(filament_init_file)[1]
        if ext == '.txt':
            beads, filaments, links = add_filaments_from_file(self.readdy_simulation, filament_init_file,
                                                              offset=-np.array(self._parameters.box_size)/2)
        elif ext == '.h5':
            dr = DataReader(filament_init_file)
            positions_final_frame = dr.read_particle_positions(minimum_image=True)[-1]
            n_frames = dr.read_n_frames()
            filaments_init, links_init = dr.get_filaments(n_frames-1)
            map_filament_indices, map_bead_indices, filaments, links = add_filaments(
                self.readdy_simulation,
                positions_final_frame[dr.get_n_non_filament_particles():],
                filaments_init, links_init
            )

            np.save(os.path.join(self.output_folder, 'map_filaments_to_init_state.npy'), map_filament_indices)
            np.save(os.path.join(self.output_folder, 'map_beads_to_init_state.npy'), map_bead_indices)
        else:
            raise RuntimeError("File has to end on .txt or .h5.")

        self._filament_handler.initialize(filaments, links)

    def add_filaments_via_arrays(self, filament_positions: np.ndarray, links_init: np.ndarray):
        if len(filament_positions) != len(links_init):
            raise ValueError("Provided initial filament positions and links between filament particles have "
                             "to be of same length.")
        self._filaments_were_added = True
        filaments_init = _generate_filaments_from_link_array(links_init)
        map_filament_indices, map_bead_indices, filaments, links = add_filaments(
            self.readdy_simulation,
            filament_positions,
            filaments_init, links_init
        )

        np.save(os.path.join(self.output_folder, 'map_filaments_to_init_state.npy'), map_filament_indices)
        np.save(os.path.join(self.output_folder, 'map_beads_to_init_state.npy'), map_bead_indices)
        self._filament_handler.initialize(filaments, links)

    def run(self, n_steps: int, dt: float, observation_interval: int, mute=False):
        if not self._filaments_were_added:
            raise RuntimeError("Add filaments via method add_filaments before running the simulation.")
        self._run_parameters = {
            'n_steps': n_steps,
            'dt': dt,
            'observation_interval': observation_interval
        }
        self.readdy_simulation.record_trajectory(observation_interval)
        self.readdy_simulation.observe.particles(observation_interval,
                                                 callback=self._filament_handler.write,
                                                 save=False)
        self._save_configuration()
        if mute:
            _normal_stdout = sys.stdout
            _normal_stderr = sys.stderr
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            self.readdy_simulation.run(n_steps, dt)
            sys.stdout = _normal_stdout
            sys.stderr = _normal_stderr
        else:
            self.readdy_simulation.run(n_steps, dt)

        self._save_final_state()

    def _save_final_state(self):
        positions_final = np.full((len(self.readdy_simulation.current_particles), 3), np.nan)
        for i, p in enumerate(self.readdy_simulation.current_particles):
            positions_final[i] = p.pos

        np.save(os.path.join(self.output_folder, 'positions_final_frame.npy'), positions_final)

    def _save_configuration(self):
        p = asdict(self._parameters)
        p['box_size'] = [float(v) for v in self._parameters.box_size]
        config = {
            'parameters': p,
            'run-parameters': self._run_parameters,
            'filament-handler': {
                'index_offset': self._filament_handler.get_index_offset()
            }
        }
        if self._interaction_setup_handler is not None:
            config['interaction_setup_parameters'] = self._interaction_setup_handler.to_config_dict()
        with open(os.path.join(self.output_folder, 'config.toml'), 'wt') as fp:
            toml.dump(config, fp)


def _generate_filaments_from_link_array(links: np.ndarray) -> List[Filament]:
    filaments = []
    for i, row in enumerate(links):
        if not _is_tail(*row):
            continue
        id_ = len(filaments)
        filaments.append(Filament(id_, i, links))
    return filaments


def _is_tail(previous, nxt, cross_filament) -> bool:
    if previous != -1:
        return False
    if nxt == -1:
        return False
    if cross_filament != -1:
        return False
    return True
