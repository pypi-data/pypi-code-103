# -*- coding: utf-8 -*-

"""The graphical part of a Custom step"""

import seamm
import custom_step
import tkinter as tk


class TkCustom(seamm.TkNode):
    """
    The graphical part of a Custom step in a flowchart.

    Attributes
    ----------
    tk_flowchart : TkFlowchart = None
        The flowchart that we belong to.
    node : Node = None
        The corresponding node of the non-graphical flowchart
    namespace : str
        The namespace of the current step.
    sub_tk_flowchart : TkFlowchart
        A graphical Flowchart representing a subflowchart
    canvas: tkCanvas = None
        The Tk Canvas to draw on
    dialog : Dialog
        The Pmw dialog object
    x : int = None
        The x-coordinate of the center of the picture of the node
    y : int = None
        The y-coordinate of the center of the picture of the node
    w : int = 200
        The width in pixels of the picture of the node
    h : int = 50
        The height in pixels of the picture of the node
    self[widget] : dict
        A dictionary of tk widgets built using the information
        contained in Set Cell_parameters.py

    See Also
    --------
    Custom, TkCustom,
    CustomParameters,
    """

    def __init__(
        self,
        tk_flowchart=None,
        node=None,
        canvas=None,
        x=120,
        y=20,
        w=200,
        h=50
    ):
        """
        Initialize a graphical node.

        Parameters
        ----------
        tk_flowchart: Tk_Flowchart
            The graphical flowchart that we are in.
        node: Node
            The non-graphical node for this step.
        namespace: str
            The stevedore namespace for finding sub-nodes.
        canvas: Canvas
           The Tk canvas to draw on.
        x: float
            The x position of the nodes center on the canvas.
        y: float
            The y position of the nodes cetner on the canvas.
        w: float
            The nodes graphical width, in pixels.
        h: float
            The nodes graphical height, in pixels.

        Returns
        -------
        None
        """
        self.dialog = None

        super().__init__(
            tk_flowchart=tk_flowchart,
            node=node,
            canvas=canvas,
            x=x,
            y=y,
            w=w,
            h=h
        )

    def create_dialog(self):
        """Create the dialog!"""
        frame = super().create_dialog('Edit Custom Python')

        # Shortcut for parameters
        P = self.node.parameters

        # Put in the editor window
        textarea = custom_step.TextArea(frame)
        textarea.insert(1.0, P['script'])
        textarea.pack(expand=tk.YES, fill=tk.BOTH)
        self['textarea'] = textarea

    def right_click(self, event):
        """Probably need to add our dialog...
        """

        super().right_click(event)
        self.popup_menu.add_command(label="Edit..", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def handle_dialog(self, result):
        """Do the right thing when the dialog is closed.
        """
        # Shortcut for parameters
        P = self.node.parameters

        if result is None or result == 'Cancel':
            self.dialog.deactivate(result)
            self['textarea'].delete(1.0, 'end')
            self['textarea'].insert(1.0, P['script'].value)
        elif result == 'Help':
            self.help()
        elif result == 'OK':
            self.dialog.deactivate(result)
            # Capture the parameters from the widgets
            text = self['textarea'].get(1.0, tk.END).rstrip()
            P['script'].value = text + '\n'
        else:
            self.dialog.deactivate(result)
            raise RuntimeError(
                "Don't recognize dialog result '{}'".format(result)
            )
