# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider


def get_coordinates_slice_as_plottable_arrays(coordinates_slice):
    if len(coordinates_slice) % 3 != 0:
        raise RuntimeError("number of items in array not dividable by 3!")
    n_points = int(len(coordinates_slice) / 3)
    x = []
    y = []
    z = []
    for i in range(0, n_points * 3, 3):
        x.append(coordinates_slice[i])
        y.append(coordinates_slice[i + 1])
        z.append(coordinates_slice[i + 2])
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)    
    return x, y, z


def plot_segment(ax, slice_of_filament_array: np.ndarray):
    x, y, z = get_coordinates_slice_as_plottable_arrays(slice_of_filament_array)
    line = ax.plot(x, y, z, marker="o")
    return line[0]


class PlotDings:

    def __init__(self, time_steps: int):
        self.time_steps = time_steps
        self.f = plt.figure()
        self.ax = self.f.gca(projection='3d')
        self.f.subplots_adjust(left=0.03, bottom=0.2)

        self.actin_data_reader = None
        self.segment_lines = []

        axcolor = 'lightgoldenrodyellow'
        self.ax_time = self.f.add_axes([0.25, 0.1, 0.65, 0.03],
                                       facecolor=axcolor)
        self.slider_time = Slider(self.ax_time, 
                                  r"time [$\Delta t$]",
                                  0, time_steps - 1, valinit=0,
                                  valfmt='%0.0f')
        self.slider_time.on_changed(self._update)

    def _update(self, val):        
        i = 0
        t = int(self.slider_time.val)
        data_slice = self.actin_data_reader.get_coordinates_at_time_step(t)
        for i in range(len(self.segment_lines)):
            l = self.segment_lines[i]
            j = i * 6
            new_coordinates = get_coordinates_slice_as_plottable_arrays(data_slice[j: j + 6])
            # l._offsets3d = new_coordinates
            l.set_data(new_coordinates[0], new_coordinates[1])
            l.set_3d_properties(new_coordinates[2])
        self.f.canvas.draw_idle()

    def _initialize_plot(self):
        data_slice = self.actin_data_reader.get_coordinates_at_time_step(0)
        for i in range(0, data_slice.shape[0], 6):
            l = plot_segment(self.ax, data_slice[i: i + 6])
            self.segment_lines.append(l)

    def show(self):
        self._initialize_plot()
        self.f.show()
