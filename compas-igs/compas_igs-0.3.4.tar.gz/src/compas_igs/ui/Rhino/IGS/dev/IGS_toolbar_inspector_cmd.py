from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import IGS_edges_table_cmd
import IGS_edge_information_cmd
import IGS_form_inspector_control_cmd
import IGS_form_constraint_edge_inspect_cmd
import IGS_form_constraint_vertex_inspect_cmd
import IGS_constraint_table_cmd


__commandname__ = "IGS_toolbar_inspector"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    options = ["EdgesTable", "EdgeInformation", "ForcePolygons", "EdgeConstraints", "VertexConstraints", "ConstraintsTable"]
    option = compas_rhino.rs.GetString("Select Inspection Mode:", strings=options)

    if not option:
        return

    if option == "EdgesTable":
        IGS_edges_table_cmd.RunCommand(True)

    elif option == "EdgeInformation":
        IGS_edge_information_cmd.RunCommand(True)

    elif option == "ForcePolygons":
        IGS_form_inspector_control_cmd.RunCommand(True)

    elif option == "EdgeConstraints":
        IGS_form_constraint_edge_inspect_cmd.RunCommand(True)

    elif option == "VertexConstraints":
        IGS_form_constraint_vertex_inspect_cmd.RunCommand(True)

    elif option == "ConstraintsTable":
        IGS_constraint_table_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
