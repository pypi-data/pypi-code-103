from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import Rhino
import compas_rhino
from compas.geometry import Line


__commandname__ = "IGS_form_constraint_vertex"


def RunCommand(is_interactive):

    if 'IGS' not in sc.sticky:
        compas_rhino.display_message('IGS has not been initialised yet.')
        return

    scene = sc.sticky['IGS']['scene']

    objects = scene.find_by_name("Form")
    if objects:
        form = objects[0]
    else:
        compas_rhino.display_message('No Form diagram in the scene.')
        return

    objects = scene.find_by_name("Force")
    if objects:
        force = objects[0]
    else:
        compas_rhino.display_message('No Force diagram in the scene.')
        return

    def OnDynamicDraw(sender, e):
        end = e.CurrentPoint
        e.Display.DrawDottedLine(start, end, color)

    vertex = form.select_vertex("Select the vertex to constraint in the form diagram")
    if not vertex:
        return

    start = compas_rhino.rs.GetPoint("Start of line constraint")
    if not start:
        return

    color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
    gp = Rhino.Input.Custom.GetPoint()
    gp.DynamicDraw += OnDynamicDraw
    gp.SetCommandPrompt('End of line constraint')
    gp.Get()

    if gp.CommandResult() != Rhino.Commands.Result.Success:
        return

    end = list(gp.Point())

    line = Line(start, end)
    form.diagram.vertex_attribute(vertex, 'line_constraint', line)
    force.diagram.constraints_from_dual()

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
