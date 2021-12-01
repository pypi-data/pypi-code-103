from typing import List, Iterable, Union, Tuple, Dict, Any
import os
from math import isclose
import numpy as np
from scipy.spatial.transform import Rotation
from ..analysis.analyser import Analyser

FilamentID = int
BeadID = int
XYZTuple = Tuple[int, float, float, float]

class XYZExporter:

    def __init__(self, particle_type: str=None):
        self.particle_type = particle_type
        self.selected_filaments = None
        self.selected_beads = None
        self.analyser = None
        self.fname_template = None
        self.output_folder = None
        self.highlighted_beads = None
        self.CoM = False

    @staticmethod
    def export_all(
            analyser: Analyser,
            folder: str,
            fiber_radius: float=0.1,
            name_non_filament_particles='non_filament',
            name_links='link',
            frames: Union[List[int], None]=None
    ):
        trajectories_filaments = analyser.get_trajectories_filaments(minimum_image=True)
        if frames is None:
            frames = np.arange(len(trajectories_filaments))

        os.makedirs(folder, exist_ok=True)

        fname_fibers = os.path.join(folder, 'fibers.xyz')
        fname_non_fil = os.path.join(folder, name_non_filament_particles + '.xyz')
        fname_links = os.path.join(folder, name_links + '.xyz')

        XYZExporter.export_fibers(analyser, fname_fibers, fiber_radius,
                                  trajectories_filaments, frames)
        XYZExporter.export_non_filament_particles(analyser, fname_non_fil,
                                                  name_non_filament_particles, frames)
        XYZExporter.export_links(analyser, fname_links, name_links,
                                 trajectories_filaments,
                                 radius=fiber_radius*1.5,
                                 frames=frames)

    @staticmethod
    def export_fibers(
            analyser: Analyser,
            fname: str,
            fiber_radius: float,
            trajectories: np.ndarray,
            frames: List[int]
    ):
        
        fh = open(fname, 'wt')

        trajectories = trajectories
        filaments_all = analyser.data_reader.get_filaments_all()
        periodic_box = analyser.data_reader.read_box_size()
        periodic_box = periodic_box[1] - periodic_box[0]

        for f in frames:
            filaments = filaments_all[f]
            traj_t = trajectories[f]

            n_particles = 0
            block_xyz = ""
        
            for fil in filaments:
                n, b = XYZExporter._filament_to_xyz(traj_t[fil.items], periodic_box, fiber_radius)
                block_xyz += b
                n_particles += n

            block_xyz = "{}\n\n".format(n_particles) + block_xyz
            fh.write(block_xyz)
            
        fh.close()

    @staticmethod
    def export_non_filament_particles(
            analyser: Analyser,
            fname: str,
            label: str,
            frames: List[int],
            particle_range: Tuple[int, int]=None,
    ):
        trajectories = analyser.get_trajectories_non_filament(minimum_image=True)
        if particle_range is not None:
            trajectories = trajectories[:, particle_range[0]:particle_range[1]]

        fh = open(fname, 'wt')

        for f in frames:
            traj_f = trajectories[f]
            n_particles = len(traj_f)
            block_xyz = ""
            for p in traj_f:
                block_xyz += f"{label} {p[0]:.2f} {p[1]:.2f} {p[2]:.2f}\n"

            block_xyz = "{}\n\n".format(n_particles) + block_xyz
            fh.write(block_xyz)
        
        fh.close()

    @staticmethod
    def export_links(analyser: Analyser, fname: str, label: str, 
                     trajectories: np.ndarray, radius: float, frames: List[int]):

        periodic_box = analyser.data_reader.read_box_size()
        periodic_box = periodic_box[1] - periodic_box[0]

        links = analyser.data_reader.get_links_all()

        fh = open(fname, 'wt')

        for f in frames:
            traj_t = trajectories[f]
            links_t = links[f]

            w = np.where(links_t[:, 2] != -1)[0]
            pairs = []
            skip = []
            for wi in w:
                if wi in skip:
                    continue
                other = links_t[wi, 2]
                assert other in w
                pairs.append((wi, other))
                skip.append(other)

            n_particles = 0
            block_xyz = ""
            for p in pairs:
                n, b = XYZExporter._filament_to_xyz(traj_t[(p,)], periodic_box, radius,
                                                    label)
                block_xyz += b
                n_particles += n

            if len(pairs) == 0:
                n_particles = 1
                line = "{} {:.2f} {:.2f} {:.2f} {:.4f} {:.4f} {:.4f} {:.4f} {:.2f} {:.2f}\n"
                block_xyz += line.format(
                    'dummy', *([0.0]*9))

            block_xyz = "{}\n\n".format(n_particles) + block_xyz
            fh.write(block_xyz)

        fh.close()
                     
    @staticmethod
    def _filament_to_xyz(coords: np.ndarray, periodic_box: np.ndarray,
                         fiber_radius: float,
                         label: str=None) -> Tuple[int, str]:

        if label is None:
            label_tail = 'tail'
            label_core = 'core'
            label_head = 'head'
        else:
            label_tail = label
            label_core = label
            label_head = label

        count = 0
        xyz = ""

        shifted_coords = coords + periodic_box/2
        
        shifted_coord_sets = split_filament_coords_at_borders(shifted_coords, periodic_box)

        for i in range(len(shifted_coord_sets)):
            c = shifted_coord_sets[i] - periodic_box/2                

            centers = (c[1:] + c[:-1]) * 0.5
            segments = c[1:] - c[:-1]
            slengths = np.sqrt((segments**2).sum(1))
            orientations = segments / slengths[:, np.newaxis]

            xyz_c = ""
        
            line = "{} {:.2f} {:.2f} {:.2f} {:.4f} {:.4f} {:.4f} {:.4f} {:.2f} {:.2f}\n"
            specifier = np.array([label_core]*len(centers))
            if i == 0:
                specifier[0] = label_tail
            if i == len(shifted_coord_sets)-1:
                specifier[-1] = label_head

            for j in range(len(centers)):
                theta, phi = get_angles(orientations[j])
                r = Rotation.from_euler('yz', [theta, phi])
                quat = r.as_quat()

                xyz_c += line.format(
                    specifier[j],
                    centers[j, 0],
                    centers[j, 1],
                    centers[j, 2],
                    quat[0],
                    quat[1],
                    quat[2],
                    quat[3],
                    fiber_radius,
                    slengths[j]
                )
            count += centers.shape[0]
            xyz += xyz_c
        return count, xyz
        
    def export(self, analyser,
               t: Union[int, Iterable[int]],
               selected_filaments: Iterable[FilamentID]=None,
               selected_beads: Iterable[BeadID]=None,
               highlighted_beads: Union[Dict[int, List[BeadID]],
                                        List[BeadID]]=None,
               label: str=None,
               CoM: bool=False):
        raise NotImplementedError('needs to be updated for new analyser (not rwfilaments_analyser)')
        self.analyser = analyser        
        self.output_folder = os.path.join(analyser.dirname, 'xyz_export')
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)
        if label is not None:
            self.output_folder = os.path.join(self.output_folder, label)
            if not os.path.exists(self.output_folder):
                os.mkdir(self.output_folder)
        self.selected_beads = selected_beads
        self.selected_filaments = selected_filaments
        self.highlighted_beads = highlighted_beads
        self.CoM = CoM

        if isinstance(t, int):
            self.fname_template = 'beads.xyz'
            self._export_single_file(t)
        else:
            t_max = t[-1]
            self.fname_template = f'beads_{{t:0{len(str(t_max))}}}.xyz'
            out_str = f"exporting for t = {{ti:0{len(str(t_max))}}}/{{t_max:0{len(str(t_max))}}}"
            for ti in t:
                print(out_str.format(ti=ti, t_max=t_max), end='\r')
                self._export_single_file(ti)
            print()

        self.selected_filaments = None
        self.output_folder = None
        self.selected_beads = None
        self.analyser = None
        self.fname_template = None
        self.highlighted_beads = None
        self.CoM = False

    def _get_xyz_data(self, t: int) -> List[XYZTuple]:
        if self.particle_type is not None:
            raise RuntimeWarning("particle_type parameter does not do anything yet!")
        xyz_data = []
        coords = self.analyser.get_coordinates(True)[t]
        if self.CoM:
            coords = coords - coords.mean(0)
        indices = self._get_selected_beads(t)
        bids = self.analyser.data_reader.data_set_bead_ids[t]
        for idx in indices:
            ci = coords[idx]
            ptype = self._get_particle_type(bids[idx])
            xyz_data.append((ptype, ci[0], ci[1], ci[2]))
        
        return xyz_data        
        
    def _get_particle_type(self, bid: BeadID) -> int:
        if self.highlighted_beads is None:
            return 0
        if isinstance(self.highlighted_beads, list):
            if bid in self.highlighted_beads:
                return 1
            return 0

        for k in self.highlighted_beads:
            if bid in self.highlighted_beads[k]:
                return k
        return 0

    def _get_selected_beads(self, t: int) -> np.ndarray:
        bids = self.analyser.data_reader.data_set_bead_ids[t]
        if self.selected_filaments is None and self.selected_beads is None:
            return np.arange(len(bids))[bids != -1]
        indices = set()
        if self.selected_beads is not None:
            for idx, bid in enumerate(bids):
                if bid in self.selected_beads:
                    indices.add(idx)
        if self.selected_filaments is None:
            return np.array(indices)

        fidxerd = self.analyser.get_filament_indexer_dict()

        for fid in self.selected_filaments:
            fidxer = fidxerd[fid][t]
            indices.update(fidxer)

        return np.array(list(indices))

    def _export_single_file(self, t: int):
        f = open(os.path.join(self.output_folder, self.fname_template.format(t=t)), 'wt')
        xyz_data = self._get_xyz_data(t)
        f.write(f'{len(xyz_data)}\n\n')
        for xyz_i in xyz_data:            
            f.write('{} {} {} {}\n'.format(*xyz_i))
        f.close()


