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
import operator
import numpy as np
import random
import cv2
import math
import functools

from typing import Tuple, Callable, Dict, List, Any, Union

from torch.nn.functional import interpolate

from .basic import AugBase
from .image import _to_cv_inter


def degrees(deg):
    return deg / 180.0 * math.pi


class GetShape(AugBase):
    """ Tensor -> [h, w, c, ...]
    """

    def process(self, image):
        return image.shape


class MatrixMul(AugBase):
    """ a, b, ... -> a @ b @ ... """

    def process(self, data):
        return functools.reduce(operator.matmul, data)


class MatrixInv(AugBase):
    """ a -> inv(a) """

    def process(self, m):
        return np.linalg.inv(m)


def _compose_rotate_and_scale(angle, scale, shift_xy, from_center, to_center):
    cosv = math.cos(angle)
    sinv = math.sin(angle)

    fx, fy = from_center
    tx, ty = to_center

    acos = scale * cosv
    asin = scale * sinv

    a0 = acos
    a1 = -asin
    a2 = tx - acos * fx + asin * fy + shift_xy[0]

    b0 = asin
    b1 = acos
    b2 = ty - asin * fx - acos * fy + shift_xy[1]

    rot_scale_m = np.array([
        [a0, a1, a2],
        [b0, b1, b2],
        [0.0, 0.0, 1.0]
    ], np.float32)
    return rot_scale_m


def _compose_flip_x(w):
    return np.array([
        [-1, 0, w-1],
        [0, 1, 0],
        [0, 0, 1]
    ], np.float32)


def _compose_flip_y(h):
    return np.array([
        [1, 0, 0],
        [0, -1, h-1],
        [0, 0, 1]
    ], np.float32)


class GetTransformMatrix(AugBase):
    """ from_shape -> [to_shape], transform_matrix
    """

    def __init__(self, target_shape,
                 shift_xy_mu=(0.0, 0.0), rot_mu=0.0, scale_mu=1.0,
                 flip_x=False, flip_y=False, ret_shape=False):
        self.target_shape = target_shape
        self.shift_xy_mu = shift_xy_mu
        self.rot_mu = rot_mu
        self.scale_mu = scale_mu
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.ret_shape = ret_shape

    def process(self, from_shape):
        image_h, image_w, *_ = from_shape
        assert isinstance(image_h, int)
        assert isinstance(image_w, int)

        to_h, to_w, *_ = self.target_shape

        matrix = _compose_rotate_and_scale(
            self.rot_mu, self.scale_mu, self.shift_xy_mu,
            from_center=[(image_w-1)/2.0, (image_h-1)/2.0],
            to_center=[(to_w-1)/2.0, (to_h-1)/2.0])
        if self.flip_x:
            matrix = _compose_flip_x(to_w) @ matrix
        if self.flip_y:
            matrix = _compose_flip_y(to_h) @ matrix
        if self.ret_shape:
            return (to_h, to_w), matrix
        return matrix


class UpdateTransformMatrix(AugBase):
    """ from_shape, transform_matrix -> [to_shape], transform_matrix
    """

    def __init__(self, target_shape,
                 shift_xy_mu=(0.0, 0.0), rot_mu=0.0, scale_mu=1.0,
                 flip_x=False, flip_y=False, ret_shape=False):
        self.target_shape = target_shape
        self.shift_xy_mu = shift_xy_mu
        self.rot_mu = rot_mu
        self.scale_mu = scale_mu
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.ret_shape = ret_shape

    def process(self, data):
        from_shape, matrix = data

        image_h, image_w, *_ = from_shape
        to_h, to_w, *_ = self.target_shape

        trans_matrix = _compose_rotate_and_scale(
            self.rot_mu, self.scale_mu, self.shift_xy_mu,
            from_center=[(image_w-1)/2.0, (image_h-1)/2.0],
            to_center=[(to_w-1)/2.0, (to_h-1)/2.0])

        if matrix is not None:
            matrix = trans_matrix @ matrix
        else:
            matrix = trans_matrix

        if self.flip_x:
            matrix = _compose_flip_x(to_w) @ matrix
        if self.flip_y:
            matrix = _compose_flip_y(to_h) @ matrix
        if self.ret_shape:
            return (to_h, to_w), matrix
        return matrix


