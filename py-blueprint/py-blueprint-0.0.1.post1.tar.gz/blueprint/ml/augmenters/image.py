# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import functools
import numpy as np
from typing import Tuple
import cv2
import random

from .basic import AugBase


class AsType(AugBase):
    """ x -> x
    """

    def __init__(self, dtype: np.dtype):
        self.dtype = dtype

    def process(self, x):
        return x.astype(self.dtype)


class ImRead(AugBase):
    """ path -> image
    """

    def process(self, path):
        return cv2.imread(path)


class Normalize255(AugBase):
    """ x -> clamp(float32(x / 255), 0, 1)
    """

    def process(self, x):
        result = (x / 255.0).astype(np.float32)
        result[result < 0] = 0
        result[result > 1] = 1
        return result


class Denormalize255(AugBase):
    """ x -> uint8(x * 255)
    """

    def process(self, x):
        result = (x * 255.0).astype(np.uint8)
        return result


class NormalizeImageNet(AugBase):
    def __init__(self):
        self.mean = np.array([0.485, 0.456, 0.406])    # rgb
        self.std = np.array([0.229, 0.224, 0.225])

    def process(self, im1):
        return (im1 - self.mean) / self.std


class HWC2CHW(AugBase):
    """ HWC -> CHW """

    def process(self, hwc):
        assert hwc.ndim == 3
        return np.transpose(hwc, (2, 0, 1))


class CHW2HWC(AugBase):
    """ CHW -> HWC """

    def process(self, chw):
        assert chw.ndim == 3
        return np.transpose(chw, (1, 2, 0))


class BGR2RGB(AugBase):
    """ BGR image -> RGB image
    """

    def process(self, bgr):
        assert bgr.ndim == 3
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


class RGB2BGR(AugBase):
    """ RGB image -> BGR image
    """

    def process(self, rgb):
        assert rgb.ndim == 3
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


class RGB2Gray(AugBase):
    """ RGB image -> Gray image (still 3 channels)
    """

    def process(self, rgb):
        assert rgb.ndim == 3
        im = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        return np.tile(np.expand_dims(im, -1), [1, 1, 3])


class FullLike(AugBase):
    """ array -> array
    """

    def __init__(self, fill_value):
        self.fill_value = fill_value

    def process(self, arr):
        return np.full_like(arr, self.fill_value)


class ArgMax(AugBase):
    """ value -> max_ids
    """

    def __init__(self, axis):
        self.axis = axis

    def process(self, data):
        return np.argmax(data, self.axis)


class RandomGray(AugBase):
    """ image -> image
    """

    def __init__(self, gray_ratio=0.1):
        self.gray_ratio = gray_ratio

    def process(self, image):
        if np.random.uniform() < self.gray_ratio:
            assert image.ndim == 3 and image.shape[-1] == 3
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            image = np.tile(np.expand_dims(image, -1), [1, 1, 3])
        return image


class RandomGamma(AugBase):
    """ image -> image
    """

    def process(self, im1):
        assert im1.ndim == 3
        im1[im1 < 0] = 0
        im1[im1 > 1] = 1
        gamma = np.random.choice([-1, 0, 1])
        if gamma == -1:
            im1 = np.sqrt(im1)
        elif gamma == 1:
            im1 = np.square(im1)
        return im1


class RandomBlur(AugBase):
    """ image -> image
    """

    def __init__(self, scale=0.01):
        self.scale = scale

    def process(self, im):
        blur_kratio = np.random.uniform(low=0.0, high=self.scale)
        blur_ksize = int(
            (im.shape[0] + im.shape[1]) / 2 * blur_kratio)
        if blur_ksize > 1:
            im = np.clip(im, 0, 1.0)
            im = cv2.blur(im, (blur_ksize, blur_ksize))
        return im


@functools.lru_cache()
def _to_cv_inter(interp):
    table = {
        'bilinear': cv2.INTER_LINEAR,
        'nearest': cv2.INTER_NEAREST}
    return table[interp]


class SwapLabels(AugBase):
    """ label, label_names -> label_swapped, label_names_swapped
    """

    def __init__(self, swap_label_names=None):
        if swap_label_names is None:
            swap_label_names = [['lb', 'rb'], ['le', 're'], ['lr', 'rr']]
        self.swap_label_names = swap_label_names
        assert isinstance(self.swap_label_names, (tuple, list))

    def process(self, data):
        assert isinstance(data, (tuple, list))
        label, label_names = data
        assert label.ndim == 2
        label_swapped = np.copy(label)
        index_swapped = list(range(len(label_swapped)))
        # swap
        for lname, rname in self.swap_label_names:
            if lname in label_names and rname in label_names:
                lid = label_names.index(lname)
                rid = label_names.index(rname)
                label_swapped[label == lid] = rid
                label_swapped[label == rid] = lid
                index_swapped[lid] = rid
                index_swapped[rid] = lid
        label_names_swapped = [label_names[i] for i in index_swapped]
        return label_swapped, label_names_swapped


class ConvertLabels(AugBase):
    """ label -> converted_label
    """

    def __init__(self, from_label_names, to_label_names, outlier_value=-1):
        self.from_label_names = from_label_names
        self.to_label_names = to_label_names
        self.outlier_value = outlier_value

    def process(self, label):
        if self.from_label_names == self.to_label_names:
            return label
        new_label = np.ones_like(label) * self.outlier_value
        for to_label_ind, label_name in enumerate(self.to_label_names):
            if label_name in self.from_label_names:
                from_label_ind = self.from_label_names.index(label_name)
                new_label[label == from_label_ind] = to_label_ind
        return new_label


