from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_force_select_fixed"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    force = objects[0]

    force.diagram.vertices_attribute('is_fixed', False)
    scene.update()

    vertices = force.select_vertices("Fix selected vertices (unfix all others)")
    if not vertices:
        return

    force.diagram.vertices_attribute('is_fixed', True, keys=vertices)
    scene.update()

    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