class UpdateRandomTransformMatrix(AugBase):
    """ from_shape, transform_matrix -> [to_shape], transform_matrix
    """

    def __init__(self, target_shape,
                 shift_sigma=0.1, rot_sigma=degrees(18), scale_sigma=0.1,
                 shift_mu=0.0, rot_mu=0.0, scale_mu=1.0,
                 shift_normal=True, rot_normal=True, scale_normal=True,
                 flip_x_rand=False, flip_y_rand=False, ret_shape=False):

        self.target_shape = target_shape
        self.shift_config = (shift_mu, shift_sigma, shift_normal)
        self.rot_config = (rot_mu, rot_sigma, rot_normal)
        self.scale_config = (scale_mu, scale_sigma, scale_normal)
        self.flip_x_rand = flip_x_rand
        self.flip_y_rand = flip_y_rand
        self.ret_shape = ret_shape

    def _random(self, mu_sigma_normal, size=None):
        mu, sigma, is_normal = mu_sigma_normal
        if is_normal:
            return np.random.normal(mu, sigma, size=size)
        else:
            return np.random.uniform(low=mu-sigma, high=mu+sigma, size=size)

    def process(self, data):
        assert isinstance(data, (tuple, list))
        from_shape, matrix = data
        assert isinstance(matrix, np.ndarray)

        from_h, from_w, *_ = from_shape
        to_h, to_w, *_ = self.target_shape

        if self.shift_config[:2] != (0.0, 0.0) or \
           self.rot_config[:2] != (0.0, 0.0) or \
           self.scale_config[:2] != (1.0, 0.0):
            shift_xy = self._random(self.shift_config, size=[2]) * \
                min(to_h, to_w)
            rot_angle = self._random(self.rot_config)
            scale = self._random(self.scale_config)
            trans_matrix = _compose_rotate_and_scale(
                rot_angle, scale, shift_xy,
                from_center=[(from_w-1)/2.0, (from_h-1)/2.0],
                to_center=[(to_w-1)/2.0, (to_h-1)/2.0])
            matrix = trans_matrix @ matrix

        if self.flip_x_rand and bool(random.getrandbits(1)):
            matrix = _compose_flip_x(to_w) @ matrix

        if self.flip_y_rand and bool(random.getrandbits(1)):
            matrix = _compose_flip_y(to_h) @ matrix

        if self.ret_shape:
            return (to_h, to_w), matrix
        return matrix


class UpdateResizeMatrix(AugBase):
    """ from_shape, transform_matrix -> [to_shape], transform_matrix
    """

    def __init__(self, target_shape, align_corners, ret_shape=False):
        self.target_shape = target_shape
        self.align_corners = align_corners
        self.ret_shape = ret_shape

    def process(self, data):
        (from_h, from_w, *_), matrix = data

        to_h, to_w, *_ = self.target_shape

        if self.align_corners:
            # to_x = from_x/(from_w-1)*(to_w-1)
            trans_matrix = np.array([
                [(to_w-1)/(from_w-1), 0, 0],
                [0, (to_h-1)/(from_h-1), 0],
                [0, 0, 1]], dtype=matrix.dtype)
        else:
            # to_x = (from_x+0.5)/from_w*to_w-0.5
            trans_matrix = np.array([
                [to_w/from_w, 0, 0.5*to_w/from_w-0.5],
                [0, to_h/from_h, 0.5*to_h/from_h-0.5],
                [0, 0, 1]], dtype=matrix.dtype)

        if matrix is None:
            matrix = trans_matrix
        else:
            matrix = trans_matrix @ matrix

        if self.ret_shape:
            return (to_h, to_w), matrix
        return matrix


