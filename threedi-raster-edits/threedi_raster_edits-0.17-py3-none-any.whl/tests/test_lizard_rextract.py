# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 12:43:17 2021

@author: chris.kerklaan

#TODO functions:
    1. rextract
    
"""
import pathlib
import numpy as np
import os
from threedi_raster_edits import Vector
from threedi_raster_edits import RasterExtraction
from threedi_raster_edits import Raster


TEST_DIRECTORY = (
    str(pathlib.Path(__file__).parent.absolute()) + "/data/lizard_rextract/"
)


UUID = "7bef8398-ec43-41a5-868c-24c419d64dcb"
PASSWORD = "KmBOtiLM.heFnG6o7rd9wvFEi0zXRVS2vjStdGIHD"


def test_rextract_single_thread(tmpdir):
    """tests if rextract works"""
    path = tmpdir.mkdir("rextract").join("download.tif").strpath
    if os.path.exists(path):
        os.remove(path)

    vector = Vector(TEST_DIRECTORY + "geometry.shp")
    geometry = vector[0].geometry
    rextract = RasterExtraction(PASSWORD)
    rextract.run(path, UUID, geometry, threads=1)

    download = Raster(path)
    nansum = np.nansum(download.array)
    assert int(nansum) == -58124


def test_rextract_multi_thread(tmpdir):
    """tests if rextract works"""
    path = tmpdir.mkdir("rextract").join("download.tif").strpath
    if os.path.exists(path):
        os.remove(path)

    vector = Vector(TEST_DIRECTORY + "geometry.shp")
    geometry = vector[0].geometry
    rextract = RasterExtraction(PASSWORD)
    rextract.run(path, UUID, geometry, threads=2)

    download = Raster(path)
    nansum = np.nansum(download.array)
    assert int(nansum) == -58124


def test_rextract_loop_single_thread(tmpdir):
    """tests if rextract works"""

    path = tmpdir.mkdir("rextract").join("download.tif").strpath
    if os.path.exists(path):
        os.remove(path)

    vector = Vector(TEST_DIRECTORY + "geometry.shp")
    geometry = vector[0].geometry
    rextract = RasterExtraction(PASSWORD, quiet=False)
    rextract.set_variables(path, UUID, geometry)
    rextract.threads = 1
    for progress in rextract:
        pass

    download = Raster(path)
    nansum = np.nansum(download.array)
    assert int(nansum) == -58124


def test_rextract_loop_multi_thread(tmpdir):
    """tests if rextract works"""
    path = tmpdir.mkdir("rextract").join("download.tif").strpath
    if os.path.exists(path):
        os.remove(path)

    vector = Vector(TEST_DIRECTORY + "geometry.shp")
    geometry = vector[0].geometry
    rextract = RasterExtraction(PASSWORD, quiet=False)
    rextract.set_variables(path, UUID, geometry)
    rextract.threads = 2
    for progress in rextract:
        pass

    download = Raster(path)
    nansum = np.nansum(download.array)
    assert int(nansum) == -58124
