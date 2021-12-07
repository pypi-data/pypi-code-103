from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_form_move_nodes"


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

    form.settings['show.edgelabels'] = True
    form.settings['show.forcelabels'] = False
    force.settings['show.edgelabels'] = True

    scene.update()

    while True:
        vertices = form.select_vertices("Select vertices (Press ESC to exit)")
        if not vertices:
            break

        if form.move_vertices(vertices):
            if scene.settings['IGS']['autoupdate']:
                formdiagram = proxy.form_update_q_from_qind(form.diagram)
                form.diagram.data = formdiagram.data

                forcediagram = proxy.force_update_from_form(force.diagram, form.diagram)
                force.diagram.data = forcediagram.data

            scene.update()

    form.settings['show.edgelabels'] = False
    form.settings['show.forcelabels'] = True
    force.settings['show.edgelabels'] = False

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
