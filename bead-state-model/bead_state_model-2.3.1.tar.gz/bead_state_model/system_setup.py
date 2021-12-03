from typing import List, Tuple, Dict, Any, Union
import os
import numpy as np
import readdy

from .components import load_beads, Filament, Bead, LinksArray
from .filament_handler import FilamentHandler

Topology = readdy._internal.readdybinding.api.top.Topology
Particle = readdy._internal.readdybinding.common.Particle
Vertex   = readdy._internal.readdybinding.api.top.Vertex
RDSystem = readdy.ReactionDiffusionSystem


def system_setup(
        box_size: Union[np.ndarray, List[float], Tuple[float, float, float]],
        n_beads_max: int,
        min_network_distance: int=6,
        diffusion_const: float=1.0,
        rate_motor_step: float=0,
        rate_motor_bind: float=0,
        rate_motor_unbind: float=0,
        reaction_radius_motor_binding: float=1.05,
        rate_attach: float=0,
        rate_detach: float=0,
        k_bend: float=26.0,
        k_stretch: float=20.0,
        k_repulsion: float=80.0,
        n_max_motors: int=None
) -> Tuple[readdy.ReactionDiffusionSystem, FilamentHandler]:
    """
    Create a readdy.ReactionDiffusionSystem and configure it for actomyosin simulations.
    This is mostly an elaborate wrapper around readdy.ReactionDiffusionSystem that defines
    a single topology filament, all the species of a filament (head, core, tail, motor),
    and reactions between them.

    :param box_size: Size of the simulation box.
    :param min_network_distance: Minimal number of edges in the graph of connected beads
                                 at which new bonds are allowed to form between two core beads
                                 that are less than reaction_radius_motor_binding apart. Below 
                                 this number, no bonds are allowed to form. This is to stop 
                                 direct neighbors in the graph (i.e. directly bound pairs
                                 of core beads) to turn into motors, so do not choose a value smaller
                                 than 2 (or even 3 or 4, depending on your 
                                 reaction_radius_motor_binding).
    :param diffusion_const: Diffusion constant of filamentous beads (head, core, tail, motor).
    :param rate_motor_step: Rate in 1/tau for motor steps to occur, where tau is the internal 
                            time scale.
    :param rate_motor_bind: Rate in 1/tau for core-core pairs to bind and transition their states
                            to motor. This binding can only happen for pairs that are less than
                            reaction_radius_motor_binding apart, and that are not connected with
                            less than min_network_distance edges.
    :param rate_motor_unbind: Rate in 1/tau for motor-motor pairs to unbind an change their states
                              to core.
    :param reaction_radius_motor_binding: Maximum distance at which two core beads can bind to become
                                          a motor-motor pair.
    :param rate_attach: Rate in 1/tau for filaments to grow by one bead. The previous head bead
                        transitions to state core, and a new head is attached.
    :param rate_detach: Rate in 1/tau for filaments to detach their tail bead. The core that was bound
                        to the tail becomes the new tail. If the tail is bound to a motor, this detachment
                        is suppressed.
    :param k_bend: Bending modulus, i.e. the constant for angular forces. A harmonic potential penalizes
                   curvature of filaments and tries to keep the filaments straight.
    :param k_stretch: Spring constant trying to keep neighbouring beads of a filament at a distance of
                      d, where d is the bead diameter. Note that the mean distance is larger than d, though,
                      due to repulsion between beads at distances smaller than d.
    :param k_repulsion: Force constant for repulsion between beads. This interaction is defined via a repulsive
                        harmonic potential.
    :param n_beads_max: Defines the maximum number of beads in the system. Memory is allocated statically.
                        This is to keep single, possibly faulty defined simulations from crashing the whole
                        computer due to memory error. This might not occur during the simulations, but can also
                        be an issue for storing huge amounts of data, or reading data from file, where readdy
                        requires quite large amounts of memory.
                        **You have to think about an upper limit of beads beforehand and set it
                        via this parameter!**
    :param n_max_motors: Maximum number of motors in simulation. No new motor pairs will form,
                         if the current number of motors is equal to or exceeds this.

    :return: [0] Configured readdy.ReactionDiffusionSystem, [1] A FilamentHandler instance initialized
             with all specified rates.
    """
    k_bend = k_bend/2
    k_stretch = k_stretch/2
    box_size = np.array(box_size)
    system = readdy.ReactionDiffusionSystem(box_size=box_size, unit_system=None)
    fh = FilamentHandler(n_beads_max, box_size, k_bend, k_stretch)

    if rate_detach > 0:
        system.add_species('monomer', 0.0)
        system.reactions.add_decay('monomer clean-up', 'monomer', 1e8)
    
    _configure_filament_topology(system, diffusion_const, k_bend, k_stretch, k_repulsion)

    if rate_motor_bind > 0:
        if n_max_motors is None:
            rate = rate_motor_bind
        else:
            def _rate_func(top1, top2):
                return fh.rate_function_max_motor_count(top1, top2, rate_motor_bind,
                                                        n_max_motors)
            rate = _rate_func
        react_str = "link: filament(core) + filament(core) -> filament(motor--motor)"
        react_str += "[self=true, distance>{}]".format(min_network_distance-1)
        system.topologies.add_spatial_reaction(
            react_str, rate=rate, radius=reaction_radius_motor_binding
        )

    if rate_motor_unbind > 0:
        system.topologies.add_structural_reaction(
            'motor-unbind',
            'filament',
            reaction_function=fh.reaction_function_motor_unbind,
            rate_function=lambda x: fh.rate_function_motor_count(x, rate_motor_unbind)
        )
        
    if rate_attach > 0:
        system.topologies.add_structural_reaction(
            'monomer-attach',
            'filament',
            reaction_function=fh.reaction_function_attach,
            rate_function=lambda x: fh.rate_function_n_filaments(x, rate_attach)
        )

    if rate_detach > 0:
        system.topologies.add_structural_reaction(
            'monomer-detach',
            'filament',
            reaction_function=fh.reaction_function_detach,
            rate_function=lambda x: fh.rate_function_n_filaments(x, rate_detach)
        )

    if rate_motor_step > 0:
        system.topologies.add_structural_reaction(
            'motor-step',
            'filament',
            reaction_function=fh.reaction_function_motor_step,
            rate_function=lambda x: fh.rate_function_motor_count(x, rate_motor_step)
        )

    return system, fh