class CenterSquaredBoxWithMaxSize(AugBase):
    """ from_shape -> box (y1x1y2x2)
    """

    def process(self, from_shape):
        h, w = from_shape[:2]
        m = min(h, w)
        y1 = (h-m) * 0.5
        x1 = (w-m) * 0.5
        return np.array([y1, x1, y1+m, x1+m], dtype=np.float32)


class RandomSquaredBoxWithMaxSize(AugBase):
    """ from_shape -> box (y1x1y2x2)
    """

    def process(self, from_shape):
        h, w = from_shape[:2]
        m = min(h, w)
        y1 = np.random.rand() * (h-m)
        x1 = np.random.rand() * (w-m)
        return np.array([y1, x1, y1+m, x1+m], dtype=np.float32)


class RandomSquaredBoxWithRandomSize(AugBase):
    """ from_shape -> box (y1x1y2x2)
    """

    def __init__(self, min_size, max_size) -> None:
        self.min_size = min_size
        self.max_size = max_size

    def process(self, from_shape):
        h, w = from_shape[:2]
        m = min(h, w)
        min_size = min(self.min_size, m)
        max_size = min(self.max_size, m)
        size = np.random.rand() * (max_size-min_size) + min_size
        y1 = np.random.rand() * (h-size)
        x1 = np.random.rand() * (w-size)
        return np.array([y1, x1, y1+size, x1+size], dtype=np.float32)


class UpdateCropAndResizeMatrix(AugBase):
    """ box (y1x1y2x2), matrix (3x3) -> [to_shape], matrix (3x3)

    Args:
        align_corners (bool): Set this to `True` only if the box you give has coordinates
            ranging from `0` to `h-1` or `w-1`.

        offset_box_coords (bool): Set this to `True` if the box you give has coordinates
            ranging from `0` to `h` or `w`. 

            Set this to `False` if the box coordinates range from `-0.5` to `h-0.5` or `w-0.5`.

            If the box coordinates range from `0` to `h-1` or `w-1`, set `align_corners=True`.
    """

    def __init__(self, target_shape, align_corners, ret_shape=False,
                 offset_box_coords=False):
        self.target_shape = target_shape
        self.align_corners = align_corners
        self.ret_shape = ret_shape
        self.offset_box_coords = offset_box_coords

    def process(self, data):
        (y1, x1, y2, x2), matrix = data
        h, w, *_ = self.target_shape
        dtype = matrix.dtype if matrix is not None else np.float32
        if self.align_corners:
            # x -> (x - x1) / (x2 - x1) * (w - 1)
            # y -> (y - y1) / (y2 - y1) * (h - 1)
            ax = 1.0 / (x2 - x1) * (w - 1)
            ay = 1.0 / (y2 - y1) * (h - 1)
            trans_matrix = np.array([
                [ax, 0, -x1 * ax],
                [0, ay, -y1 * ay],
                [0, 0, 1]
            ], dtype=dtype)
        else:
            if self.offset_box_coords:
                # x1, x2 \in [0, w], y1, y2 \in [0, h]
                # first we should offset x1, x2, y1, y2 to be ranging in
                # [-0.5, w-0.5] and [-0.5, h-0.5]
                # so to convert these pixel coordinates into boundary coordinates.
                x1, x2, y1, y2 = x1-0.5, x2-0.5, y1-0.5, y2-0.5

            # x -> (x - x1) / (x2 - x1) * w - 0.5
            # y -> (y - y1) / (y2 - y1) * h - 0.5
            ax = 1.0 / (x2 - x1) * w
            ay = 1.0 / (y2 - y1) * h
            trans_matrix = np.array([
                [ax, 0, -x1 * ax - 0.5],
                [0, ay, -y1 * ay - 0.5],
                [0, 0, 1]
            ], dtype=dtype)

        if matrix is None:
            matrix = trans_matrix
        else:
            matrix = trans_matrix @ matrix

        if self.ret_shape:
            return (h, w), matrix
        return matrix


