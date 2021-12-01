import vtk

color = vtk.vtkNamedColors()

def draw_outline_with_lines(x_min, x_max, y_min, y_max, z_min, z_max):
    corner_points = vtk.vtkPoints()
    corner_points.InsertNextPoint([0., 0., 0.]) # 0
    corner_points.InsertNextPoint([0., 0., z_max]) # 1
    corner_points.InsertNextPoint([0., y_max, 0.]) # 2
    corner_points.InsertNextPoint([x_max, 0., 0.]) # 3
    corner_points.InsertNextPoint([x_max, 0., z_max]) # 4
    corner_points.InsertNextPoint([x_max, y_max, 0]) # 5
    corner_points.InsertNextPoint([0., y_max, z_max]) # 6
    corner_points.InsertNextPoint([x_max, y_max, z_max]) # 7

    line0 = vtk.vtkLine()
    line0.GetPointIds().SetId(0, 0)
    line0.GetPointIds().SetId(1, 1)

    line1 = vtk.vtkLine()
    line1.GetPointIds().SetId(0, 0)
    line1.GetPointIds().SetId(1, 2)

    line2 = vtk.vtkLine()
    line2.GetPointIds().SetId(0, 0)
    line2.GetPointIds().SetId(1, 3)

    line3 = vtk.vtkLine()
    line3.GetPointIds().SetId(0, 1)
    line3.GetPointIds().SetId(1, 4)

    line4 = vtk.vtkLine()
    line4.GetPointIds().SetId(0, 1)
    line4.GetPointIds().SetId(1, 6)

    line5 = vtk.vtkLine()
    line5.GetPointIds().SetId(0, 2)
    line5.GetPointIds().SetId(1, 5)
    
    line6 = vtk.vtkLine()
    line6.GetPointIds().SetId(0, 2)
    line6.GetPointIds().SetId(1, 6)

    line7 = vtk.vtkLine()
    line7.GetPointIds().SetId(0, 3)
    line7.GetPointIds().SetId(1, 4)

    line8 = vtk.vtkLine()
    line8.GetPointIds().SetId(0, 3)
    line8.GetPointIds().SetId(1, 5)

    line9 = vtk.vtkLine()
    line9.GetPointIds().SetId(0, 4)
    line9.GetPointIds().SetId(1, 7)

    line10 = vtk.vtkLine()
    line10.GetPointIds().SetId(0, 5)
    line10.GetPointIds().SetId(1, 7)

    line11 = vtk.vtkLine()
    line11.GetPointIds().SetId(0, 6)
    line11.GetPointIds().SetId(1, 7)

    lines = vtk.vtkCellArray()
    lines.InsertNextCell(line0)
    lines.InsertNextCell(line1)
    lines.InsertNextCell(line2)
    lines.InsertNextCell(line3)
    lines.InsertNextCell(line4)
    lines.InsertNextCell(line5)
    lines.InsertNextCell(line6)
    lines.InsertNextCell(line7)
    lines.InsertNextCell(line8)
    lines.InsertNextCell(line9)
    lines.InsertNextCell(line10)
    lines.InsertNextCell(line11)

    lines_poly_data = vtk.vtkPolyData()
    lines_poly_data.SetPoints(corner_points)
    lines_poly_data.SetLines(lines)

    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")

    for i in range(12):
        colors.InsertNextTypedTuple([0, 240, 0])

    lines_poly_data.GetCellData().SetScalars(colors)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(lines_poly_data)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def draw_outline_with_tubes(x_min: float, x_max: float,
                            y_min: float, y_max: float,
                            z_min: float, z_max: float,
                            r: float=10.0) -> vtk.vtkActor:    
    
    cube = vtk.vtkCubeSource()
    cube.SetBounds(x_min, x_max, y_min, y_max, z_min, z_max)

    edges = vtk.vtkExtractEdges()
    edges.SetInputConnection(cube.GetOutputPort())

    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(edges.GetOutputPort())
    tubes.SetRadius(r)
    tubes.SetNumberOfSides(6)
    tubes.UseDefaultNormalOn()
    tubes.SetDefaultNormal(.577, .577, .577)

    tube_mapper = vtk.vtkPolyDataMapper()
    tube_mapper.SetInputConnection(tubes.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(tube_mapper)
    actor.GetProperty().SetDiffuseColor(color.GetColor3d("khaki"))

    return actor

def draw_plane() -> vtk.vtkActor:
    plane_source = vtk.vtkPlaneSource()
    plane_source.SetNormal(0, 0, 1)
    plane_source.SetCenter(550, 550, 0)
    actor = _poly_data_to_actor(plane_source)
    actor.GetProperty().SetColor(color.GetColor3d("gray"))
    return actor
    

def _poly_data_to_actor(poly_data) -> vtk.vtkActor:
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(poly_data.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor
