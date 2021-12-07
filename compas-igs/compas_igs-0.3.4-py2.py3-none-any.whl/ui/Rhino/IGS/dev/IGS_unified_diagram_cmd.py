from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from compas.geometry import centroid_points
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector
from compas.geometry import distance_point_point_xy

import scriptcontext as sc

import compas_rhino

from compas_igs.rhino import mesh_ud

try:
    import Rhino
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__commandname__ = "IGS_unified_diagram"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    # translation
    form_center = centroid_points(form.vertex_xyz.values())
    force_center = centroid_points(force.vertex_xyz.values())

    translation = subtract_vectors(force_center, form_center)

    # get scale
    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt("Enter scale for unified diagram (press ESC to exit)")
    go.AcceptNothing(True)

    scale_opt = Rhino.Input.Custom.OptionDouble(0.50, 0.01, 0.99)

    go.AddOptionDouble("Alpha", scale_opt)

    # get scale and rotation
    def _draw_ud(form, force, translation=translation, scale=0.5):
        compas_rhino.clear_layer(force.layer)

        # 2. compute unified diagram geometries
        geometry = mesh_ud(form, force, translation=translation, scale=scale)

        if not geometry:
            return

        faces, bars = geometry

        # 3. draw polygons
        for face, face_xyz in faces.items():
            count = len(face_xyz)
            filtered_xyz = []
            for i in range(-1, count - 1):
                if distance_point_point_xy(face_xyz[i], face_xyz[i + 1]) < 0.01:
                    continue
                filtered_xyz.append(face_xyz[i])
            if len(filtered_xyz) == 2:
                line = {'start': filtered_xyz[0], 'end': filtered_xyz[1], 'layer': force.layer}
                compas_rhino.draw_lines([line])
                continue
            compas_rhino.draw_mesh(filtered_xyz, [range(len(filtered_xyz))], layer=force.layer, name=str(face), redraw=False)

        # 4. draw bars
        bar_colors = {}
        for edge in force.diagram.edges_where_dual({'is_external': False}):
            if force.diagram.dual_edge_force(edge) > + force.settings['tol.forces']:
                bar_colors[edge] = force.settings['color.tension']
            elif force.diagram.dual_edge_force(edge) < - force.settings['tol.forces']:
                bar_colors[edge] = force.settings['color.compression']

        for bar, bar_xyz in bars.items():
            count = len(bar_xyz)
            filtered_xyz = []
            for i in range(-1, count - 1):
                if distance_point_point_xy(bar_xyz[i], bar_xyz[i + 1]) < 0.01:
                    continue
                filtered_xyz.append(bar_xyz[i])
            if len(filtered_xyz) == 2:
                line = {'start': filtered_xyz[0], 'end': filtered_xyz[1], 'layer': force.layer}
                compas_rhino.draw_lines([line])
                continue
            compas_rhino.draw_mesh(filtered_xyz, [range(len(filtered_xyz))], layer=force.layer, name=str(bar), color=bar_colors[bar], redraw=False)

    # unified diagram
    while True:
        rs.EnableRedraw(True)
        opt = go.Get()
        scale = scale_opt.CurrentValue
        if not opt:
            print("The scale for unified diagram needs to be between 0.01 and 0.99!")
        if opt == Rhino.Input.GetResult.Cancel:  # esc
            keep = rs.GetBoolean("Keep unified diagram? (press ESC to exit)", [("Copy", "No", "Yes")], (False))
            scene.clear_layers()
            if keep and keep[0]:
                _draw_ud(form, force, translation=scale_vector(translation, 2.5), scale=scale)
            scene.update()
            scene.save()
            return
        _draw_ud(form, force, translation=translation, scale=scale)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == '__main__':

    RunCommand(True)
