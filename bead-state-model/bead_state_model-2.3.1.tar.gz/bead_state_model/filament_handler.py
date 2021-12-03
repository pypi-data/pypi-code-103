from typing import List, Tuple, Dict, Union
import numpy as np
import h5py
import readdy
from .components import Filament, LinksArray
from .network_assembly.create_filament import rotation_matrix
from .periodic_boundaries import get_minimum_image_vector

Topology = readdy._internal.readdybinding.api.top.Topology
Particle = readdy._internal.readdybinding.common.Particle
Vertex = readdy._internal.readdybinding.api.top.Vertex
RDSystem = readdy.ReactionDiffusionSystem


class FilamentHandler:
    """
    Keeps track of filaments and their beads. Needs to be carefully initialized
    before any simulation! The order of how you add particles to your simulation
    instance and to this filament handler is important. Basically you always have
    to add any non-filament particles ("external" particles like a microrheological
    bead, or any other shapes like indenters, walls, etc.) before you add filaments.
    These external particles must not be removed (or more added) during a simulation.
    Unfortunately the FilamentHandler is sensitive to those kinds of things. See
    the example in the documentation in :ref:`example bead in network`.

    Main purpose of this class
    is to allow for faster algorithms to handle reactions. E.g. to store
    information about the polarity of a filament (in which direction
    along the filament is "front", in which is "back"), and which
    filaments form one large topology (topology is the name that
    readdy uses for beads that are connected by bonds to form larger
    structures). This saves computation time, since it's not necessary
    to walk along the edges of all the topology graphs at each reaction.
    """

    # Need to keep track of all beads handled
    # by any FilamentHandler. ReaDDy does not start with id=0
    # when a new system or simulation is created within the
    # same process.
    _global_n_beads_total = 0

    enum_map = {"tail": 0, "core": 1, "head": 2,
                "motor": 3, "monomer": 15}

    def __init__(self, reserve_n_beads: int, box: np.ndarray,
                 k_bend: float, k_stretch: float):
        """
        :param reserve_n_beads: Maximum number of beads to allocate memory for. This has to be set
                                before a simulation and can't be changed. This is to keep possibly
                                wrongly initialized simulations from occupying too much memory,
                                to keep them from crashing the whole computer.
        :param box: Simulation box. Required for some reaction functions and minimum image projections.
        :param k_bend: Bending modulus used for angular force computations. Used here to estimate the
                       standard deviation to draw angles for newly attached beads.
        :param k_stretch: Spring constant for harmonic interaction potential between bound beads.
                          Used here to estimate the standard deviation to draw a distance
                          for newly attached beads.
        """
        self.links = np.full((reserve_n_beads, 3), -1, dtype=np.int32)
        self.filaments = []
        self.map_topology_id_to_filament_ids = {}
        self.map_tails_to_filament_ids = {}
        self.map_filament_id_to_topology_id = {}
        self.map_topology_id_to_motors = {}
        self.simulation = None
        self.box = box
        if k_stretch < 1e-15:
            self.sigma_length = 2
        else:
            self.sigma_length = np.sqrt(1 / k_stretch)
        if k_bend < 1e-15:
            self.sigma_angle = 2 * np.pi
        else:
            self.sigma_angle = np.sqrt(1 / k_bend)
        self.n_beads_total = 0
        self._index_offset = 0
        self._n_non_filament_particles = 0
        self.output_file = None
        self._n_write_called = 0
        self._update_required = False
        self._n_motors = 0

    def get_index_offset(self) -> int:
        return self._index_offset

    def initialize(self, filaments: List[Filament], links: LinksArray):
        """
        Initialize this instance with a list of filaments and the links between
        beads of those filaments. **Call this only after you added all non-filament**
        **particles with method FilamentHandler.add_non_filament_particle**!
        **Call this method only once per instance** I.e. only one call of this method
        before any run of a simulation.
        This class is sensitive to the order of these function calls.
        Non-filament particles have to be added first (and the number of them must not change)
        to compute a statical offset for mapping bead IDs to particle IDs in readdy.

        :param filaments: List of filament instances. This has to be all the initial filaments
                          in the system. Additional filaments can't be added any other way.
        :param links: Array (linked list) defining all bonds between filamentous beads.
                      See documentation for detailed description of this array.
        """
        self._index_offset = FilamentHandler._global_n_beads_total
        self.links[:len(links)] = links
        self.n_beads_total += len(links)
        FilamentHandler._global_n_beads_total += self.n_beads_total
        self.filaments = filaments
        for i, f in enumerate(self.filaments):
            self.map_topology_id_to_filament_ids[i] = [i]
            self.map_filament_id_to_topology_id[i] = i
            self.map_tails_to_filament_ids[f.get_tail()] = i
            self.map_topology_id_to_motors[i] = []
        self.update(({}, {'link': 1}, {}))

    def add_non_filament_particle(self, ptype: str, position: np.ndarray):
        """
        Add "external" particles, i.e. particles that are not beads of any filament, but
        rather particles like a larger bead for microrheological measurements, or
        a bead representing the tip of an indenter.
        **Register all particles with the simulation's FilamentHandler!**
        **Adding particles via readdy's normal methods will lead to a broken FilamentHandler!**
        **Make all your calls to this method before you call FilamentHandler.initialize!**

        :param ptype: Type of particle. For this particle type, interactions have to be
                      defined using readdy's methods like
                      system.potentials.add_box(...). Consult the documentation of readdy
                      for these methods.
        :param position: np.array defining [x, y, z] coordinates of particle.
        """
        if self.n_beads_total != 0:
            msg = "FilamentHandler already contains filaments. "
            msg += "You need to add all non-filament particles before initializing "
            msg += "setting information on filaments!\n"
            msg += "Make all calls to FilamentHandler.add_non_filament_particle "
            msg += "before calling FilamentHandler.initialize ."
            raise RuntimeError(msg)
        self.simulation.add_particle(ptype, position)
        FilamentHandler._global_n_beads_total += 1
        self._n_non_filament_particles += 1

    def add_non_filament_particle_number(self, n: int):
        if self.n_beads_total != 0:
            msg = "FilamentHandler already contains filaments. "
            msg += "You need to add all non-filament particles before initializing "
            msg += "setting information on filaments!\n"
            msg += "Make all calls to FilamentHandler.add_non_filament_particle "
            msg += "before calling FilamentHandler.initialize ."
            raise RuntimeError(msg)
        FilamentHandler._global_n_beads_total += n
        self._n_non_filament_particles += n

    def update(
            self,
            reaction_counts: Union[Tuple[Dict[str, int], Dict[str, int],
                                         Dict[str, int]], Dict[str, int]]
    ):
        """
        This is used by :func:`bead_state_model.system_setup.simulation_setup` as a callback function
        to keep track of all reactions changing bonds of filaments, to update the filament_handler
        accordingly.
        """
        if isinstance(reaction_counts, tuple) and len(reaction_counts) > 1 and 'link' in reaction_counts[1]:
            self._update_required = True
        if not self._update_required:
            return

        self._update_required = False

        new_map_tid_to_fids = {}
        new_map_fid_to_tid = {}
        new_map_tid_to_motors = {}
        for tid, top in enumerate(self.simulation.current_topologies):
            fids = []
            motors = []
            vertices = top.get_graph().get_vertices()
            for v in vertices:
                if top.particle_type_of_vertex(v) == 'tail':
                    fid = self.map_tails_to_filament_ids[top.particle_id_of_vertex(v) - self._index_offset]
                    fids.append(fid)
                    new_map_fid_to_tid[fid] = tid
                if top.particle_type_of_vertex(v) == 'motor':
                    id_m1 = top.particle_id_of_vertex(v) - self._index_offset
                    motors.append(id_m1)
                    if self.links[id_m1, 2] != -1:
                        continue
                    id_m2 = None
                    for vm in v.neighbors():
                        if top.particle_type_of_vertex(vm) != 'motor':
                            continue
                        id_vm = top.particle_id_of_vertex(vm) - self._index_offset
                        if self.links[id_vm, 2] == -1:
                            id_m2 = id_vm
                            break
                    if id_m2 is None:
                        raise RuntimeError("New motor without any bond found.")
                    self.links[id_m1, 2] = id_m2
                    self.links[id_m2, 2] = id_m1
            new_map_tid_to_motors[tid] = motors
            new_map_tid_to_fids[tid] = fids
        assert new_map_fid_to_tid.keys() == self.map_filament_id_to_topology_id.keys()
        self.map_topology_id_to_filament_ids = new_map_tid_to_fids
        self.map_filament_id_to_topology_id = new_map_fid_to_tid
        self.map_topology_id_to_motors = new_map_tid_to_motors
        self._n_motors = (self.links[:self.n_beads_total, 2] != -1).sum()

    def reaction_function_motor_step(
            self,
            topology
    ) -> readdy.StructuralReactionRecipe:
        recipe = readdy.StructuralReactionRecipe(topology)
        top_id = self._get_topology_id(topology)
        motors = self._get_motors(top_id)
        if len(motors) == 0:
            return recipe
        self._update_required = True

        map_pid_to_vid = self._build_map_particle_id_to_vertex_index(topology)
        motor_id = motors[
            np.random.choice(len(motors))
        ]
        fwd_neighbor_id = self.links[motor_id, 1]
        if self.links[fwd_neighbor_id, 1] == -1:
            # forward neighbor is head of filament: do nothing
            return recipe
        if self.links[fwd_neighbor_id, 2] != -1:
            # forward neighbor is cross-link or motor: do nothing
            return recipe

        linked_motor_id = self.links[motor_id, 2]
        recipe.remove_edge(map_pid_to_vid[motor_id], map_pid_to_vid[linked_motor_id])
        self.links[motor_id, 2] = -1
        recipe.change_particle_type(map_pid_to_vid[motor_id], "core")
        recipe.change_particle_type(map_pid_to_vid[fwd_neighbor_id], "motor")
        recipe.add_edge(map_pid_to_vid[fwd_neighbor_id], map_pid_to_vid[linked_motor_id])
        self.links[fwd_neighbor_id, 2] = linked_motor_id
        self.links[linked_motor_id, 2] = fwd_neighbor_id
        self.map_topology_id_to_motors[top_id].remove(motor_id)
        self.map_topology_id_to_motors[top_id].append(fwd_neighbor_id)

        return recipe

    def rate_function_motor_count(self, topology, rate: float) -> float:
        top_id = self._get_topology_id(topology)
        n_motors = max(len(self.map_topology_id_to_motors[top_id]), 2)
        return rate * n_motors

    def rate_function_max_motor_count(self, topology1: Topology, topology2: Topology,
                                      rate: float, n_max_motors: int) -> float:
        r = max(rate * (1 - self._n_motors / n_max_motors), 0.0)
        return r

    def reaction_function_motor_unbind(self, topology):
        recipe = readdy.StructuralReactionRecipe(topology)
        top_id = self._get_topology_id(topology)
        motors = self._get_motors(top_id)
        if len(motors) == 0:
            return recipe
        self._update_required = True

        motor_pairs = set()
        for m in motors:
            m_other = self.links[m, 2]
            pair = (min(m, m_other), max(m, m_other))
            motor_pairs.add(pair)

        map_pid_to_vid = self._build_map_particle_id_to_vertex_index(topology)

        if len(motor_pairs) == 1:
            selected_pair = list(motor_pairs)[0]
        else:
            distances = np.empty((len(motor_pairs), 3))
            vertices = topology.get_graph().get_vertices()
            for i, p in enumerate(motor_pairs):
                _v1 = topology.position_of_vertex(vertices[map_pid_to_vid[p[0]]])
                _v2 = topology.position_of_vertex(vertices[map_pid_to_vid[p[1]]])
                v = self._get_minimum_image_vector_between_motor_pair(_v1, _v2)
                distances[i] = v
            distances = np.sqrt((distances ** 2).sum(1))
            idx = self._get_distance_weighted_random_index(distances)
            selected_pair = list(motor_pairs)[idx]

        self.links[selected_pair[0], 2] = -1
        self.links[selected_pair[1], 2] = -1
        filament_ids = self.map_topology_id_to_filament_ids[top_id]

        for fid in filament_ids:
            fil = self.filaments[fid]
            for m in selected_pair:
                if m in fil.motors:
                    fil.motors.remove(m)
        for m in selected_pair:
            recipe.change_particle_type(map_pid_to_vid[m], 'core')
        recipe.remove_edge(map_pid_to_vid[selected_pair[0]], map_pid_to_vid[selected_pair[1]])
        return recipe

    @staticmethod
    def _get_distance_weighted_random_index(distances):
        diff = (1 - distances) ** 2
        exp_E = np.exp(-diff)
        p = 1 - exp_E / exp_E.sum()
        possible_indices = np.arange(len(distances))
        p = p / p.sum()
        idx = np.random.choice(possible_indices, replace=False, p=p)
        return idx

    def _get_minimum_image_vector_between_motor_pair(self, _v1, _v2):
        v1 = np.empty(3)
        v2 = np.empty(3)
        for j in range(3):
            v1[j] = _v1[j]
            v2[j] = _v2[j]
        v = get_minimum_image_vector(v1, v2[np.newaxis, :], self.box)
        return v

    def reaction_function_detach(self, topology):
        self._update_required = True
        recipe = readdy.StructuralReactionRecipe(topology)
        top_id = self._get_topology_id(topology)
        filament_ids = self.map_topology_id_to_filament_ids[top_id]

        fil_id = filament_ids[
            np.random.choice(len(filament_ids))
        ]
        if len(self.filaments[fil_id].items) < 4:
            # filament is at minimum size: do nothing
            return recipe
        tail_id = self.filaments[fil_id].get_tail()
        fwd_neighbor = self.links[tail_id, 1]
        if self.links[fwd_neighbor, 2] != -1:
            # forward neighbor is motor or cross-link: do nothing
            return recipe

        map_pid_to_vid = self._build_map_particle_id_to_vertex_index(topology)
        self.links[tail_id, 1] = -1
        self.links[fwd_neighbor, 0] = -1
        self.filaments[fil_id].items.pop(0)
        self.map_tails_to_filament_ids.pop(tail_id)
        self.map_tails_to_filament_ids[fwd_neighbor] = fil_id
        recipe.separate_vertex(map_pid_to_vid[tail_id])
        recipe.change_particle_type(map_pid_to_vid[tail_id], "monomer")
        recipe.change_particle_type(map_pid_to_vid[fwd_neighbor], "tail")
        return recipe

    def rate_function_n_filaments(self, topology, rate: float) -> float:
        top_id = self._get_topology_id(topology)
        n_fils = len(self.map_topology_id_to_filament_ids[top_id])
        return n_fils * rate

    def reaction_function_attach(self, topology) -> readdy.StructuralReactionRecipe:
        self._update_required = True
        recipe = readdy.StructuralReactionRecipe(topology)
        top_id = self._get_topology_id(topology)
        filament_ids = self.map_topology_id_to_filament_ids[top_id]

        fil_id = filament_ids[
            np.random.choice(len(filament_ids))
        ]
        head_id = self.filaments[fil_id].items[-1]
        next_id = self.links[head_id, 0]

        next_position = None
        head_position = None
        head_vertex = None
        pids = []
        pids_min_offset = []
        for v in topology.get_graph().get_vertices():
            pids.append(topology.particle_id_of_vertex(v))
            pids_min_offset.append(topology.particle_id_of_vertex(v) - self._index_offset)
            if topology.particle_id_of_vertex(v) - self._index_offset == next_id:
                next_position = topology.position_of_vertex(v)
            if topology.particle_id_of_vertex(v) - self._index_offset == head_id:
                head_position = topology.position_of_vertex(v)
                head_vertex = v
            if next_position is None:
                continue
            if head_position is None:
                continue
            break
        if next_position is None:
            msg = "Unable to find second bead (id = {}) of Filament {} ".format(
                next_id,
                fil_id)
            msg += "in Topology {}".format(top_id)
            raise RuntimeError(msg)

        if head_position is None:
            msg = "Unable to find first bead (id = {}) of Filament {} ".format(
                head_id,
                fil_id)
            msg += "in Topology {}".format(top_id)
            raise RuntimeError(msg)
        head_pos = np.empty(3)
        next_pos = np.empty((1, 3))
        for i in range(3):
            head_pos[i] = head_position[i]
            next_pos[0, i] = next_position[i]
        direction = get_minimum_image_vector(head_pos + self.box / 2,
                                             next_pos + self.box / 2,
                                             self.box)[0]
        direction = direction / np.sqrt(np.sum(direction ** 2))
        length = np.random.randn() * self.sigma_length + 1
        angle = np.random.randn() * self.sigma_angle
        gamma = np.random.rand() * np.pi
        relative_position = np.array([length * np.cos(angle),
                                      length * np.sin(angle) * np.cos(gamma),
                                      length * np.sin(angle) * np.sin(gamma)])
        new_position = head_pos + rotation_matrix(direction).dot(relative_position)

        recipe.append_particle([head_vertex], 'head', new_position)
        recipe.change_particle_type(head_vertex, 'core')
        self.links[head_id, 1] = self.n_beads_total
        self.links[self.n_beads_total, 0] = head_id
        self.filaments[fil_id].items.append(self.n_beads_total)
        self.n_beads_total += 1
        FilamentHandler._global_n_beads_total += 1

        return recipe

    def write(self, particles, ndigits_t: int = 5):
        """
        Write current state of filaments (which beads belong to which filaments,
        defined via links between filamentous beads) to a HDF5 file.
        """
        if self.output_file is None:
            msg = "Can't write state of FilamentHandler, "
            msg += "no output folder was set."
            raise RuntimeError(msg)
        f = h5py.File(self.output_file, 'a')
        dataset_name_template = "{}/{:0" + str(ndigits_t) + "}"
        dataset_name_template_filaments = dataset_name_template + '/{}'
        name_ds_types = dataset_name_template.format('types', self._n_write_called)
        name_ds_links = dataset_name_template.format('links', self._n_write_called)
        name_ds_fil_ids = dataset_name_template_filaments.format(
            'filaments', self._n_write_called, 'ids'
        )
        name_ds_fil_tails = dataset_name_template_filaments.format(
            'filaments', self._n_write_called, 'tails'
        )
        bead_types = np.full(self.n_beads_total, 15, dtype='u1')
        types, ids, _ = particles

        for t, pid in zip(types, ids):
            idx = pid - self._index_offset
            if t == 'motor':
                assert (self.links[idx] != -1).all()
            elif t == 'tail':
                assert self.links[idx, 0] == -1
            elif t == 'head':
                assert self.links[idx, 1] == -1
            elif t == 'core':
                assert self.links[idx, 0] != -1
                assert self.links[idx, 1] != -1
                assert self.links[idx, 2] == -1, 'idx = {}; links[{}, 2] = {}'.format(
                    idx, idx, self.links[idx, 2]
                )
            else:
                continue
            bead_types[idx] = FilamentHandler.enum_map[t]
        ds_types = f.create_dataset(
            name_ds_types, data=bead_types,
            dtype=h5py.special_dtype(enum=('u1', FilamentHandler.enum_map))
        )
        ds_links = f.create_dataset(
            name_ds_links, data=self.links[:self.n_beads_total]
        )
        ds_fil_ids = f.create_dataset(
            name_ds_fil_ids, data=np.array(list(self.map_tails_to_filament_ids.values()))
        )
        ds_fil_tails = f.create_dataset(
            name_ds_fil_tails, data=np.array(list(self.map_tails_to_filament_ids.keys()))
        )
        f.attrs['n_datasets'] = self._n_write_called + 1
        f.close()

        self._n_write_called += 1

    def _build_map_particle_id_to_vertex_index(self, topology) -> Dict[int, int]:
        m = {}
        vertices = topology.get_graph().get_vertices()
        for i, v in enumerate(vertices):
            m[topology.particle_id_of_vertex(v) - self._index_offset] = i  # v.particle_index
        return m

    def _get_topology_id(self, topology) -> int:
        vertices = topology.get_graph().get_vertices()
        for v in vertices:
            if topology.particle_type_of_vertex(v) == 'tail':
                tail_id = topology.particle_id_of_vertex(v) - self._index_offset
                f_id = self.map_tails_to_filament_ids[tail_id]
                return self.map_filament_id_to_topology_id[f_id]
        raise RuntimeError("No bead of type 'tail' found in topology.")

    def _get_motors(self, topology_id: int) -> List[int]:
        return self.map_topology_id_to_motors[topology_id]

    def _detach_tail(self, filament_id: int) -> int:
        particle_id = self.filaments[filament_id].pop(0)
        self.links[particle_id] = -1
        return particle_id

    def _attach_monomer(self, filament_id: int, particle_id: int) -> int:
        id_head = self.filaments[filament_id][-1]
        self.filaments[filament_id].append(particle_id)
        self.links[id_head][1] = particle_id
        self.links[particle_id][0] = id_head
        return id_head
