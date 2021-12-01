import vtk


class BeadAnimator:

    def __init__(self):
        self.data_reader = None
        self.bead_sources = []
        self.vtk_renderer = None
        self.bead_radius = None
        self.minimum_image = False

    def show_at_t(self, t):
        coordinates, status = self.data_reader\
                                  .get_system_state_at_time_step(t, self.minimum_image)
        self._draw_data_slice(coordinates, status)

    def _draw_data_slice(self, coordinates, status):
        if coordinates.shape[0] % 3 != 0:
            msg = "data_slice needs to be multiple of 3 (x-, y-, z-coordinates)."
            raise RuntimeError(msg)

        if len(self.bead_sources) == 0:
            for i in range(0, coordinates.shape[0] // 3):            
                coords = tuple(coordinates[i * 3: i * 3 + 3])
                new_sphere = vtk.vtkSphereSource()
                new_sphere.SetCenter(*coords)
                new_sphere.SetRadius(self.bead_radius)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(new_sphere.GetOutputPort())
                new_actor = vtk.vtkActor()
                new_actor.SetMapper(mapper)
                self.bead_sources.append(new_sphere)
                self.vtk_renderer.AddActor(new_actor)
            return
        for i in range(0, coordinates.shape[0] // 3):
            coords = tuple(coordinates[i * 3: i * 3 + 3])
            self.bead_sources[i].SetCenter(*coords)
