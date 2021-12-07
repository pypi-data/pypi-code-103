from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import IGS_form_constraint_vertex_cmd
import IGS_force_constraint_vertex_cmd

__commandname__ = "IGS_toolbar_form_constraints_vertex"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    options = ["FormDiagram", "ForceDiagram"]
    option = compas_rhino.rs.GetString("Constraint Vertex in the:", strings=options)

    if not option:
        return

    if option == "FormDiagram":
        IGS_form_constraint_vertex_cmd.RunCommand(True)

    elif option == "ForceDiagram":
        IGS_force_constraint_vertex_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
