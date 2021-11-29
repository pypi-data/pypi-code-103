import os
import tempfile

import numpy as np

import napari
from napari.plugins.io import save_layers

from napari_dexp import napari_get_reader

from dexp.datasets.zarr_dataset import ZDataset


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None


def test_write_and_read(make_napari_viewer):
    with tempfile.TemporaryDirectory() as tmpdir:
        ds_path = os.path.join(tmpdir, 'tmp.zarr')
        dataset = ZDataset(ds_path, mode='w')
        dataset.add_channel('Image', shape=(5, 25, 25, 25), dtype=int, value=0)
        dataset.append_metadata({
            'Image': {
                'dz': 2, 'dt': 20,
                'tx': 1.5, 'tz': 3.5,
            }
        })
        dataset.close()

        viewer: napari.Viewer = make_napari_viewer()
        layer = viewer.open(ds_path)[0]
        assert np.all(layer.scale == (20, 2, 1, 1))
        assert np.all(layer.translate == (0, 3.5, 0, 1.5))
        
        saved_path = os.path.join(tmpdir, 'saved.zarr')
        save_layers(saved_path, [layer])

        saved_layer = viewer.open(saved_path)[0]
        assert np.all(np.asarray(saved_layer.data) == np.asarray(layer.data))
