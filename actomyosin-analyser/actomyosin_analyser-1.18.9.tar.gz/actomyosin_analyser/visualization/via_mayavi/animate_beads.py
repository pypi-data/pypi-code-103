from math import isclose
import numpy as np
from mayavi.mlab import points3d, plot3d, gcf
from .mayavi_animator import MayaviAnimator
from ...model.bead import (STATE_FILAMENT_START,
                           STATE_FILAMENT_INTERIOR,
                           STATE_FILAMENT_END)


class BeadAnimator(MayaviAnimator):

    def __init__(self):
        self.data_reader = None
        self.beads = None
        self.tubes = []
        self.minimum_image_box = None
        self.bead_scale_factor = 20.0

    def show_at_t(self, t):
        if self.beads is not None:
            self.beads.scene.disable_render = True
        coordinates, status = self.data_reader.get_system_state_at_time_step(t)
        self._draw_data_slice(coordinates, status)
        if self.beads is not None:
            self.beads.scene.disable_render = False

    def _draw_data_slice(self, coordinates, bead_links):
        if coordinates.shape[0] % 3 != 0:
            msg = "coordinates' length needs to be multiple of 3 (x-, y-, z-coordinates)."
            raise RuntimeError(msg)
        x, y, z = self._data_slice_to_coords(coordinates)

        if self.minimum_image_box is not None:
            x -= self.minimum_image_box[0] * np.floor(x / self.minimum_image_box[0])
            y -= self.minimum_image_box[1] * np.floor(y / self.minimum_image_box[1])
            z -= self.minimum_image_box[2] * np.floor(z / self.minimum_image_box[2])
        
        s = bead_links.states
        if self.beads is None:
            size_array = self._bead_states_to_size_array(s)
            color_lookup_table = self._create_color_lookup_table()
            self.beads = points3d(x, y, z, size_array,
                                  scale_mode="scalar", scale_factor=self.bead_scale_factor,
                                  resolution=25)
            self.beads.module_manager.scalar_lut_manager.lut.table = color_lookup_table
            # ======================================================================================
            # connect filament beads with tubes
            # --------------------------------------------------------------------------------------
            for f in bead_links.filaments:                
                current = f.start
                indices = []
                while current != f.end:
                    indices.append(current)
                    current = bead_links.linked_beads[current].next
                indices.append(current)
                tube_coord_sets = self._get_minimum_image_tube_coords(
                    x[indices], y[indices], z[indices])
                for tube_set in tube_coord_sets:
                    x_tube = tube_set[0]
                    y_tube = tube_set[1]
                    z_tube = tube_set[2]
                    self.tubes.append(plot3d(x_tube, y_tube, z_tube,
                                             np.zeros_like(x_tube),
                                             color=(0.1725, 0.6274, 0.1725),
                                             tube_radius=2.0))
            # --------------------------------------------------------------------------------------
            return
        # ==========================================================================================
        # in case of animation, remove all tubes
        # ------------------------------------------------------------------------------------------
        for tubes in self.tubes:
            tubes.remove()
        self.tubes = []
        # ------------------------------------------------------------------------------------------
                
        self.beads.mlab_source.set(x=x, y=y, z=z)

    def initialize_animation(self, time_step):
        data_slice, status = self.data_reader.get_system_state_at_time_step(time_step)
        self._draw_data_slice(data_slice, status)
    
    def _get_minimum_image_tube_coords(self, x, y, z):
        """
        To connect beads at x, y, z with tubes, this method calculates
        where virtual beads need to be placed at the planes of periodic boundaries.
        """
        tube_coord_sets = []
        x_tube = [x[0]]
        y_tube = [y[0]]
        z_tube = [z[0]]
        n_virtual_beads = 0
        for i in range(1, x.shape[0]):
            dx = x[i] - x[i - 1]
            dy = y[i] - y[i - 1]
            dz = z[i] - z[i - 1]
            x_shift = self.minimum_image_box[0] * round(dx / self.minimum_image_box[0])
            y_shift = self.minimum_image_box[1] * round(dy / self.minimum_image_box[1])
            z_shift = self.minimum_image_box[2] * round(dz / self.minimum_image_box[2])
            boundary_cuts = {}          
            if x_shift != 0:            
                dx -= x_shift
                if (x[i - 1] + dx > self.minimum_image_box[0]):
                    r_cut_x = abs((self.minimum_image_box[0] - x[i - 1]) / dx)
                else:
                    r_cut_x = abs(x[i - 1] / dx)
                boundary_cuts['x'] = r_cut_x
            if y_shift != 0:
                dy -= y_shift
                if (y[i - 1] + dy > self.minimum_image_box[1]):
                    r_cut_y = abs((self.minimum_image_box[1] - y[i - 1]) / dy)
                else:
                    r_cut_y = abs(y[i - 1] / dy)
                boundary_cuts['y'] = r_cut_y
            if z_shift != 0:
                dz -= z_shift
                if (z[i - 1] + dz > self.minimum_image_box[2]):
                    r_cut_z = abs((self.minimum_image_box[2] - z[i - 1]) / dz)
                else:
                    r_cut_z = abs(z[i - 1] / dz)
                boundary_cuts['z'] = r_cut_z
            sorted_boundary_cut_pairs = sorted(boundary_cuts.items(), key=lambda x: x[1])
            prev_x = x[i - 1]
            prev_y = y[i - 1]
            prev_z = z[i - 1]
            prev_r = 0
            for pair in sorted_boundary_cut_pairs:                
                key, r = pair                
                virtual_x = prev_x + (r - prev_r) * dx
                virtual_y = prev_y + (r - prev_r) * dy
                virtual_z = prev_z + (r - prev_r) * dz
                n_virtual_beads += 1
                x_tube.append(virtual_x)
                y_tube.append(virtual_y)
                z_tube.append(virtual_z)                
                tube_coord_sets.append((np.array(x_tube), np.array(y_tube), np.array(z_tube)))

                if key == 'x':
                    if isclose(virtual_x, 0.0, abs_tol=self.minimum_image_box[0] * 0.01):
                        virtual_x += self.minimum_image_box[0]
                    else:
                        virtual_x -= self.minimum_image_box[0]
                elif key == 'y':
                    if isclose(virtual_y, 0.0, abs_tol=self.minimum_image_box[1] * 0.01):
                        virtual_y += self.minimum_image_box[1]
                    else:
                        virtual_y -= self.minimum_image_box[1]
                elif key == 'z':
                    if isclose(virtual_z, 0.0, abs_tol=self.minimum_image_box[2] * 0.01):
                        virtual_z += self.minimum_image_box[2]
                    else:
                        virtual_z -= self.minimum_image_box[2]
                x_tube = [virtual_x]
                y_tube = [virtual_y]
                z_tube = [virtual_z]
                prev_x = virtual_x
                prev_y = virtual_y
                prev_z = virtual_z
                prev_r = r
            x_tube.append(x[i])
            y_tube.append(y[i])
            z_tube.append(z[i])
        tube_coord_sets.append((np.array(x_tube), np.array(y_tube), np.array(z_tube)))

        return tube_coord_sets

    def _bead_states_to_size_array(self, states):
        size_array = np.zeros_like(states)
        size_array[states == STATE_FILAMENT_START] = 1.25
        size_array[states == STATE_FILAMENT_END] = 1.25
        size_array[states == STATE_FILAMENT_INTERIOR] = 1.0
        return size_array

    def _create_color_lookup_table(self):
        lut = np.zeros((255, 4), dtype=np.int8)
        lut[254, :] = [31, 119, 180, 255]
        lut[0, :] = [0, 0, 0, 255]
        lut[1: 254, 0] = np.ones_like(lut[1: 254, 0]) * 255
        lut[1: 254, 1] = np.ones_like(lut[1: 254, 1]) * 127
        lut[1: 254, 2] = np.ones_like(lut[1: 254, 2]) * 14
        lut[1: 254, 3] = np.ones_like(lut[1: 254, 3]) * 255
        return lut