def simulation_setup(
        system: readdy.ReactionDiffusionSystem,
        filament_handler: FilamentHandler,
        kernel: str,
        force_monitor_threshold: float=None,
        simulation_keyword_arguments: Dict[str, Any]={}
) -> readdy.Simulation:
    """
    Create simulation instance and set up reaction_counts observable
    as a trigger to update the filament_handler in every time step.
    Note that observable reaction_counts is blocked due to this!
    You can specify a force threshold for monitoring. This will block
    observable force, and use this observable for a callback function
    that writes the number of particles exceeding this threshold at
    every time step. An alarmingly high force e.g. would be greater than
    0.5 / dt, since this means a bead of a filament (radius = 0.5, diffusion coeff. = 1.0)
    would be caused to move half it's diameter by this force.

    :param system: The system that was created with function system_setup.
    :param filament_handler: FilamentHandler that was created with function ``system_system_setup``.
    :param kernel: Either ``"SingleCPU"`` or ``"CPU"`` to select one of the compute kernels
                   readdy provides.
    :param force_monitor_threshold: Forces above this threshold will be logged. The logging
                                    simply counts the occurrences how often this threshold was exceeded
                                    at each time step. If this is not None, a log file
                                    ``force_monitor.log`` is placed into the folder of
                                    the ``simulation.output_file`` .
    :param simulation_keyword_arguments: A dictionary that is passed as keyword arguments
                                         to the system.simulation call.
    """
    simulation = system.simulation(kernel, **simulation_keyword_arguments)
    filament_handler.simulation = simulation
    simulation.observe.reaction_counts(
        stride=1,
        callback=filament_handler.update,
        save=False
    )
    if force_monitor_threshold is None:
        return simulation

    simulation.force_monitor_output_file = None
    simulation.observe.forces(
        stride=1, save=False,
        callback=lambda x: _force_monitor_callback(x, force_monitor_threshold, simulation)
    )
    return simulation


