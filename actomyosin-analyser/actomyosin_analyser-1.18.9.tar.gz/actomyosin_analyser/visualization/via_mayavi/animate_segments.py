import numpy as np
from mayavi.mlab import points3d, plot3d
from .mayavi_animator import MayaviAnimator


class SegmentAnimator(MayaviAnimator):

    def __init__(self):
        self.data_reader = None
        self.points_begin = None
        self.points_end = None
        self.tubes = []

    def show_at_t(self, t, mlab_fig=None):
        self._set_render_disable_status(True)
        data_slice_t = self.data_reader.get_coordinates_at_time_step(t)
        self._draw_data_slice(data_slice_t)
        self._set_render_disable_status(False)

    def _set_render_disable_status(self, state: bool):
        self.points_begin.scene.disable_render = state
        self.points_end.scene.disable_render = state
        for tube in self.tubes:
            tube.scene.disable_render = state

    def initialize_animation(self, time_step):
        data_slice = self.data_reader.get_coordinates_at_time_step(time_step)
        self._draw_data_slice(data_slice)

    def _draw_data_slice(self, data_slice):        
        if data_slice.shape[0] % 3 != 0:
            msg = "data_slice needs to be multiple of 3 (x-, y-, z-coordinates)."
            raise RuntimeError(msg)
        if data_slice.shape[0] % 2 != 0:
            msg = "data_slice needs to have even number of values (2 points per segment)"
            raise RuntimeError(msg)
        x, y, z = self._data_slice_to_coords(data_slice)

        ind_even = np.arange(0, x.shape[0], 2)
        ind_odd = np.arange(1, x.shape[0], 2)

        if self.points_begin is None:
            self.points_begin = points3d(x[ind_even], y[ind_even], z[ind_even], color=(1.0, 0., 0.),
                                         scale_mode="none", scale_factor=20.0, resolution=25)
        else:
            self.points_begin.mlab_source.set(x=x[ind_even], y=y[ind_even], z=z[ind_even])
        if self.points_end is None:
            self.points_end = points3d(x[ind_odd], y[ind_odd], z[ind_odd], color=(0.0, 1., 0.),
                                       scale_mode="none", scale_factor=20.0, resolution=25)
        else:
            self.points_end.mlab_source.set(x=x[ind_odd], y=y[ind_odd], z=z[ind_odd])

        if len(self.tubes) == 0:
            for i in range(0, x.shape[0], 2):
                current_x = np.array([x[i], x[i + 1]])
                current_y = np.array([y[i], y[i + 1]])
                current_z = np.array([z[i], z[i + 1]])
                self.tubes.append(plot3d(current_x, current_y, current_z,
                                         tube_radius=10., tube_sides=15))
        else:
            for i in range(0, x.shape[0], 2):
                tube = self.tubes[i // 2]
                current_x = np.array([x[i], x[i + 1]])
                current_y = np.array([y[i], y[i + 1]])
                current_z = np.array([z[i], z[i + 1]])
                tube.mlab_source.set(x=current_x, y=current_y, z=current_z)