def _make_n2p_mat(shape, align_corners):
    if shape is None:
        return None
    h, w = shape[:2]
    if align_corners:
        h, w = h-1, w-1
    return np.array([
        [w/2, 0, w/2],
        [0, h/2, h/2],
        [0, 0, 1]
    ], dtype=np.float32)


class ConvertTransformMatrixToPyTorchTheta(AugBase):
    """ ConvertTransformMatrixToPyTorchTheta

        from_shape, transform_matrix (3x3) -> theta (2x3)

        Convert a 3x3 transform matrix into a 2x3 theta matrix for 
        invoking torch.nn.functional.affine_grid.
    """

    def __init__(self, target_shape, inverse=True, keep3x3=False, align_corners=False):
        self.p2n_to = np.linalg.inv(_make_n2p_mat(target_shape, align_corners))
        self.inverse = inverse
        self.keep3x3 = keep3x3
        self.align_corners = align_corners

    def process(self, data):
        from_shape, matrix = data
        n2p_from = _make_n2p_mat(from_shape, self.align_corners)
        if self.inverse:
            matrix = np.linalg.inv(matrix)
        theta = self.p2n_to @ matrix @ n2p_from
        if self.keep3x3:
            return theta
        else:
            return theta[:2, :]


class ConvertPyTorchThetaToTransformMatrix(AugBase):
    """ ConvertTransformMatrixToPyTorchTheta

        from_shape, theta (2x3) -> transform_matrix (3x3)

        Convert a 2x3 theta matrix into a 3x3 transform matrix.
    """

    def __init__(self, target_shape, inverse=True, align_corners=False):
        self.n2p_to = _make_n2p_mat(target_shape, align_corners)
        self.inverse = inverse
        self.align_corners = align_corners

    def process(self, data):
        from_shape, theta = data
        p2n_from = np.linalg.inv(_make_n2p_mat(from_shape, self.align_corners))

        if theta.size(0) == 2:
            theta = np.concatenate(
                [theta, np.zeros([1, 3], dtype=theta.dtype)], axis=0)

        matrix = self.n2p_to @ theta @ p2n_from
        if self.inverse:
            matrix = np.linalg.inv(matrix)
        return matrix


@functools.lru_cache(maxsize=128)
def _meshgrid(h, w):
    yy, xx = np.meshgrid(np.arange(0, h, dtype=np.float32),
                         np.arange(0, w, dtype=np.float32),
                         indexing='ij')
    return yy, xx


def _forge_transform_map(output_shape, fn: Callable[[np.ndarray], np.ndarray]
                         ) -> Tuple[np.ndarray, np.ndarray]:
    """ Forge transform maps with a given function `fn`.

    Args:
        output_shape (tuple): (h, w, ...).
        fn (Callable[[np.ndarray], np.ndarray]): The function that accepts 
            a Nx2 array and outputs the transformed Nx2 array. Both input 
            and output store (x, y) coordinates.

    Note: 
        both input and output arrays of `fn` should store (y, x) coordinates.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Two maps `X` and `Y`, where for each pixel (y, x) or coordinate (x, y),
            `(X[y, x], Y[y, x]) = fn([x, y])`
    """
    h, w, *_ = output_shape
    yy, xx = _meshgrid(h, w)  # h x w
    in_xxyy = np.stack([xx, yy], axis=-1).reshape([-1, 2])  # (h x w) x 2
    out_xxyy: np.ndarray = fn(in_xxyy)  # (h x w) x 2
    return out_xxyy.reshape([h, w, 2])


def _safe_arctanh(x):
    x[x < -0.999] = -0.999
    x[x > +0.999] = +0.999
    x = np.arctanh(x)
    return x


