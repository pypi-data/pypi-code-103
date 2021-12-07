from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino
find_object = sc.doc.Objects.Find


__commandname__ = "IGS_form_constraint_edge__inspect"


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

    form_settings = form.settings.copy()
    force_settings = force.settings.copy()
    form.settings['show.edges'] = True
    form.settings['show.forcelabels'] = False
    form.settings['show.edgelabels'] = False
    form.settings['show.forcepipes'] = False
    force.settings['show.constraints'] = True
    force.settings['show.edges'] = True
    force.settings['show.forcelabels'] = False
    force.settings['show.edgelabels'] = False
    force.settings['show.constraints'] = True
    scene.update()

    pointfilter = compas_rhino.rs.filter.point

    form_vertex_index = form.diagram.vertex_index()
    force_vertex_index = force.diagram.vertex_index()

    while True:
        guid = compas_rhino.rs.GetObject(message="Select a vertex in the form or in the force diagram to check constraints",
                                         preselect=True, select=True, filter=pointfilter)

        if not guid:
            break
        elif guid not in form.guid_vertex and guid not in force.guid_vertex:
            compas_rhino.display_message("Vertex does not belog to form or force diagram.")
            break

        if guid in form.guid_vertex:
            key_form = form.guid_vertex[guid]
            constraint = form.diagram.vertex_attribute(key_form, 'line_constraint')
            index = form_vertex_index[key_form]
        if guid in force.guid_vertex:
            key_force = force.guid_vertex[guid]
            constraint = force.diagram.vertex_attribute(key_force, 'line_constraint')
            index = force_vertex_index[key_force]

        if constraint:
            sp = constraint.start
            ep = constraint.end
            constraint = [sp, ep]

        compas_rhino.display_message(
            "Vertex Index: {0}\nLine constraint: {1}".format(index, constraint))

        answer = compas_rhino.rs.GetString("Continue selecting vertices?", "No", ["Yes", "No"])
        if not answer:
            break
        if answer == "No":
            break
        if answer == 'Yes':
            scene.update()

    form.settings = form_settings
    force.settings = force_settings

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
