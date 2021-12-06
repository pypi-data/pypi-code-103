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

import colorsys
import random
import numpy as np

import cv2
from matplotlib import pyplot as plt
from skimage import draw


def gen_random_colors(N, bright=True):
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors


_static_label_colors = [
    np.array((1.0, 1.0, 1.0), np.float32),
    np.array((255, 250, 79), np.float32) / 255.0,  # face
    np.array([255, 125, 138], np.float32) / 255.0,  # lb
    np.array([213, 32, 29], np.float32) / 255.0,  # rb
    np.array([0, 144, 187], np.float32) / 255.0,  # le
    np.array([0, 196, 253], np.float32) / 255.0,  # re
    np.array([255, 129, 54], np.float32) / 255.0,  # nose
    np.array([88, 233, 135], np.float32) / 255.0,  # ulip
    np.array([0, 117, 27], np.float32) / 255.0,  # llip
    np.array([255, 76, 249], np.float32) / 255.0,  # imouth
    np.array((1.0, 0.0, 0.0), np.float32),
    np.array((255, 250, 79), np.float32) / 255.0,
    np.array((255, 250, 79), np.float32) / 255.0,
    np.array((250, 245, 74), np.float32) / 255.0,
    np.array((0.0, 1.0, 0.5), np.float32),
    np.array((1.0, 0.0, 0.5), np.float32),
] + gen_random_colors(256)

_names_in_static_label_colors = [
    'bg', 'face', 'lb', 'rb', 'le', 're', 'nose',
    'ulip', 'llip', 'imouth', 'hair', 'lr', 'rr', 'neck',
    'cloth', 'eyeg', 'hat', 'earr'
]


def get_static_colors(size=0):
    if size <= len(_static_label_colors):
        return _static_label_colors
    return _static_label_colors + gen_random_colors(
        size-len(_static_label_colors))


def blend_labels(image, labels, label_names_dict=None,
                 default_alpha=0.6, color_offset=None):
    assert labels.ndim == 2
    bg_mask = labels == 0
    if label_names_dict is None:
        colors = _static_label_colors
    else:
        colors = [np.array((1.0, 1.0, 1.0), np.float32)]
        for i in range(1, labels.max() + 1):
            if isinstance(label_names_dict, dict) and i not in label_names_dict:
                bg_mask = np.logical_or(bg_mask, labels == i)
                colors.append(np.zeros((3)))
                continue
            label_name = label_names_dict[i]
            if label_name in _names_in_static_label_colors:
                color = _static_label_colors[
                    _names_in_static_label_colors.index(
                        label_name)]
            else:
                color = np.array((1.0, 1.0, 1.0), np.float32)
            colors.append(color)

    if color_offset is not None:
        ncolors = []
        for c in colors:
            nc = np.array(c)
            if (nc != np.zeros(3)).any():
                nc += color_offset
            ncolors.append(nc)
        colors = ncolors

    if image is None:
        image = orig_image = np.zeros(
            [labels.shape[0], labels.shape[1], 3], np.float32)
        alpha = 1.0
    else:
        orig_image = image / np.max(image)
        image = orig_image * (1.0 - default_alpha)
        alpha = default_alpha
    for i in range(1, np.max(labels) + 1):
        image += alpha * \
            np.tile(
                np.expand_dims(
                    (labels == i).astype(np.float32), -1),
                [1, 1, 3]) * colors[(i) % len(colors)]
    image[np.where(image > 1.0)] = 1.0
    image[np.where(image < 0)] = 0.0
    image[np.where(bg_mask)] = orig_image[np.where(bg_mask)]
    return image


_default_color = np.array([1, 0, 0], np.float32)


def draw_line(image, y1, x1, y2, x2, thickness, color=_default_color):
    if image.dtype == np.uint8:
        image = image / 255.0
    else:
        image = np.copy(image)

    perp = np.array([y1 - y2, x2 - x1])
    perp = perp * thickness / 2.0 / np.linalg.norm(perp)

    p1 = np.array([x1, y1])
    p2 = np.array([x2, y2])

    p1a = p1 - perp
    p1b = p1 + perp
    p2a = p2 - perp
    p2b = p2 + perp

    r = np.array([p1a[1], p2a[1], p2b[1], p1b[1]])
    c = np.array([p1a[0], p2a[0], p2b[0], p1b[0]])
    image[draw.polygon(r, c, shape=image.shape)] = color
    return image


