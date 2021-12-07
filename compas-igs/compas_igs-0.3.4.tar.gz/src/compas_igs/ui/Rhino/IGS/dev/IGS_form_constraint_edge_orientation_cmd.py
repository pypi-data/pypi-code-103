from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino


__commandname__ = "IGS_form_constraint_edge_orientation"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    objects = scene.find_by_name("Form")
    if objects:
        form = objects[0]
    else:
        compas_rhino.display_message('No Form diagram in the scene.')
        return

    objects = scene.find_by_name("Force")
    if objects:
        force = objects[0]
    else:
        compas_rhino.display_message('No Force diagram in the scene.')
        return

    edges = form.select_edges("Edges to constraint their current orientation.")
    if not edges:
        return

    for edge in edges:
        sp, ep = form.diagram.edge_coordinates(*edge)
        dx = ep[0] - sp[0]
        dy = ep[1] - sp[1]
        length = (dx**2 + dy**2)**0.5
        form.diagram.edge_attribute(edge, 'target_vector', [dx/length, dy/length])

    force.diagram.constraints_from_dual()

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
