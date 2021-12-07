from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import IGS_force_inspector_on_cmd
import IGS_force_inspector_off_cmd

__commandname__ = "IGS_force_inspector_control"


def RunCommand(is_interactive):
    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return

    answer = compas_rhino.rs.GetString("Force Dual Inspector", "Cancel", ["On", "Off", "Cancel"])
    if answer == "On":
        IGS_force_inspector_on_cmd.RunCommand(True)
    if answer == "Off":
        IGS_force_inspector_off_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
