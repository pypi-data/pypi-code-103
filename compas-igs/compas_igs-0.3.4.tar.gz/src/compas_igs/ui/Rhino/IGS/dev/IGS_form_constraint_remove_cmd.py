from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino


__commandname__ = "IGS_form_constraint_remove"


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

    for vertex, attr in form.diagram.vertices(True):
        attr['line_constraint'] = None

    for vertex, attr in force.diagram.vertices(True):
        attr['line_constraint'] = None
        attr['is_fixed'] = False

    for edge, attr in form.diagram.edges(True):
        attr['target_vector'] = None
        attr['target_force'] = None

    for edge, attr in force.diagram.edges(True):
        attr['target_vector'] = None

    scene.update()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