def add_filaments_from_file(
        simulation: readdy.Simulation,
        file_beads: str,
        offset: np.ndarray
) -> Tuple[List[Bead], List[Filament], LinksArray]:
    """
    Add filaments specified in given beads file to simulation instance. Note that any
    non-filament particles have to be registered with the ``filament_handler`` before you
    call this function! This function can only handle non-bound filaments! Any bonds from
    one filament to another via motors are ignored during set up! If you want to
    initialize your system with existing bonds, use the function ``add_filaments``.

    :param simulation: readdy.Simulation instance created via function ``simulation_setup``.
    :param file_beads: Path to file defining the beads. See documentation for format of that file.
    :param offset: Numpy array defining offset in [x, y, z] that is added to the coordinates of
                   the beads. I mostly use this to be able to use bead positions from other
                   simulation software where a simulation box extends from [0, 0, 0] to
                   [X, Y, Z], whereas in readdy the box rather is from [-X/2, -Y/2, -Z/2]
                   to [X/2, Y/2, Z/2]. So setting offset to [-X/2, -Y/2, -Z/2] maps the first
                   to the latter.
    :return: [0] List of Bead objects (position, state, bonds),
             [1] List of Filament objects (head, tail, bead indices),
             [2] Numpy array defining the bonds between beads as a linked list
             (-1 means no bond). See documentation for meaning of columns and rows.
    """
    beads, filaments, links = load_beads(file_beads)
    filament_topologies = []
    filament_id = 0
    for i, b in enumerate(beads):
        if b.prv != -1:
            continue
        fil = Filament(filament_id, i, beads)
        filament_id += 1
        if len(fil.items) < 3:
            raise RuntimeError("Too short filament encountered! Error can't be handled yet.")
        top = simulation.add_topology(
            "filament",
            fil.to_readdy_species_list(),
            fil.to_particle_coordinates(beads) + offset
        )
        graph = top.get_graph()
        for j in range(len(fil.items)-1):
            graph.add_edge(j, j+1)
        filament_topologies.append(top)
        
    return beads, filaments, links


def add_filaments(
        simulation: readdy.Simulation,
        positions: np.ndarray,
        filaments: List[Filament],
        links: LinksArray
):
    """
    Add filaments to simulation instance. Note that any non-filament particles have
    to be registered with the ``filament_handler`` before you call this function!

    :param simulation: readdy.Simulation instance created via function ``simulation_setup``.
    :param positions: Positions of beads.
    :param filaments: List of Filament instances (defining heads, tails, beads
                      of filaments).
    :param links: Numpy array defining the bonds between beads as a linked list
                  (-1 means no bond). See documentation for meaning of columns and rows.
    """
    # Rearrange filaments and links to have
    # linked filaments in consecutive batches.
    # Because they have to be added bundled together via the
    # simulation.add_topology method.
    map_fil_idx, map_bead_idx, filaments_new, links_new, topologies =\
        _filaments_to_topology_inits(filaments, positions, links)

    for species, positions, edges in topologies:    
        top = simulation.add_topology(
            "filament",
            species,
            positions
        )
        graph = top.get_graph()
        for e in edges: 
            graph.add_edge(*e)
    return map_fil_idx, map_bead_idx, filaments_new, links_new


