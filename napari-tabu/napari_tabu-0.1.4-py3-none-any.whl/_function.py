"""
This module is an example of a barebones function plugin for napari

It implements the ``napari_experimental_provide_function`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from enum import Enum
import numpy as np
from napari_plugin_engine import napari_hook_implementation
from napari_tools_menu import register_action

import napari

@napari_hook_implementation
def napari_experimental_provide_function():
    return [open_in_new_window]


# 1.  First example, a simple function that thresholds an image and creates a labels layer
def open_in_new_window(layer : napari.layers.Layer, napari_viewer:napari.Viewer):
    new_viewer = napari.Viewer()
    from ._dock_widget import SendBackWidget, _add_layer_to_viewer
    _add_layer_to_viewer(layer, new_viewer)

    # add back button to new viewer
    sbw = SendBackWidget(napari_viewer, new_viewer)

    new_viewer.window.add_dock_widget(sbw, area='right',
                                         name="Return")


@register_action(menu="Utilities > Open selected layers in new window")
def send_selected_to_new_window(viewer):
    new_viewer = napari.Viewer()
    from ._dock_widget import SendBackWidget, _add_layer_to_viewer
    for l in viewer.layers.selection:
        _add_layer_to_viewer(l, new_viewer)

    # add back button to new viewer
    sbw = SendBackWidget(viewer, new_viewer)

    new_viewer.window.add_dock_widget(sbw, area='right',
                                         name="Return")

