from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas.geometry import subtract_vectors
from compas.geometry import add_vectors


__commandname__ = "IGS_force_scale"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    options = ["Factor", "3Points"]
    option = compas_rhino.rs.GetString("Scale ForceDiagram:", strings=options)

    if not option:
        return

    if option == "Factor":
        scale_factor = compas_rhino.rs.GetReal("Scale factor", force.scale)
        force.scale = scale_factor

    elif option == "3Points":
        loc0 = force.settings['_location_0deg']
        loc90 = force.settings['_location_90deg']

        force.scale_from_3_points(message="Select the base node of the Force Diagram for the scaling operation.")

        anchor_xyz = force.location.copy()
        if force.settings['rotate.90deg']:
            force.settings['_location_90deg'] = anchor_xyz
            anchor_vector = subtract_vectors(anchor_xyz, loc90)
            anchor_rotated = [anchor_vector[1], -anchor_vector[0], 0.0]  # rotate 90
            force.settings['_location_0deg'] = add_vectors(loc0, anchor_rotated)
        else:
            force.settings['_location_0deg'] = anchor_xyz
            anchor_vector = subtract_vectors(anchor_xyz, loc0)
            anchor_rotated = [-anchor_vector[1], anchor_vector[0], 0.0]  # rotate -90
            force.settings['_location_90deg'] = add_vectors(loc90, anchor_rotated)

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
