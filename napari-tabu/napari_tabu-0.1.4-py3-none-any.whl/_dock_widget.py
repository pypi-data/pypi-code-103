"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
# from napari_plugin_engine import napari_hook_implementation
import warnings

from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from magicgui import magic_factory
import napari
import numpy as np

class SendBackWidget(QWidget):
    def __init__(self, napari_viewer, napari_child_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.child_viewer = napari_child_viewer

        btn = QPushButton("Send current layer back to main napari")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        for l in self.child_viewer.layers.selection:
            _add_layer_to_viewer(l, self.viewer)

def _add_layer_to_viewer(layer: napari.layers.Layer, viewer:napari.Viewer):
    if isinstance(layer, napari.layers.Labels):
        new_layer = viewer.add_labels(
            layer.data,
            opacity=layer.opacity,
            blending=layer.blending,
        )
        new_layer.contour = layer.contour
        #new_layer.brush_size=layer.brush_size,
        #new_layer.color_mode=layer.color_mode,
        #new_layer.n_edit_dims=layer.n_edit_dims,
        #new_layer.contigous=layer.contigous,
    elif isinstance(layer, napari.layers.Image):
        viewer.add_image(
            layer.data,
            name=layer.name,
            opacity=layer.opacity,
            gamma=layer.gamma,
            contrast_limits=layer.contrast_limits,
            colormap=layer.colormap,
            blending=layer.blending,
            interpolation=layer.interpolation,
        )
    elif isinstance(layer, napari.layers.Points):
        viewer.add_points(
            layer.data,
            opacity=layer.opacity,
            #point_size=layer.point_size,
            blending=layer.blending,
            symbol=layer.symbol,
            face_color=layer.face_color,
            edge_color=layer.edge_color,
        )

    elif isinstance(layer, napari.layers.Shapes):
        viewer.add_shapes(
            layer.data,
            shape_type=layer.shape_type,
            opacity=layer.opacity,
            edge_width=layer.edge_width,
            blending=layer.blending,
            face_color=layer.face_color,
            edge_color=layer.edge_color,
        )
    else:
        warnings.warn("Not supported layer type: " + str(layer.__class__))

#@napari_hook_implementation
#def napari_experimental_provide_dock_widget():
#    # you can return either a single widget, or a sequence of widgets
#    return [ExampleQWidget, example_magic_widget]
