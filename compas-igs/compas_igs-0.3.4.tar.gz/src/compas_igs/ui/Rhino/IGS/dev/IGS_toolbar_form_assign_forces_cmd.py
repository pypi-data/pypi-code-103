from __future__ import print_function
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import IGS_form_select_ind_cmd
import IGS_form_assign_forces_cmd

__commandname__ = "IGS_toolbar_form_assign_forces"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    IGS_form_select_ind_cmd.RunCommand(True)
    IGS_form_assign_forces_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
