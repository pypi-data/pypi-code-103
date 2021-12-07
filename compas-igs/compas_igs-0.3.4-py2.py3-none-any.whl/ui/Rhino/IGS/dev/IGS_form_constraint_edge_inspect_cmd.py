from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino
find_object = sc.doc.Objects.Find


__commandname__ = "IGS_form_constraint_edge_inspect"


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

    form_settings = form.settings.copy()
    force_settings = force.settings.copy()
    form.settings['show.edges'] = True
    form.settings['show.forcelabels'] = False
    form.settings['show.edgelabels'] = False
    form.settings['show.forcepipes'] = False
    form.settings['show.constraints'] = True
    force.settings['show.edges'] = True
    force.settings['show.forcelabels'] = False
    force.settings['show.edgelabels'] = False
    force.settings['show.constraints'] = True
    scene.update()

    edge_index = form.diagram.edge_index()

    while True:
        edge_form = form.select_edge("Select an edge the Form Diagram to inspect constraints")

        index = edge_index[edge_form]
        edge_force = list(force.diagram.ordered_edges(form.diagram))[index]

        target_force = form.diagram.edge_attribute(edge_form, 'target_force')
        target_vector = form.diagram.edge_attribute(edge_form, 'target_vector')

        f = form.diagram.edge_attribute(edge_form, 'f')

        tol = form.settings['tol.forces']
        state = ''
        if not form.diagram.edge_attribute(edge_form, 'is_external'):
            if f > + tol:
                state = 'in tension'
            elif f < - tol:
                state = 'in compression'

        key2guid = {form.guid_edge[guid]: guid for guid in form.guid_edge}
        key2guid.update({(v, u): key2guid[(u, v)] for u, v in key2guid})
        find_object(key2guid[edge_form]).Select(True)
        key2guid = {force.guid_edge[guid]: guid for guid in force.guid_edge}
        key2guid.update({(v, u): key2guid[(u, v)] for u, v in key2guid})
        if abs(f) > tol:
            find_object(key2guid[edge_force]).Select(True)

        compas_rhino.display_message(
            "Edge Index: {0}\nTarget Force assigned (kN): {1}\nTarget Vector Assigned: {2}\nCurrent Force Magnitude: {3:.3g}kN {4}".format(index, target_force,
                                                                                                                                           target_vector, abs(f), state))

        answer = compas_rhino.rs.GetString("Continue selecting edges?", "No", ["Yes", "No"])
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
