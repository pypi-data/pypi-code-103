from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import IGS_form_constraint_edge_force_cmd
import IGS_form_constraint_edge_orientation_cmd

__commandname__ = "IGS_toolbar_form_constraints_edge"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    options = ["ForceMagnitude", "Orientation"]
    option = compas_rhino.rs.GetString("Constraint Edge:", strings=options)

    if not option:
        return

    if option == "ForceMagnitude":
        IGS_form_constraint_edge_force_cmd.RunCommand(True)

    elif option == "Orientation":
        IGS_form_constraint_edge_orientation_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