def _tanh_warp_transform(coords, transform_matrix, warp_factor, warped_shape):
    """ Tanh-warp function.

    Args:
        coords (np.ndarray): N x 2 (x, y).
        transform_matrix: 3 x 3. A matrix that transforms un-normalized coordinates 
            from the original image to the aligned yet not-warped image.
        warp_factor (float): The warp factor. 
            0 means linear transform, 1 means full tanh warp.
        warped_shape (tuple): [height, width].

    Returns:
        np.ndarray: N x 2 (x, y).
    """
    h, w, *_ = warped_shape
    # h -= 1
    # w -= 1

    if warp_factor > 0:
        # normalize coordinates to [-1, +1]
        coords = coords / np.array([w, h], dtype=coords.dtype) * 2 - 1

        nl_part1 = coords > 1.0 - warp_factor
        nl_part2 = coords < -1.0 + warp_factor

        coords[nl_part1] = _safe_arctanh(
            (coords[nl_part1] - 1.0 + warp_factor) /
            warp_factor) * warp_factor + \
            1.0 - warp_factor
        coords[nl_part2] = _safe_arctanh(
            (coords[nl_part2] + 1.0 - warp_factor) /
            warp_factor) * warp_factor - \
            1.0 + warp_factor

        # denormalize
        coords = (coords + 1) / 2 * np.array([w, h], dtype=coords.dtype)

    coords_homo = np.concatenate(
        [coords, np.ones([coords.shape[0], 1], dtype=coords.dtype)], axis=1)  # N x 3

    inv_matrix = np.linalg.inv(transform_matrix)
    coords_homo = np.dot(coords_homo, inv_matrix.T)  # N x 3
    return (coords_homo[:, :2] / coords_homo[:, [2, 2]]).astype(coords.dtype)


def _inverted_tanh_warp_transform(coords, transform_matrix, warp_factor, warped_shape):
    """ Inverted Tanh-warp function.

    Args:
        coords (np.ndarray): N x 2 (x, y).
        transform_matrix: 3 x 3. A matrix that transforms un-normalized coordinates 
            from the original image to the aligned yet not-warped image.
        warp_factor (float): The warp factor. 
            0 means linear transform, 1 means full tanh warp.
        warped_shape (tuple): [height, width].

    Returns:
        np.ndarray: N x 2 (x, y).
    """
    h, w, *_ = warped_shape
    # h -= 1
    # w -= 1

    coords_homo = np.concatenate(
        [coords, np.ones([coords.shape[0], 1], dtype=coords.dtype)], axis=1)  # N x 3

    coords_homo = np.dot(coords_homo, transform_matrix.T)  # N x 3
    coords = (coords_homo[:, :2] / coords_homo[:, [2, 2]]).astype(coords.dtype)

    if warp_factor > 0:
        # normalize coordinates to [-1, +1]
        coords = coords / np.array([w, h], dtype=coords.dtype) * 2 - 1

        nl_part1 = coords > 1.0 - warp_factor
        nl_part2 = coords < -1.0 + warp_factor

        coords[nl_part1] = np.tanh(
            (coords[nl_part1] - 1.0 + warp_factor) /
            warp_factor) * warp_factor + \
            1.0 - warp_factor
        coords[nl_part2] = np.tanh(
            (coords[nl_part2] + 1.0 - warp_factor) /
            warp_factor) * warp_factor - \
            1.0 + warp_factor

        # denormalize
        coords = (coords + 1) / 2 * np.array([w, h], dtype=coords.dtype)

    return coords