def _filaments_to_topology_inits(
        filaments: List[Filament],
        positions: np.ndarray,
        links: LinksArray
) -> Tuple[
    np.ndarray,
    np.ndarray,
    List[Filament],
    LinksArray,
    List[Tuple[List[str], np.ndarray, List[Tuple[int, int]]]]
]:
    """
    Rearrange filaments and links to have
    linked filaments in consecutive batches.
    Because they have to be added bundled together via the
    simulation.add_topology method.
    """
    map_fil_to = []
    map_bead_to = []
    filaments_new = []
    links_new = np.full_like(links, -1)
    topologies = []
    skip = []
    for f in range(len(filaments)):
        if f in skip:
            continue
        indices_beads_current_topology = []
        map_fil_to.append(f)
        fil = filaments[f]
        n_beads_before = len(map_bead_to)
        
        # create lists for ``new_fil``, for which the bead ID 
        # can be different from the original ``fil``
        indices_new_fil = [i + n_beads_before for i in range(len(fil.items))]
        motors_new_fil = [indices_new_fil[fil.items.index(m)] for m in fil.motors]
        new_fil = Filament(fil.id, indices_new_fil, motors_new_fil)
        filaments_new.append(new_fil)

        map_bead_to += fil.items
        indices_beads_current_topology += fil.items
        species = fil.to_readdy_species_list()
        pos_f = positions[fil.items]
        edges = []
        for i in range(len(fil.items)-1):
            e = (i, i+1)
            edges.append(e)
            links_new[i+n_beads_before, 1] = i+1+n_beads_before
            links_new[i+1+n_beads_before, 0] = i+n_beads_before

        if len(fil.motors) == 0:
            topologies.append((species, pos_f, edges))
            continue
        connected_filaments = _get_connected_filaments(fil.motors, links, filaments,
                                                       start=f+1, skip=skip)
        pos_cfs = []
        n_beads_before_cf = n_beads_before + len(fil.items)
        for cf in connected_filaments:
            cfil = filaments[cf]

            # create lists for ``new_fil``, for which the bead ID 
            # can be different from the original ``fil``
            indices_new_fil = [i + n_beads_before_cf for i in range(len(cfil.items))]
            motors_new_fil = [indices_new_fil[cfil.items.index(m)] for m in cfil.motors]
            new_fil = Filament(cfil.id, indices_new_fil, motors_new_fil)
            filaments_new.append(new_fil)
            
            map_bead_to += cfil.items
            pos_cfs.append(positions[cfil.items])
            map_fil_to.append(cf)
            
            species += cfil.to_readdy_species_list()
            for i in range(len(cfil.items)-1):
                e = (i+n_beads_before_cf-n_beads_before, i+1+n_beads_before_cf-n_beads_before)
                links_new[i+n_beads_before_cf, 1] = i+1+n_beads_before_cf
                links_new[i+1+n_beads_before_cf, 0] = i+n_beads_before_cf
                edges.append(e)
            indices_beads_current_topology += cfil.items
            n_beads_before_cf += len(cfil.items)

        fil_top = [f] + connected_filaments
        motor_edges = _get_motor_edges([filaments[idx] for idx in fil_top],
                                       links,
                                       indices_beads_current_topology)
        for m1, m2 in motor_edges:
            links_new[n_beads_before+m1, 2] = m2+n_beads_before
            links_new[n_beads_before+m2, 2] = m1+n_beads_before
        edges += motor_edges
        pos_top = np.concatenate([pos_f] + pos_cfs)

        topologies.append((species, pos_top, edges))
    map_fil_from = np.empty(len(map_fil_to), dtype=int)
    map_bead_from = np.full(max(map_bead_to)+1, -1, dtype=int)
    for i, f in enumerate(map_fil_to):
        map_fil_from[f] = i
    for i, b in enumerate(map_bead_to):
        map_bead_from[b] = i
    return map_fil_from, map_bead_from, filaments_new, links_new, topologies
    

def _get_connected_filaments(
        motors: List[int],
        links: LinksArray,
        filaments: List[Filament],
        start: int,
        skip: List[int]
) -> List[int]:
    """
    Recursively find filaments connected to current filament via given motors.
    
    :param motors: List of bead indices of motors of current filament.
    :param links: Array containing all links of all beads of the system.
    :param filaments: List of all filaments in the system.
    :param start: Index at which to start the search, this should usually
                  be the index of the current filament plus 1.
    :param skip: List of filament indices to be skipped during the search. 
                 This list can get items appended to during the execution 
                 of this function.
    
    :return: List of filament indices connected via the given motors.
    """
    connected_fil = []
    for m in motors:
        connected_m = links[m, 2]
        for f in range(start, len(filaments)):
            if f in skip:
                continue
            fil = filaments[f]
            if connected_m not in fil.motors:
                continue
            connected_fil.append(f)
            skip.append(f)
            motors_f = fil.motors.copy()
            motors_f.pop(motors_f.index(connected_m))
            connected_fil += _get_connected_filaments(motors_f, links, filaments,
                                                      start, skip)
            break
    return connected_fil


def _get_motor_edges(
        filaments_current_topology: List[Filament],
        links: LinksArray,
        indices_beads_current_topology: List[int]
) -> List[Tuple[int, int]]:
    """
    Determine edges between motor beads for current topology. ``filaments_current_topology`` 
    is the list of filaments that
    are part of the current topology. Important for edges in readdy are the indices 
    of the beads in the current topology. For that, the particle IDs of the motors 
    (as stored in Filament.motors) have to be mapped to the indices of the beads 
    as they are appended to the list ``indices_beads_current_topology``.
    """
    filaments = filaments_current_topology
    motors_global_indices = []
    for fil in filaments:
        motors_global_indices += fil.motors
    motor_pairs = []
    skip = []
    for m in motors_global_indices:
        if m in skip:
            continue
        connected_m = links[m, 2]
        assert connected_m != -1
        skip.append(connected_m)
        pair = (indices_beads_current_topology.index(m),
                indices_beads_current_topology.index(connected_m))
        motor_pairs.append(pair)
    return motor_pairs
    
                
