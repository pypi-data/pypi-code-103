from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_server_restart"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    proxy = sc.sticky['IGS']['proxy']
    if not proxy:
        return

    proxy.stop_server()
    proxy.start_server()

    compas_rhino.display_message('IGS server restarted.')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
