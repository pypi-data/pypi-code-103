import numpy as np
import napari

from .utils import *

# Shift, Control, Alt, Meta, Up, Down, Left, Right, PageUp, PageDown, Insert, 
# Delete, Home, End, Escape, Backspace, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10,
# F11, F12, Space, Enter, Tab

KEYS = {"focus_next": "]",
        "focus_previous": "[",
        "hide_others": "Control-Shift-A",
        "reslice": "/",
        "to_front": "Control-Shift-F",
        "reset_view": "Control-Shift-R",
        }

# Overwrite napari shortcut
@napari.Viewer.bind_key("Alt-Up", overwrite=True)
def z_up(viewer:"napari.Viewer"):
    axes = "".join(viewer.dims.axis_labels)
    i = axes.find("z")
    if i < 0:
        return None
    else:
        step = list(viewer.dims.current_step)
        step[i] = min(step[i]+1, viewer.dims.nsteps[i]-1)
        viewer.dims.current_step = step
        return None


@napari.Viewer.bind_key("Alt-Down", overwrite=True)
def z_down(viewer:"napari.Viewer"):
    axes = "".join(viewer.dims.axis_labels)
    i = axes.find("z")
    if i < 0:
        return None
    else:
        step = list(viewer.dims.current_step)
        step[i] = max(step[i]-1, 0)
        viewer.dims.current_step = step
        return None
    
__all__ = list(KEYS.keys())

def bind_key(func):
    return napari.Viewer.bind_key(KEYS[func.__name__])(func)
    
@bind_key
def focus_next(viewer:"napari.Viewer"):
    _change_focus(viewer, 1)
    return None

@bind_key
def focus_previous(viewer:"napari.Viewer"):
    _change_focus(viewer, -1)
    return None

def _change_focus(viewer:"napari.Viewer", ind:int):
    # assert one Shapes or Points layer is selected
    selected_layer = get_a_selected_layer(viewer)
    if not isinstance(selected_layer, (napari.layers.Shapes, napari.layers.Points)):
        return None

    # check if one shape/point is selected
    selected_data = list(selected_layer.selected_data)
    if len(selected_data) != 1:
        return None
    selected_data = selected_data[0]
    
    # determine next/previous index/data to select
    ndata = len(selected_layer.data)
    next_to_select = (selected_data + ind) % ndata
    next_data = np.atleast_2d(selected_layer.data[next_to_select])
    
    # update camera    
    scale = selected_layer.scale
    next_center = np.mean(next_data, axis=0) * scale
    viewer.dims.current_step = list(next_data[0, :].astype(np.int64))
    
    viewer.camera.center = next_center
    zoom = viewer.camera.zoom
    viewer.camera.events.zoom() # Here events are emitted and zoom changes automatically.
    viewer.camera.zoom = zoom
    
    selected_layer.selected_data = {next_to_select}
    selected_layer._set_highlight()
    return None
    
    
@bind_key
def hide_others(viewer:"napari.Viewer"):
    """
    Make selected layers visible and others invisible. 
    """
    selected = viewer.layers.selection
    visibility_old = [layer.visible for layer in viewer.layers]
    visibility_new = [layer in selected for layer in viewer.layers]
    if visibility_old != visibility_new:
        for layer, vis in zip(viewer.layers, visibility_new):
            layer.visible = vis
    else:
        for layer in viewer.layers:
            layer.visible = True

@bind_key
def to_front(viewer:"napari.Viewer"):
    """
    Let selected layers move to front.
    """
    not_selected_index = [i for i, l in enumerate(viewer.layers) 
                          if l not in viewer.layers.selection]
    viewer.layers.move_multiple(not_selected_index, 0)
    
@bind_key
def reset_view(viewer:"napari.Viewer"):
    """
    Reset translate/scale parameters to the initial value.
    """    
    for layer in viewer.layers.selection:
        layer.translate -= (layer.translate - layer.metadata["init_translate"])
        layer.scale = layer.metadata["init_scale"]

@bind_key
def reslice(viewer:"napari.Viewer"):
    """
    2D Reslice with currently selected lines/paths and images.
    """
    if viewer.dims.ndisplay == 3:
        viewer.status = "Cannot reslice in 3D mode."
    imglist = list(iter_selected_layer(viewer, "Image"))
    
    ndim = np.unique([shape_layer.ndim for shape_layer 
                      in iter_selected_layer(viewer, "Shapes")])
    if len(ndim) > 1:
        viewer.status = "Cannot crop using Shapes layers with different number of dimensions."
    else:
        ndim = ndim[0]
        
    if ndim == viewer.dims.ndim == 3:
        active_plane = [-3, -2, -1]
    else:
        active_plane = [-2, -1]
        
    if len(imglist) == 0:
        imglist = [front_image(viewer)]
    
    paths = []
    for shape_layer in iter_selected_layer(viewer, "Shapes"):
        for shape, type_ in zip(shape_layer.data, shape_layer.shape_type):
            if type_ in ("line", "path"):
                paths.append((shape, shape_layer.scale)) # shape = float pixel
    out = []
    for path, shape_layer_scale in paths:        
        for layer in imglist:
            factor = layer.scale[active_plane]/shape_layer_scale[active_plane]
            dr = layer.translate[active_plane] / layer.scale[active_plane]
            out_ = layer.data.reslice(path[:,active_plane]/factor - dr)
            out.append(out_)
    
    viewer.window._results.append(out)
    
    return None
