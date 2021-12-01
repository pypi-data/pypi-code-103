import numpy as np
from mayavi.mlab import points3d, draw


class FilamentAnimator:

    def __init__(self):
        self.filament_data_reader = None
        self.points = None

    def show_at_t(self, t, figure=None):
        self._set_render_disable_status(True)
        data_slice_t, _ = self.filament_data_reader.get_coordinates_and_status_at_time_step(t)
        self._draw_data_slice(data_slice_t, figure)
        # self._set_render_disable_status(False)

    def _set_render_disable_status(self, state: bool):
        self.points.scene.disable_render = state

    def initialize_animation(self, time_step):
        data_slice, _ = self.filament_data_reader.get_coordinates_and_status_at_time_step(time_step)
        self._draw_data_slice(data_slice)

    def _draw_data_slice(self, data_slice, figure=None):
        if data_slice.shape[0] % 3 != 0:
            msg = "data_slice needs to be multiple of 3 (x-, y-, z-coordinates)."
            raise RuntimeError(msg)
        x, y, z = self._data_slice_to_coords(data_slice)
        if figure is not None:
            self.points = points3d(x, y, z,
                                   figure=figure,
                                   scale_mode="none", scale_factor=50.0, resolution=25)
            return
        
        if self.points is None:
            self.points = points3d(x, y, z,
                                   scale_mode="none", scale_factor=50.0, resolution=25)
        else:
            self.points.mlab_source.reset(x=x, y=y, z=z)

    def _data_slice_to_coords(self, data_slice: np.ndarray):
        size = data_slice.shape[0] // 3
        x = np.empty(size)
        y = np.empty(size)
        z = np.empty(size)        

        for i in range(size):
            x[i] = data_slice[3 * i]
            y[i] = data_slice[3 * i + 1]
            z[i] = data_slice[3 * i + 2]
        return x, y, z
