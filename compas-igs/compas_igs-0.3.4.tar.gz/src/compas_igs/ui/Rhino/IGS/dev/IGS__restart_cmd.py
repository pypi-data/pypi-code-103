from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
import scriptcontext as sc


__commandname__ = "IGS__restart"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']
    if not scene:
        return

    proxy = sc.sticky['IGS']['proxy']
    if not proxy:
        return

    scene.purge()
    proxy.stop_server()
    proxy.start_server()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
