import os
import shutil
from multiprocessing import Process

import pytest

from stag.stag import main_
from stag.utils import chdir
from stag.config import read_config
from stag.signals import signals

SITES_DIR = os.path.join(os.path.dirname(__file__), "sites")
DISABLED = []


def copy_site(name, dst):
    source = os.path.join(SITES_DIR, name)
    shutil.copytree(source, dst)


def get_sites():
    _, directories, _ = next(os.walk(SITES_DIR))
    return directories


def get_files(root):
    for rd, _, fs in os.walk(root):
        for f in fs:
            yield os.path.join(rd, f)


@pytest.mark.parametrize("sitename", get_sites())
def test_site_generation(sitename, tmp_path):
    if sitename in DISABLED:
        pytest.skip(f"Disabled test for site generation: {sitename}")

    site_dir = tmp_path / sitename
    copy_site(sitename, site_dir)
    with chdir(site_dir):
        print(site_dir)
        output = "_output"

        # Use multiprocessing to sandbox each function call from each other.
        # Things which have global state which might need clearing include, but
        # are not limited to:
        #   - cached read_config()
        #   - global signals
        #   - loaded plugins (this is the tough one)
        p = Process(target=main_, args=(["build", "-o", output],))
        p.start()
        p.join()

        with open("expected_files.txt") as ef:
            expected_files = sorted(line.strip() for line in ef)

        generated_files = sorted(f[len(f"{output}/") :] for f in get_files(output))

        assert generated_files == expected_files
