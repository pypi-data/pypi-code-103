# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division

# Standard
import sys
from os.path import realpath, join, split

# Scientific
import numpy as np

# TPL
import pyhesaff
import utool as ut


ut.inject_colored_exceptions()


def get_testdata_dir(ensure=True, key='testdb1'):
    """
    Gets test img directory and downloads it if it doesn't exist
    """
    testdata_map = {
        'testdb1': 'https://wildbookiarepository.azureedge.net/data/testdata.zip'
    }
    zipped_testdata_url = testdata_map[key]
    testdata_dir = ut.grab_zipped_url(zipped_testdata_url, ensure=ensure)
    return testdata_dir


def get_test_image():
    img_fname = 'zebra.jpg'
    if '--zebra.png' in sys.argv:
        img_fname = 'zebra.jpg'
    if '--lena.png' in sys.argv:
        img_fname = 'lena.jpg'
    if '--jeff.png' in sys.argv:
        img_fname = 'jeff.png'
    imgdir = get_testdata_dir()
    img_fpath = realpath(join(imgdir, img_fname))
    return img_fpath


def load_test_data(short=False, n=0, use_cpp=False, **kwargs):
    import cv2

    if 'short' not in vars():
        short = False
    # Read Image
    # ellipse.rrr()
    nScales = 4
    nSamples = 16
    img_fpath = get_test_image()
    imgBGR = cv2.imread(img_fpath)
    imgLAB = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2LAB)
    imgL = imgLAB[:, :, 0]
    detect_kwargs = {'scale_min': 20, 'scale_max': 100}
    detect_kwargs.update(kwargs)
    if not use_cpp:
        kpts, desc = pyhesaff.detect_feats(img_fpath, **detect_kwargs)
    else:
        # Try the new C++ code
        [kpts], [desc] = pyhesaff.detect_feats_list([img_fpath], **detect_kwargs)

    if short and n > 0:
        extra_fxs = []
        if split(img_fpath)[1] == 'zebra.png':
            extra_fxs = [374, 520, 880][0:1]
        fxs = np.array(spaced_elements2(kpts, n).tolist() + extra_fxs)
        kpts = kpts[fxs]
        desc = desc[fxs]
    test_data = locals()
    return test_data


def spaced_elements2(list_, n):
    if n is None:
        return np.arange(len(list_))
    if n == 0:
        return np.empty(0)
    indexes = np.arange(len(list_))
    stride = len(indexes) // n
    return indexes[0:-1:stride]


def spaced_elements(list_, n):
    if n is None:
        return 'list'
    indexes = np.arange(len(list_))
    stride = len(indexes) // n
    return list_[indexes[0:-1:stride]]
