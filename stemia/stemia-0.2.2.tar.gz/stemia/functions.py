"""
useful functions for image processing
"""

from math import ceil

import numpy as np
from scipy.ndimage import rotate, label, fourier_shift, zoom
from scipy.fft import fft2, fftshift


def rot_avg(img):
    img_stack = np.zeros((360, *img.shape))
    for i in range(360):
        img_rot = rotate(img, i, reshape=False)
        img_stack[i] = img_rot
    return np.average(img_stack, axis=0)


def crop_center(img, keep, axis='xy'):
    """
    0 < keep < 1
    """
    x, y = img.shape
    startx = 0
    starty = 0
    cropx = x
    cropy = y
    if 'x' in axis:
        cropx = ceil(x * keep)
        startx = x // 2 - (cropx // 2)
    if 'y' in axis:
        cropy = ceil(y * keep)
        starty = y // 2 - (cropy // 2)
    return img[starty:starty+cropy, startx:startx+cropx]


def binarise(img, percentile):
    threshold = np.percentile(img, percentile)
    return np.where(img > threshold, 1, 0)


def to_positive(img):
    return img + img.min()


def fourier_translate(img, shift):
    trans_ft = fourier_shift(np.fft.fftn(img), shift)
    return np.real(np.fft.ifftn(trans_ft)).astype(np.float32)


def label_features(img, kernel=np.ones((3, 3))):
    labeled, count = label(img, structure=kernel)
    return labeled, range(1, count + 1)


def features_by_size(img, kernel=np.ones((3, 3))):
    labeled, count = label_features(img, kernel=kernel)
    by_size = []
    for lb in count:
        feature = np.where(labeled == lb, 1, 0)
        by_size.append(feature)
    by_size.sort(reverse=True, key=lambda feature: feature.sum())
    return labeled, by_size


def rotations(img, degree_range):
    """
    degree range: iterable of degrees (counterclockwise)
    """
    for angle in degree_range:
        yield angle, rotate(img, angle, reshape=False)


def coerce_ndim(img, ndim):
    if img.ndim > ndim:
        raise ValueError(f'image has too high dimensionality ({img.ndim})')
    while img.ndim < ndim:
        img = np.expand_dims(img, 0)
    return img


def cross_correlation(img1, img2):
    max_size = np.max([img1.shape, img2.shape], axis=0)
    ft1 = fft2(img1, max_size)
    ft2 = fft2(img2, max_size)
    # https://scikit-image.org/docs/0.11.x/auto_examples/plot_register_translation.html
    image_product = ft1 * ft2.conj()
    cc_image = fftshift(image_product)
    return cc_image.real


def match_pixel_size(mrc1, mrc2):
    v1 = mrc1.voxel_size
    v2 = mrc2.voxel_size
    ratio = v1.field(0) / v2.field(0)

    data1 = mrc1.data
    data2 = mrc2.data
    if ratio > 1:
        data1 = zoom(data1, 1 / ratio)
    elif ratio < 1:
        data2 = zoom(data2, ratio)

    return data1, data2