def get_angles(v: np.ndarray) -> Tuple[float, float]:
    """
    Get angles theta, phi in spherical coordinates of vector v.
    """
    theta = np.arccos(v[2])
    # phi = np.arccos(v[0]/np.sin(theta))
    phi = np.arctan2(v[1], v[0])
    return theta, phi


def minimum_image_projection(
        coords: np.ndarray,
        box: Union[np.ndarray, List[float]]) -> np.ndarray:
    proj = np.empty_like(coords)
    for i in range(len(box)):
        proj[:, i] = coords[:, i] -\
            np.floor_divide(coords[:, i], box[i]) * box[i]
    return proj


def split_filament_coords_at_borders(ordered_bead_coords: np.ndarray,
                                     box) -> List[np.ndarray]:
    """
    @param ordered_bead_coords Coordinates of beads, have to be corrected via minimum image!
    """
    coordinate_sets = []
    diff = ordered_bead_coords[1:] - ordered_bead_coords[:-1]
    shifts = _compute_shifts_array(diff, box)
    shifts_at = np.where(shifts != 0)
    if len(shifts_at[0]) == 0:
        return [ordered_bead_coords]
    shifts_at_n, shifts_at_i, r_cuts = _sort_conflicting_shifts(shifts_at[0], shifts_at[1],
                                                                ordered_bead_coords, diff,
                                                                shifts, box)
    shifted_diffs = diff + shifts
    n_prev = shifts_at_n[0]
    prev_virtual_bead = None

    coord_set, prev_virtual_bead = _generate_coord_set_before_first_split(
        ordered_bead_coords[:shifts_at_n[0] + 1], n_prev, r_cuts[0], shifted_diffs)
    coordinate_sets.append(coord_set)
    for j, n in enumerate(shifts_at_n[1:]):
        j = j+1
        set_shape = list(ordered_bead_coords.shape)
        if n == n_prev:
            num_points = 2
        else:
            num_points = n - n_prev + 2
        set_shape[0] = num_points
        coord_set = np.empty(tuple(set_shape))
        if prev_virtual_bead is not None:
            prev_i = shifts_at_i[j-1]
            if isclose(prev_virtual_bead[prev_i], box[prev_i], abs_tol=box[prev_i] * 0.01):
                prev_virtual_bead[prev_i] -= box[prev_i]
            else:
                prev_virtual_bead[prev_i] += box[prev_i]
            coord_set[0] = prev_virtual_bead
        if n == n_prev:
            virtual_bead = coord_set[0] + (r_cuts[j] - r_cuts[j-1]) * shifted_diffs[n]
        else:
            coord_set[1: -1] = ordered_bead_coords[n_prev+1: n+1]
            virtual_bead = ordered_bead_coords[n] + r_cuts[j] * shifted_diffs[n]
        prev_virtual_bead = virtual_bead
        coord_set[-1] = virtual_bead

        coordinate_sets.append(coord_set)
        n_prev = n
        
    coord_set = _generate_coord_set_after_last_split(
        ordered_bead_coords, n_prev, shifts_at_i, prev_virtual_bead, box)
    
    coordinate_sets.append(coord_set)
    
    return coordinate_sets