def _add_filament(simulation: readdy.Simulation, init_pos: np.ndarray) -> Topology:
    n_beads = len(init_pos)
    fil = ['tail'] + ['core'] * (n_beads-2) + ['head']
    top = simulation.add_topology(
        "filament", fil, init_pos
    )
    graph = top.get_graph()
    for i in range(n_beads-1):
        graph.add_edge(i, i+1)
        
    return top


def _force_monitor_callback(forces, threshold, simulation):
    if simulation.force_monitor_output_file is None:
        simulation.force_monitor_output_file =\
            os.path.join(os.path.split(simulation.output_file)[0], 'force_monitor.log')
        with open(simulation.force_monitor_output_file, 'wt') as fh:
            fh.write('# force log, counting particles with force > {}\n'.format(threshold))

    forces_array = np.empty((len(forces), 3))
    for i, f in enumerate(forces):
        for j in range(3):
            forces_array[i, j] = f[j]
    thr2 = threshold**2
    abs_forces_2 = np.sum(forces_array**2, axis=1)
    w = np.where(abs_forces_2 > thr2)[0]
    with open(simulation.force_monitor_output_file, 'at') as fh:
        fh.write('{}\n'.format(len(w)))


def _configure_filament_topology(system: readdy.ReactionDiffusionSystem,
                                 diffusivity: float,
                                 k_bend: float,
                                 k_stretch: float,
                                 k_repulsion: float):
    
    system.add_topology_species("head", diffusivity)
    system.add_topology_species("tail", diffusivity)

    system.add_topology_species("core", diffusivity)
    system.add_topology_species("motor", diffusivity)

    system.topologies.add_type("filament")

    tuples = [
        ("head", "core"),
        ("core", "core"),
        ("core", "tail"),
        ("core", "motor"),
        ("motor", "motor"),
        ("head", "motor"),
        ("motor", "tail")
    ]
    
    for (t1, t2) in tuples:
        system.topologies.configure_harmonic_bond(t1, t2, force_constant=k_stretch, length=1.0)
    
    tuples += [('head', 'head'), ('tail', 'tail')]

    for (t1, t2) in tuples:
        system.potentials.add_harmonic_repulsion(t1, t2,
                                                 force_constant=k_repulsion,
                                                 interaction_distance=1.0)
        
    triplets = [
        ("head", "core", "core"),
        ("core", "core", "core"),
        ("core", "core", "tail"),
        ("head", "core", "tail"),
        ("head", "motor", "core"),
        ("head", "core", "motor"),
        ("head", "motor", "tail"),
        ("core", "motor", "core"),
        ("core", "core", "motor"),
        ("core", "motor", "tail"),
        ("motor", "core", "tail")
    ]

    for (t1, t2, t3) in triplets:
        system.topologies.configure_harmonic_angle(
            t1, t2, t3, force_constant=k_bend,
            equilibrium_angle=np.pi)


def _rate_function_motor_step(topology: Topology, rate) -> float:
    motors_and_forward_neighbors = _get_valid_motors_and_forward_neighbors(topology)
    return len(motors_and_forward_neighbors)*rate


def _reaction_function_motor_step(topology: Topology):
    recipe = readdy.StructuralReactionRecipe(topology)
    motors_and_forward_neighbors = _get_valid_motors_and_forward_neighbors(topology)    
    
    motor, fwd_neighbor = motors_and_forward_neighbors[
        np.random.choice(len(motors_and_forward_neighbors))
    ]
    linked_motor = _get_linked_motor(topology, motor)
    recipe.remove_edge(motor.particle_index,
                       linked_motor.particle_index)
    recipe.change_particle_type(motor.particle_index, "core")
    recipe.change_particle_type(fwd_neighbor.particle_index, "motor")
    recipe.add_edge(fwd_neighbor, linked_motor)
    
    return recipe


def _get_linked_motor(topology: Topology, motor: Vertex) -> Vertex:
    for v in motor:
        v = v.get()
        if topology.particle_type_of_vertex(v) == "motor":
            return v
    raise RuntimeError("no linked motor found")


