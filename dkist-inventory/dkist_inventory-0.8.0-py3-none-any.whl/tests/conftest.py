from pathlib import Path

import pytest
import astropy.units as u

from dkist.conftest import *
from dkist_inventory.asdf_generator import headers_from_filenames
from dkist_inventory.transforms import TransformBuilder

from dkist_data_simulator.spec214.vtf import SimpleVTFDataset
from dkist_data_simulator.spec214.visp import SimpleVISPDataset
from dkist_data_simulator.spec214.vbi import MosaicedVBIBlueDataset


def rm_tree(pth):
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()


@pytest.fixture(scope="session", params=["vtf", "visp", "vbi-mosaic"])
def header_directory(request, tmpdir_factory):
    atmpdir = Path(tmpdir_factory.mktemp(request.param))

    datasets = {
        "visp": SimpleVISPDataset(2, 2, 4, 10, linewave=500 * u.nm),
        "vtf": SimpleVTFDataset(2, 2, 4, 10, linewave=500 * u.nm),
        "vbi-mosaic": MosaicedVBIBlueDataset(n_time=2, time_delta=10, linewave=400 * u.nm),
    }

    ds = datasets[request.param]
    ds.generate_files(atmpdir, f"{request.param.upper()}_{{ds.index}}.fits")

    yield atmpdir

    # Cleanup at the end of the session
    rm_tree(atmpdir)


@pytest.fixture
def header_filenames(header_directory):
    files = list(header_directory.glob("*"))
    files.sort()
    return files


@pytest.fixture
def transform_builder(header_filenames):
    headers = headers_from_filenames(header_filenames)
    return TransformBuilder(headers)