def _generate_coord_set_before_first_split(bead_coords_before_split, n, r_cut, shifted_diffs):
    coord_set_shape = list(bead_coords_before_split.shape)
    coord_set_shape[0] = coord_set_shape[0] + 1
    coord_set = np.empty(tuple(coord_set_shape))
    coord_set[:-1] = bead_coords_before_split[:]
    virtual_bead = bead_coords_before_split[-1] + r_cut * shifted_diffs[n]
    coord_set[-1] = virtual_bead
    return coord_set, virtual_bead
    

def _generate_coord_set_after_last_split(ordered_bead_coords, n_prev,
                                         shifts_at_i, prev_virtual_bead, box):
    num_points = len(ordered_bead_coords) - n_prev
    set_shape = list(ordered_bead_coords.shape)
    set_shape[0] = num_points
    coord_set = np.empty(tuple(set_shape))
    last_i = shifts_at_i[-1]
    if isclose(prev_virtual_bead[last_i], box[last_i], abs_tol=box[last_i] * 0.01):
        prev_virtual_bead[last_i] -= box[last_i]
    else:
        prev_virtual_bead[last_i] += box[last_i]
    coord_set[0] = prev_virtual_bead
    coord_set[1:] = ordered_bead_coords[n_prev+1:]
    return coord_set