class ConvertLabelValues(AugBase):
    """ label -> converted_label

    Example:
        aug.ConvertLabelValues([{0}, {1, 3, 4}, {}, {2, 5}])
    """

    def __init__(self, convert_label_values, outlier_value=-1):
        self.convert_label_values = convert_label_values
        self.outlier_value = outlier_value

    def process(self, label):
        new_label = np.ones_like(label) * self.outlier_value
        for to_ind, from_inds in enumerate(self.convert_label_values):
            for from_ind in from_inds:
                new_label[label == from_ind] = to_ind
        return new_label


class ConvertLabelsToBinaryMask(AugBase):
    """ label -> mask(bool)

    Example:
        aug.ConvertLabelsToBinaryMask(positive_label_values:list)
    """

    def __init__(self, positive_label_values: Tuple[int, list, tuple]):
        self.positive_label_values = positive_label_values

    def process(self, label):
        if isinstance(self.positive_label_values, int):
            return (label == self.positive_label_values).astype(np.uint8)
        return np.logical_or.accumulate(
            [label == v for v in self.positive_label_values], dtype=np.uint8)


class ReplaceBackground(AugBase):
    """ image, fg_alpha -> image
    """

    def __init__(self, bg_dataset, bg_tag='image'):
        self.bg_dataset = bg_dataset
        self.bg_tag = bg_tag

    def process(self, data):
        image, fg_alpha = data
        bg_ind = np.random.randint(0, len(self.bg_dataset))
        bg_im = self.bg_dataset[bg_ind][self.bg_tag]

        # random bg image
        # fit bg to image
        h, w = image.shape[:2]

        scale_factor = max(h / bg_im.shape[0], w / bg_im.shape[1])
        bg_im = cv2.resize(
            bg_im, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        assert bg_im.shape[0] >= h and bg_im.shape[1] >= w
        cx = np.random.randint(0, bg_im.shape[1] - w)
        cy = np.random.randint(0, bg_im.shape[0] - h)
        bg_im = bg_im[cy:cy + h, cx:cx + w, :] \
            if len(bg_im.shape) == 3 else bg_im[cy:cy + h, cx:cx + w]
        image = image * fg_alpha + \
            bg_im.astype(float) * (1.0 - fg_alpha)
        return image


class RandomPureColors(AugBase):
    """ image_shape -> image: float, [0~1]
    """

    def __init__(self, low=0.0, high=1.0):
        self.low = low
        self.high = high

    def process(self, image_shape):
        h, w, c = image_shape
        color = np.random.uniform(self.low, self.high, size=[1, 1, c])
        return np.broadcast_to(color, [h, w, c])


class RandomPixels(AugBase):
    """ image_shape -> image: float, [0~1]
    """

    def __init__(self, low=0.0, high=1.0):
        self.low = low
        self.high = high

    def process(self, image_shape):
        return np.random.uniform(self.low, self.high, size=image_shape)


class RandomOcclusion(AugBase):
    """ image -> image
    """

    def __init__(self, h_min: float = 0.2, h_max: float = 0.8, w_delta: float = 0.2):
        self.h_min = h_min
        self.h_max = h_max
        self.w_delta = w_delta

    def process(self, image):
        h, w, _ = image.shape
        rh = random.random() * (self.h_max - self.h_min) + self.h_min
        rw = rh - self.w_delta + 2 * self.w_delta * random.random()
        cx = int((h - 1) * random.random())
        cy = int((w - 1) * random.random())
        dh = int(h / 2 * rh)
        dw = int(w / 2 * rw)
        x0 = max(0, cx - dw // 2)
        y0 = max(0, cy - dh // 2)
        x1 = min(w - 1, cx + dw // 2)
        y1 = min(h - 1, cy + dh // 2)
        image = np.array(image)
        image[y0:y1+1, x0:x1+1, :] = 0
        return image


class NoiseFusion(AugBase):
    """ image -> image
    """

    def process(self, image):
        h, w, c = image.shape
        dtype = image.dtype
        noise = np.random.rand(h, w, c)
        alpha = 0.5 * random.random()
        image = (1 - alpha) * image + alpha * noise
        return image.astype(dtype)


class FlipImage(AugBase):
    """ image -> image
    """

    def __init__(self, axis=1):
        self.axis = axis

    def process(self, image):
        return np.array(np.flip(image, axis=self.axis))


class DrawPointsOnImage(AugBase):
    """ image (hxwx3), points (nx2) -> image """

    def __init__(self, radius, color=None, with_text=False, font_scale=0.2):
        self.radius = radius
        if color is None:
            color = [255] * 4
        self.color = color
        self.with_text = with_text
        self.font_scale = font_scale

    def process(self, data):
        image, points = data
        image = np.array(image)
        points = points.astype(np.int32)
        for i, (x, y) in enumerate(points):
            cv2.circle(image, (x, y), self.radius, self.color, -1, cv2.LINE_AA)
            if self.with_text:
                cv2.putText(image, str(i), (x+1, y-1),
                            cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                            self.font_scale, self.color, None, cv2.LINE_AA)
        return image
