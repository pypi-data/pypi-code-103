from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino


__commandname__ = "IGS_form_constraint_edge_force"


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
    if not objects:
        compas_rhino.display_message('No Force diagram in the scene.')
        return

    edges = form.select_edges("Edges to assign target force")
    if not edges:
        return

    forcemag = compas_rhino.rs.GetReal("Value of the target force (KN)", 1.0)
    if not forcemag and forcemag != 0.0:
        return

    for edge in edges:
        form.diagram.edge_attribute(edge, 'target_force', abs(forcemag))

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
