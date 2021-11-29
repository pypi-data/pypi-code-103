from napari_plugin_engine import napari_hook_implementation
from napari.utils.colormaps.colormap_utils import AVAILABLE_COLORMAPS
from dexp.datasets.zarr_dataset import ZDataset
import numpy as np
import os


@napari_hook_implementation
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    paths = [path] if isinstance(path, str) else path

    # if we know we cannot read the file, we immediately return None.
    for path in paths:
        if not path.endswith((".zarr", ".zarr.zip")):
            return None
        elif path.endswith('.zarr') and '.zattrs' not in os.listdir(path):
            return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


LABELS_KEYWORDS = ('segment', 'instance', 'mask', 'label')


def _guess_layer_type(channel: str) -> str:
    # TODO: propose a better alternative using metadata?
    layer_type = 'image'
    for keyword in LABELS_KEYWORDS:
        if keyword in channel.lower():
            layer_type = 'labels'
            break
    return layer_type


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    paths = [path] if isinstance(path, str) else path

    layer_data = []

    for path in paths:
        mode = 'r' if path.endswith('.zip') else 'r+'
        dataset = ZDataset(path, mode=mode)

        for channel in dataset.channels():
            layer_type = _guess_layer_type(channel)

            add_kwargs = {
                'name': channel,
                'scale': dataset.get_resolution(channel),
                'translate': dataset.get_translation(channel),
            }

            array = dataset.get_array(channel)
            layer_data.append((array, add_kwargs, layer_type))

            if layer_type == 'image':
                add_kwargs['blending'] = 'additive'
                add_kwargs['rendering'] = 'attenuated_mip'
                add_kwargs['contrast_limits'] = (
                    0, 1500 if issubclass(array.dtype.type, np.integer) else 1.0
                )

                for colormap in AVAILABLE_COLORMAPS:
                    if colormap in channel.lower():
                        add_kwargs['colormap'] = colormap

                proj_array = dataset.get_projection_array(channel, axis=0)
                if proj_array is not None:
                    proj_array = np.asarray(proj_array)
                    proj_array = proj_array.reshape((proj_array.shape[0], 1, *proj_array.shape[1:]))

                    scale = add_kwargs['scale']
                    translation = add_kwargs['translate']
                    contrast_limits = add_kwargs['contrast_limits']
                    proj_kwargs = {
                        'name': 'proj_' + channel,
                        'blending': 'additive',
                        'visible': False,
                        'colormap': add_kwargs.get('colormap'),
                        'scale': [scale[0], 1] + scale[-2:],
                        'contrast_limits': contrast_limits,
                        'translate': [0] + translation[-2:],
                    }

                    layer_data.append((proj_array, proj_kwargs, layer_type))
        
    return layer_data