class GetTransformMap(AugBase):
    """ transform_matrix -> map

    Args:
        warped_shape: The target image shape to transform to.
        warp_factor: The warping factor. `warp_factor=1.0` represents a vannila Tanh-warping, 
            `warp_factor=0.0` represents a cropping.

    This involves an implementation of the Tanh-warping, which is proposed in:

        [1] Lin, Jinpeng, Hao Yang, Dong Chen, Ming Zeng, Fang Wen, and Lu Yuan. 
            "Face parsing with roi tanh-warping." In Proceedings of the IEEE/CVF 
            Conference on Computer Vision and Pattern Recognition, pp. 5654-5663. 2019.

        [2] Zheng, Yinglin, Hao Yang, Ting Zhang, Jianmin Bao, Dongdong Chen, Yangyu Huang,
            Lu Yuan, Dong Chen, Ming Zeng and Fang Wen. "General Facial Representation 
            Learning in a Visual-Linguistic Manner" In arxiv.

    Please cite the paper on your usage.

    """

    def __init__(self, warped_shape, warp_factor=0.0):
        self.warped_shape = warped_shape
        self.warp_factor = warp_factor

    def process(self, matrix):
        return _forge_transform_map(
            self.warped_shape,
            functools.partial(_tanh_warp_transform,
                              transform_matrix=matrix,
                              warp_factor=self.warp_factor,
                              warped_shape=self.warped_shape))


class GetInvertedTransformMap(AugBase):
    """ transform_matrix, original_image_shape -> inverted_map

    This is an inverted transform of GetTransformMap.

    Args:
        warped_shape: The target image shape to transform to.
        warp_factor: The warping factor. `warp_factor=1.0` represents a vannila Tanh-warping, 
            `warp_factor=0.0` represents a cropping.

    This involves an implementation of the Tanh-warping, which is proposed in:

        [1] Lin, Jinpeng, Hao Yang, Dong Chen, Ming Zeng, Fang Wen, and Lu Yuan. 
            "Face parsing with roi tanh-warping." In Proceedings of the IEEE/CVF 
            Conference on Computer Vision and Pattern Recognition, pp. 5654-5663. 2019.
            
        [2] Zheng, Yinglin, Hao Yang, Ting Zhang, Jianmin Bao, Dongdong Chen, Yangyu Huang,
            Lu Yuan, Dong Chen, Ming Zeng and Fang Wen. "General Facial Representation 
            Learning in a Visual-Linguistic Manner" In arxiv.

    Please cite the paper on your usage.

    """

    def __init__(self, warped_shape, warp_factor=0.0):
        self.warped_shape = warped_shape
        self.warp_factor = warp_factor

    def process(self, data):
        matrix, orig_shape = data
        return _forge_transform_map(
            orig_shape,
            functools.partial(_inverted_tanh_warp_transform,
                              transform_matrix=matrix,
                              warp_factor=self.warp_factor,
                              warped_shape=self.warped_shape))


class TransformByMap(AugBase):
    """ image, map -> transformed_image
    """

    def __init__(self, interpolation: str, outlier_value=0, outlier_range=None):
        self.interpolation = _to_cv_inter(interpolation)
        self.outlier_value = outlier_value
        self.outlier_range = outlier_range

    def process(self, data):
        image, map_xxyy = data
        xx = map_xxyy[:, :, 0]
        yy = map_xxyy[:, :, 1]
        if self.outlier_range is None:
            ov = self.outlier_value
        else:
            ov = np.random.uniform(
                low=self.outlier_range[0], high=self.outlier_range[1],
                size=[image.shape[2]])
        return cv2.remap(image, xx, yy, self.interpolation,
                         borderMode=cv2.BORDER_CONSTANT,
                         borderValue=ov)


class TransformPoints2D(AugBase):
    """ points, matrix3x3 -> points
    """

    def __init__(self, warped_shape, warp_factor=0.0):
        self.warped_shape = warped_shape
        self.warp_factor = warp_factor

    def process(self, data):
        points, matrix = data
        return _inverted_tanh_warp_transform(
            points, matrix, self.warp_factor, self.warped_shape)


class TransformPoints2DInverted(AugBase):
    """ points, matrix3x3 -> points
    """

    def __init__(self, warped_shape, warp_factor=0.0):
        self.warped_shape = warped_shape
        self.warp_factor = warp_factor

    def process(self, data):
        points, matrix = data
        return _tanh_warp_transform(
            points, matrix, self.warp_factor, self.warped_shape)


