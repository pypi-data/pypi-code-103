from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino

from compas_igs.rhino import AttributesForm


__commandname__ = "IGS_constraint_table"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    form = scene.find_by_name("Form")[0]

    objects = scene.find_by_name("Force")
    if objects:
        force = objects[0]
    else:
        force = None

    # Turn on edge labels
    form_settings = form.settings.copy()
    force_settings = force.settings.copy()
    form.settings["show.edgelabels"] = True
    force.settings["show.edgelabels"] = True
    form.settings["show.vertexlabels"] = True
    force.settings["show.vertexlabels"] = True
    form.settings["show.constraints"] = False
    force.settings["show.constraints"] = False
    force.settings["show.forcepipes"] = False
    scene.update()

    AttributesForm.from_sceneNode(form, dual=force, tabs=['Constraints'])

    # Revert to original setting
    form.settings = form_settings
    force.settings = force_settings

    scene.update()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
