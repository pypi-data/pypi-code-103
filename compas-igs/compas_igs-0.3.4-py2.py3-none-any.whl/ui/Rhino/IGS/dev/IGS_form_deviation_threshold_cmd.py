from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_form_deviation_threshold"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    max_dev = compas_rhino.rs.GetReal(message="Assign threshold for maximum angle deviation", number=scene.settings['IGS']['max_deviation'])
    if not max_dev:
        return

    scene.settings['IGS']['max_deviation'] = max_dev


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
