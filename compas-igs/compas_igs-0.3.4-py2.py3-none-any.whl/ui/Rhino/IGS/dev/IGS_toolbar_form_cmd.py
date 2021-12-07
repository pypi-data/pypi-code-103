from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import IGS_form_from_obj_cmd
import IGS_form_from_lines_cmd
import IGS_form_from_layer_cmd


__commandname__ = "IGS_toolbar_form"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    options = ["FromObj", "FromLines", "FromLayer"]
    option = compas_rhino.rs.GetString("Create Form:", strings=options)

    if not option:
        return

    if option == "FromObj":
        IGS_form_from_obj_cmd.RunCommand(True)

    elif option == "FromLines":
        IGS_form_from_lines_cmd.RunCommand(True)

    elif option == "FromLayer":
        IGS_form_from_layer_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
