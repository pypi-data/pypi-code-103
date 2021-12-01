from .vtk_filament_representation import VTKFilamentRepresentation


class FilamentAnimator:

    def __init__(self):
        self.data_reader = None
        self.filaments = []
        self.vtk_renderer = None

    def show_at_t(self, t):
        data_slice, filament_length_array = self.data_reader\
                                                .get_coordinates_at_time_step(t)
        self._draw_data_slice(data_slice, filament_length_array)

    def _draw_data_slice(self, data_slice, filament_length_array):
        if data_slice.shape[0] % 3 != 0:
            msg = "data_slice needs to be multiple of 3 (x-, y-, z-coordinates)."
            raise RuntimeError(msg)
        if len(filament_length_array) > len(self.filaments):
            for i in range(len(self.filaments), len(filament_length_array)):
                new_filament = VTKFilamentRepresentation()
                new_filament.vtk_renderer = self.vtk_renderer
                self.filaments.append(new_filament)

        current_index = 0
        i = 0
        for f in filament_length_array:
            self.filaments[current_index].set_coordinates(data_slice[i: i + 3 * f])
            i += 3 * f
            current_index += 1