def draw_boxes_y1x1y2x2(image, boxes, thickness, color=_default_color):
    r"""Draw boxes on image

    Args:
        image: A numpy array with shape h x w x 3, dtype uint8(0-255) or float(0-1)
        boxes: A numpy array with shape 4 or num_boxes x 4, dtype int

    Returns:
        image: h x w x 3, float(0-1)
    """
    if image.dtype == np.uint8:
        image = image / 255.0
    else:
        image = np.copy(image)
    if boxes.ndim == 1:
        boxes = np.expand_dims(boxes, 0)
    for i in range(boxes.shape[0]):
        y1, x1, y2, x2 = boxes[i]
        y1 = int(y1)
        x1 = int(x1)
        y2 = int(y2)
        x2 = int(x2)
        image = draw_line(image, y1 - thickness / 2, x1 - thickness / 2,
                          y1 - thickness / 2, x2 + thickness / 2,
                          thickness, color)
        image = draw_line(image, y1 - thickness / 2, x1 - thickness / 2,
                          y2 + thickness / 2, x1 - thickness / 2,
                          thickness, color)
        image = draw_line(image, y2 + thickness / 2, x1 - thickness / 2,
                          y2 + thickness / 2, x2 + thickness / 2,
                          thickness, color)
        image = draw_line(image, y1 - thickness / 2, x2 + thickness / 2,
                          y2 + thickness / 2, x2 + thickness / 2,
                          thickness, color)
    return image


def draw_circle(image, center_y, center_x, radius, color=_default_color):
    if image.dtype == np.uint8:
        image = image / 255.0
    else:
        image = np.copy(image)
    image[draw.circle(center_y, center_x, radius, shape=image.shape)] = color
    return image


def draw_points_yx(image, points, radius, color=_default_color):
    if image.dtype == np.uint8:
        image = image / 255.0
    else:
        image = np.copy(image)
    if points.ndim == 1:
        points = np.expand_dims(points, 0)
    for i in range(points.shape[0]):
        cy, cx = points[i]
        image = draw_circle(image, cy, cx, radius, color)
    return image


def draw_points_xy(image, points, radius, color=_default_color):
    if image.dtype == np.uint8:
        image = image / 255.0
    else:
        image = np.copy(image)
    if points.ndim == 1:
        points = np.expand_dims(points, 0)
    for i in range(points.shape[0]):
        cx, cy = points[i]
        image = draw_circle(image, cy, cx, radius, color)
    return image


def draw_landmarks(image, landmarks, color=None, radius=3,
                   with_text=False, font_scale=1.0, font_color=None):
    landmarks = landmarks.astype(np.int32)
    if color is None:
        color = [255] * 4
    if font_color is None:
        font_color = [255]
    for i, (x, y) in enumerate(landmarks):
        if callable(color):
            c = color(i)
        else:
            c = color
        cv2.circle(image, (x, y), radius, c, -1)
        if with_text:
            cv2.putText(image, str(i), (x+1, y-1),
                        cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, font_scale, font_color)
    return image


def set_plt_figsize(a, b):
    plt.rcParams['figure.figsize'] = (a, b)


def show_single(image, **kwargs):
    print(f'showing images with shape={image.shape}, '
          f'dtype={image.dtype}, max={image.max()}, min={image.min()}')
    plt.imshow(image, **kwargs)
    # plt.pause(0.1)
    plt.show()


def show_batch(images, nrows=1, **kwargs):
    assert images.ndim in [3, 4]
    if images.ndim == 3:
        images = np.expand_dims(images, -1)
    print(f'showing images with shape={images.shape}, '
          f'dtype={images.dtype}, max={images.max()}, min={images.min()}')
    for i, image in enumerate(images):
        plt.subplot(nrows, (len(images)+nrows-1)//nrows, i+1, frameon=True)
        plt.imshow(image, **kwargs)
    plt.show()


def show_multi(*images, nrows=1, **kwargs):
    if len(images) == 0:
        print('input is empty')
        return
    for i, image in enumerate(images):
        print(f'showing image[{i}] with shape={image.shape}, '
              f'dtype={image.dtype}, max={image.max()}, min={image.min()}')
        plt.subplot(nrows, (len(images)+nrows-1)//nrows, i+1, frameon=True)
        plt.imshow(image, **kwargs)
    plt.show()

