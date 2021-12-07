from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_igs.utilities import check_equilibrium
from compas_igs.utilities import compute_angle_deviations


__commandname__ = "IGS_force_move_nodes"


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

    proxy.package = 'compas_ags.ags.graphstatics'

    formdiagram, forcediagram = proxy.form_update_from_force(form.diagram, force.diagram)
    form.diagram.data = formdiagram.data
    force.diagram.data = forcediagram.data

    threshold = scene.settings['IGS']['max_deviation']
    compute_angle_deviations(form.diagram, force.diagram, tol_force=threshold)
    if not check_equilibrium(form.diagram, force.diagram, tol_angle=threshold, tol_force=threshold):
        compas_rhino.display_message('Error: Invalid movement on force diagram nodes or insuficient constraints in the form diagram.')
        max_dev = max(form.diagram.edges_attribute('a'))
        compas_rhino.display_message('Diagrams are not parallel!\nMax. angle deviation: {0:.2g} deg\nThreshold assumed: {1:.2g} deg.'.format(max_dev, threshold))

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
