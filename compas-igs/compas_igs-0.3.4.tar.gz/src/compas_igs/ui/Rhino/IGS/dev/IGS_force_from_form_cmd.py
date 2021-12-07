from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import math
import compas_rhino
from compas_ags.diagrams import ForceDiagram

from compas_igs.utilities import compute_force_drawinglocation
from compas_igs.utilities import compute_force_drawingscale
from compas_igs.utilities import compute_form_forcescale


__commandname__ = "IGS_force_from_form"


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

    proxy.package = 'compas_ags.ags.graphstatics'

    edges = list(form.diagram.edges_where({'is_ind': True}))

    if not len(edges):
        compas_rhino.display_message(
            "You have not yet assigned force values to the form diagram. Please assign forces first.")
        return

    dof = proxy.form_count_dof(form.diagram)
    if dof[0] != len(edges):
        compas_rhino.display_message(
            "You have not assigned the correct number of force values. Please, check the degrees of freedom of the form diagram and update the assigned forces accordingly.")
        return

    # this should become part of the scene
    for guid in list(scene.objects.keys()):
        obj = scene.objects[guid]
        if obj.name == 'Force':
            compas_rhino.rs.EnableRedraw(False)
            try:
                obj.clear()
                del scene.objects[guid]
            except Exception:
                pass
            compas_rhino.rs.EnableRedraw(True)
            compas_rhino.rs.Redraw()

    forcediagram = ForceDiagram.from_formdiagram(form.diagram)
    force_id = scene.add(forcediagram, name="Force", layer="IGS::ForceDiagram")
    force = scene.find(force_id)

    formdiagram = proxy.form_update_q_from_qind(form.diagram)
    form.diagram.data = formdiagram.data

    forcediagram = proxy.force_update_from_form(force.diagram, form.diagram)
    force.diagram.data = forcediagram.data

    force.scale = compute_force_drawingscale(form, force)

    # compute and store the ideal location for the diagram at 0 and 90 degrees
    force.rotation = [0, 0, +math.pi/2]
    location_90deg = compute_force_drawinglocation(form, force).copy()

    force.rotation = [0, 0, 0]
    location_0deg = compute_force_drawinglocation(form, force).copy()

    force.settings['_location_0deg'] = location_0deg
    force.settings['_location_90deg'] = location_90deg

    form.settings['scale.forces'] = compute_form_forcescale(form)

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
