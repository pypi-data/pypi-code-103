from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_igs.rhino import SettingsForm
from compas_igs.rhino import FormObject
from compas_igs.rhino import ForceObject


__commandname__ = "IGS_toolbar_display"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']
    if not scene:
        return

    # TODO: deal with undo redo
    SettingsForm.from_scene(scene, object_types=[FormObject, ForceObject], global_settings=['IGS'])

    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
