from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_toggle_bidirectional"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    answer = compas_rhino.rs.GetString("Bi-directional function at Form/Force Diagrams", "Cancel", ["On", "Off", "Cancel"])
    if answer == "On":
        scene.settings['IGS']['bi-directional'] = True
        compas_rhino.display_message("Bi-directional Form/Force: [On]")
    if answer == "Off":
        scene.settings['IGS']['bi-directional'] = False
        compas_rhino.display_message("Bi-directional Form/Force: [Off]")


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