def _get_valid_motors_and_forward_neighbors(topology: Topology) -> List[Tuple[int, int]]:
    vertices = topology.get_graph().get_vertices()
    motor_neighbor_pairs = []
    for v in vertices:
        if topology.particle_type_of_vertex(v) != "motor":
            continue
        v_fwd_neighbor = _get_forward_neighbor2(topology, v)
        if v_fwd_neighbor is None:
            continue
        motor_neighbor_pairs.append((v, v_fwd_neighbor))
    return motor_neighbor_pairs


def _get_forward_neighbor2(topology: Topology,
                           v: Vertex) -> Vertex:
    if topology.particle_type_of_vertex(v) == 'head':
        return None
    if topology.particle_type_of_vertex(v) == 'tail':
        return v.neighbors()[0].get()
    if _all_neighbors_motors(topology, v):
        return None
    for v_neighbor in v.neighbors():
        v_neighbor = v_neighbor.get()
        if topology.particle_type_of_vertex(v_neighbor) == 'head':
            return None
        if _neighbor_leads_to_filament_head(topology, v, v_neighbor):
            return v_neighbor
    return None


def _neighbor_leads_to_filament_head(topology, v, v_neighbor) -> bool:
    if topology.particle_type_of_vertex(v) != 'motor':
        msg = "type of vertex {} is != 'motor', this function is safe to use "
        msg += "only for 'motor' as starting vertex"
        raise ValueError(msg.format(v.particle_index))
           
    if topology.particle_type_of_vertex(v_neighbor) == 'motor':
        return False
    if topology.particle_type_of_vertex(v_neighbor) == 'tail':
        return False

    passed_vertices = [v, v_neighbor]
    passed_indices  = [v.particle_index, v_neighbor.particle_index]
    v_current = v_neighbor

    # walk along edges until end of filament is reached
    while True:
        current_length = len(passed_vertices)
        for v_nn in v_current:
            v_nn = v_nn.get()
            if v_nn.particle_index in passed_indices:
                continue
            if (topology.particle_type_of_vertex(v_current) == 'motor' and
                topology.particle_type_of_vertex(v_nn) == 'motor'):
                continue
            if topology.particle_type_of_vertex(v_nn) == 'head':
                return True
            if topology.particle_type_of_vertex(v_nn) == 'tail':
                return False
            v_current = v_nn
            passed_vertices.append(v_current)
            passed_indices.append(v_current.particle_index)
            break
        if current_length == len(passed_vertices):
            return False
        current_length = len(passed_vertices)


def _get_forward_neighbor(topology: Topology,
                         v: Vertex) -> Vertex:
    if topology.particle_type_of_vertex(v) == 'head':
        return None
    for v_neighbor in v:
        v_neighbor = v_neighbor.get() # dereference to get the actual Vertex
        if topology.particle_type_of_vertex(v_neighbor) == "head":
            return v_neighbor
        if topology.particle_type_of_vertex(v_neighbor) == "tail":
            continue
        if topology.particle_type_of_vertex(v_neighbor) == "motor":
            continue
        v_fwd_neighbor = _get_forward_neighbor(topology, v_neighbor)
        if v_fwd_neighbor is None:
            continue
        return v_neighbor
    return None


def _rate_function_dissolve(topology, rate):
    """ 
    if the topology has at least (head, core, tail),
    tail shall be removed with fixed probablility per time
    """
    vertices = topology.get_graph().get_vertices()
    if len(vertices) > 3:
        return rate
    else:
        return 0.


def _reaction_function_dissolve(topology):
    """
    Find tail and remove it,
    and make adjacent core particle the new tail.
    """
    recipe = readdy.StructuralReactionRecipe(topology)
    vertices = topology.get_graph().get_vertices()

    tail_idx = None
    adjacent_core_idx = None
    for v in vertices:
        if topology.particle_type_of_vertex(v) == 'tail':
            adjacent_core_idx = v.neighbors()[0].get().particle_index
            tail_idx = v.particle_index

    recipe.separate_vertex(tail_idx)
    recipe.change_particle_type(tail_idx, "substrate")
    recipe.change_particle_type(adjacent_core_idx, "tail")

    return recipe


def _all_neighbors_motors(topology: Topology, vertex: Vertex) -> bool:
    for v in vertex:
        v = v.get()
        if topology.particle_type_of_vertex(v) != 'motor':
            return False
    return True
