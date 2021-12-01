import vtk


class VTKFilamentRepresentation:

    def __init__(self):
        self.sphere_mapper = []
        self.sphere_actors = []
        self.sphere_sources = []
        self.vtk_renderer = None

    def set_coordinates(self, data_slice):
        if data_slice.shape[0] % 3 != 0:
            msg = "data_slice needs to be multiple of 3 (x-, y-, z-coordinates)."
            raise RuntimeError(msg)
        for i in range(0, data_slice.shape[0] // 3):            
            coords = tuple(data_slice[i * 3: i * 3 + 3])
            if len(self.sphere_actors) <= i:
                new_sphere = vtk.vtkSphereSource()
                new_sphere.SetCenter(*coords)
                new_sphere.SetRadius(20)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(new_sphere.GetOutputPort())
                new_actor = vtk.vtkActor()
                new_actor.SetMapper(mapper)
                self.sphere_actors.append(new_actor)
                self.sphere_mapper.append(mapper)
                self.sphere_sources.append(new_sphere)
                self.vtk_renderer.AddActor(new_actor)
            else:                
                self.sphere_sources[i].SetCenter(*coords)