def _compute_shifts_array(diff, box):
    shifts = np.zeros_like(diff)
    for i, b in enumerate(box):
        if b is None:            
            continue
        shifts_i = -b * np.rint(diff[:, i] / b)
        shifts[:, i] = shifts_i
    return shifts
        
def _sort_conflicting_shifts(shifts_at_n, shifts_at_i,
                             ordered_bead_coords, diff, shifts, box):

    r_cuts = np.zeros(shifts_at_n.shape)
    for j in range(len(shifts_at_n)):
        conflicting_indices = []
        nj = shifts_at_n[j]
        k = j + 1
        while k < len(shifts_at_n):
            nk = shifts_at_n[k]
            if nj != nk:
                break
            conflicting_indices.append(k)
            k += 1
        if len(conflicting_indices) == 0:
            ij = shifts_at_i[j]
            dx = diff[nj, ij] + shifts[nj, ij]
            x_nj_ij = ordered_bead_coords[nj, ij]
            if x_nj_ij + dx > box[ij]:
                r_cut = abs((box[ij] - x_nj_ij) / dx)
            else:                
                r_cut = abs(x_nj_ij / dx)
            r_cuts[j] = r_cut
            continue
        conflicting_indices.insert(0, j)
        boundary_cuts = {}
        for l in conflicting_indices:
            nl = shifts_at_n[l]
            il = shifts_at_i[l]
            dx = diff[nl, il] + shifts[nl, il]
            x_nl_il = ordered_bead_coords[nl, il]
            if x_nl_il + dx > box[il]:
                r_cut = abs((box[il] - x_nl_il) / dx)
            else:                
                r_cut = abs(x_nl_il / dx)
            boundary_cuts[l] = r_cut
        sorted_boundary_cut_pairs = sorted(boundary_cuts.items(), key=lambda x: x[1])

        conflicting_shifts_in_correct_order_n = []
        conflicting_shifts_in_correct_order_i = []
        r_cuts_in_correct_order = []
        # a cut pair is a Tuple of the index in the shifts_at array and the r_cut value
        for cut_pair in sorted_boundary_cut_pairs:
            conflicting_shifts_in_correct_order_n.append(shifts_at_n[cut_pair[0]])
            conflicting_shifts_in_correct_order_i.append(shifts_at_i[cut_pair[0]])
            r_cuts_in_correct_order.append(cut_pair[1])
        shifts_at_n[j:j+len(conflicting_indices)] = conflicting_shifts_in_correct_order_n
        shifts_at_i[j:j+len(conflicting_indices)] = conflicting_shifts_in_correct_order_i
        r_cuts[j:j+len(conflicting_indices)] = r_cuts_in_correct_order
    return shifts_at_n, shifts_at_i, r_cuts
