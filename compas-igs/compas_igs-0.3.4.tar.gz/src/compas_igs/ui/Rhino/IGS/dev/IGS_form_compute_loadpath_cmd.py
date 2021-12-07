from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_form_compute_loadpath"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    proxy = sc.sticky['IGS']['proxy']
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

    proxy.package = 'compas_ags.ags.loadpath'

    lp = proxy.compute_loadpath(form.diagram, force.diagram)
    compas_rhino.display_message('The total load-path of the structure is {} kNm.'.format(round(lp, 2)))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
