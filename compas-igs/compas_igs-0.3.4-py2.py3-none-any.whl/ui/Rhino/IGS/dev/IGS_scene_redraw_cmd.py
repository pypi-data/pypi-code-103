from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "IGS_scene_redraw"


def RunCommand(is_interactive):

    sc.doc.EndUndoRecord(sc.doc.CurrentUndoRecordSerialNumber)

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']
    if not scene:
        return

    scene.clear_layers()
    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