class TransformAll(AugBase):
    """ (image/point, ...), matrix3x3 -> (transformed_image/transformed_point, ...)
    """

    def __init__(self, warped_shape, warp_factor: float,
                 warp_configs: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        self.warped_shape = warped_shape
        self.warp_factor = warp_factor

        if isinstance(warp_configs, dict):
            warp_configs = [warp_configs]
            self.is_single_input = True
        else:
            self.is_single_input = False
        self.warp_configs = warp_configs
        self.has_image = any(
            [cfg['data_type'] == 'image' for cfg in self.warp_configs])

    def process(self, data):
        input_data, matrix = data
        if self.is_single_input:
            input_data = [input_data]

        outputs = []
        if self.has_image:
            map_xxyy = _forge_transform_map(
                self.warped_shape,
                functools.partial(_tanh_warp_transform,
                                  transform_matrix=matrix,
                                  warp_factor=self.warp_factor,
                                  warped_shape=self.warped_shape))
            xx = map_xxyy[:, :, 0]
            yy = map_xxyy[:, :, 1]

        for d, cfg in zip(input_data, self.warp_configs):
            assert isinstance(d, np.ndarray)
            data_type = cfg['data_type']
            if data_type == 'image':
                assert d.ndim == 3
                if 'outlier_range' not in cfg:
                    ov = cfg.get('outlier_value', 0)
                else:
                    ov = np.random.uniform(
                        low=cfg['outlier_range'][0], high=cfg['outlier_range'][1],
                        size=[d.shape[2]])
                outputs.append(cv2.remap(d, xx, yy, _to_cv_inter(cfg['interpolation']),
                                         borderMode=cv2.BORDER_CONSTANT,
                                         borderValue=ov))
            elif data_type == 'point':
                assert d.ndim == 2
                assert d.shape[1] == 2
                outputs.append(_inverted_tanh_warp_transform(
                    d, matrix, self.warp_factor, self.warped_shape))
            else:
                raise RuntimeError(
                    f'Unsupported data_type in TransformWithWarp: {data_type}')

        if self.is_single_input:
            return outputs[0]
        return outputs


class TransformPoints2DPerspective(AugBase):
    """ points (nx2), matrix3x3 -> points (nx2)
    """

    def process(self, data):
        points, matrix = data
        dtype = points.dtype

        # nx3
        points = np.concatenate([points, np.ones_like(points[:, [0]])], axis=1)
        points = points @ np.transpose(matrix)  # nx3
        points = points[:, :2] / points[:, [2, 2]]
        return points.astype(dtype)


class TransformImagePerspective(AugBase):
    """ image, matrix3x3 -> transformed_image
    """

    def __init__(self, target_shape, interpolation: str, outlier_value=0, outlier_range=None):
        self.target_shape = target_shape
        self.interpolation = _to_cv_inter(interpolation)
        self.outlier_value = outlier_value
        self.outlier_range = outlier_range

    def process(self, data):
        image, mat = data
        if self.outlier_range is None:
            ov = self.outlier_value
        else:
            ov = np.random.uniform(
                low=self.outlier_range[0], high=self.outlier_range[1],
                size=[image.shape[2]])
        return cv2.warpPerspective(
            image, mat, dsize=(self.target_shape[1], self.target_shape[0]),
            flags=self.interpolation, borderValue=ov)


class FlipLROrderedPoints(AugBase):
    """ points (nx2) -> points (nx2)
    """

    def __init__(self, image_shape, flip_mapping: List[Tuple[int, int]]) -> None:
        self.image_shape = image_shape
        self.flip_mapping = flip_mapping

    def process(self, points):
        _, w, *_ = self.image_shape
        points_flip = np.array(points)
        for i, j in self.flip_mapping:
            points_flip[i] = points[j]
            points_flip[j] = points[i]
        points_flip[:, 0] = w - 1 - points_flip[:, 0]
        return points_flip
