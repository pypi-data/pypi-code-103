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

from typing import Callable, Any

import numpy as np
import functools
from skimage import transform

from .basic import AugBase

try:
    from face_sdk import FaceDetection
except ImportError:
    FaceDetection = None


def _compute_iou(boxA, boxB):
    """compute_iou
    y1, x1, y2, x2
    """
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[1], boxB[1])
    yA = max(boxA[0], boxB[0])
    xB = min(boxA[3], boxB[3])
    yB = min(boxA[2], boxB[2])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[3] - boxA[1]) * (boxA[2] - boxA[0])
    boxBArea = (boxB[3] - boxB[1]) * (boxB[2] - boxB[0])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


def _get_pixel(single_mask, y, x, outlier=0):
    h = single_mask.shape[0]
    w = single_mask.shape[1]
    if y < 0 or y >= h or x < 0 or x >= w:
        return outlier
    return single_mask[y, x]


def _get_target_fa_points(label_names, label, fa_points):
    if fa_points.size == 0:
        return fa_points

    max_num_matches = 0
    num_faces = fa_points.shape[0]
    best_face_id = -1
    for ii in range(num_faces):
        le_x, le_y, re_x, re_y, nose_x, nose_y, *_ = [
            int(fa_points[ii, k, t]) for k in range(5) for t in range(2)]
        num_matches = 0
        for px, py, names in [
            (le_x, le_y, ['le', 'face', 'face_neck', 'fg']),
            (re_x, re_y, ['re', 'face', 'fg']),
                (nose_x, nose_y, ['nose', 'face', 'fg'])]:
            for name in names:
                if name in label_names and _get_pixel(
                        label, py, px, -1) == label_names.index(name):
                    num_matches += 1

        if num_matches > max_num_matches:
            best_face_id = ii
            max_num_matches = num_matches

    fa_points = fa_points[best_face_id]
    return fa_points


def _filter_fa_points(face_rects, fa_points,
                      area_thres=12, overlap_thres=0.5):
    if face_rects.shape[0] == 0:
        return face_rects, fa_points

    face_weights = (face_rects[:, 3] - face_rects[:, 1]) * \
        (face_rects[:, 2] - face_rects[:, 0])
    valid_face_inds = face_weights > area_thres
    face_weights = face_weights[valid_face_inds]
    face_rects = face_rects[valid_face_inds]
    fa_points = fa_points[valid_face_inds]

    # remove fa_points with high overlaps
    inds = np.argsort(face_weights)[::-1]
    kept_inds = []
    for ind in inds:
        rect = face_rects[ind, :]
        overlapped = False
        for kind in kept_inds:
            krect = face_rects[kind, :]
            if _compute_iou(rect, krect) > overlap_thres:
                overlapped = True
                break
        if not overlapped:
            kept_inds.append(ind)
    face_weights = face_weights[kept_inds]
    face_rects = face_rects[kept_inds, :]
    fa_points = fa_points[kept_inds, :, :]
    return face_rects, fa_points


def _make_face_detector(detector) -> FaceDetection:
    if FaceDetection is None:
        raise RuntimeError('FaceSDK is not installed')
    if detector == 'jda':
        return FaceDetection(algorithm_version=1)
    if detector == 'dnn':
        return FaceDetection(algorithm_version=5)
    if detector == 'sln':
        return FaceDetection(algorithm_version=11)
    if isinstance(detector, int):
        return FaceDetection(algorithm_version=detector)
    raise RuntimeError('unsupported detector type')


_default_detector_ = 'dnn'


def _convert_face_rects(face_rects_xywh):
    xs, ys, ws, hs = np.split(face_rects_xywh, 4, axis=1)
    x2s = xs + ws
    y2s = ys + hs
    return np.concatenate([ys, xs, y2s, x2s], axis=1)


class DetectFaces(AugBase):
    """ image -> multi_fa_points, [face_rects]
    """

    def __init__(self,
                 area_thres=12, overlap_thres=0.5, max_faces=1000,
                 detector=_default_detector_, ret_rects=False):
        self.det = _make_face_detector(detector)
        self.area_thres = area_thres
        self.overlap_thres = overlap_thres
        self.max_faces = max_faces
        self.ret_rects = ret_rects

    def process(self, image):
        face_rects_xywh, multi_fa_points = self.det.detect_and_align(image)
        multi_fa_points = np.reshape(multi_fa_points[:, :10], [-1, 5, 2])
        face_rects, multi_fa_points = _filter_fa_points(
            _convert_face_rects(face_rects_xywh)[:self.max_faces],
            multi_fa_points[:self.max_faces],
            area_thres=self.area_thres,
            overlap_thres=self.overlap_thres)

        if self.ret_rects:
            return multi_fa_points, face_rects
        else:
            return multi_fa_points


class DetectFace(AugBase):
    """ detect single face
        image -> fa_points, [face_rect]
    """

    def __init__(self, detector=_default_detector_, ret_rect=False):
        self.det = _make_face_detector(detector)
        self.ret_rect = ret_rect

    def process(self, image):
        face_rects_xywh, multi_fa_points = self.det.detect_and_align(image)
        multi_fa_points = np.reshape(multi_fa_points[:, :10], [-1, 5, 2])
        face_rects = _convert_face_rects(face_rects_xywh)
        if self.ret_rect:
            return multi_fa_points[0], face_rects[0]
        else:
            return multi_fa_points[0]


class DetectFaceWithGroundtruthScorer(DetectFaces):
    """ image, gt_data -> fa_points, [face_rect]
    """

    def __init__(self, scorer: Callable[[np.ndarray, Any], np.ndarray],
                 area_thres=12, overlap_thres=0.5, max_faces=1000,
                 detector=_default_detector_, ret_rects=False):
        super().__init__(
            area_thres, overlap_thres, max_faces, detector, ret_rects)
        self.scorer = scorer

    def process(self, data):
        image, gt_data = data
        if self.ret_rects:
            multi_fa_points, face_rects = super().process(image)
        else:
            multi_fa_points = super().process(image)

        face_gt_scores = self.scorer(multi_fa_points, gt_data)
        max_ind = np.argmax(face_gt_scores)

        if self.ret_rects:
            return multi_fa_points[max_ind], face_rects[max_ind]
        else:
            return multi_fa_points[max_ind]


class _ComputeFaceGtHits:
    def __init__(self, label_names):
        self.label_names = label_names

    def __call__(self, multi_fa_points, label):
        num_faces = multi_fa_points.shape[0]
        face_gt_hits = np.zeros((num_faces,), dtype=np.uint8)
        for ii in range(num_faces):
            le_x, le_y, re_x, re_y, nose_x, nose_y, *_ = [
                int(multi_fa_points[ii, k, t]) for k in range(5) for t in range(2)]
            for px, py, names in [
                (le_x, le_y, ['le', 'face', 'face_neck', 'fg']),
                (re_x, re_y, ['re', 'face', 'fg']),
                    (nose_x, nose_y, ['nose', 'face', 'fg'])]:
                for name in names:
                    if name in self.label_names and _get_pixel(
                            label, py, px, -1) == self.label_names.index(name):
                        face_gt_hits[ii] += 1
        return face_gt_hits


class DetectFaceWithGroundtruthLabel(DetectFaceWithGroundtruthScorer):
    """ image, label -> fa_points, [face_rect]
    """

    def __init__(self, label_names,
                 area_thres=12, overlap_thres=0.5, max_faces=1000,
                 detector=_default_detector_, ret_rects=False):
        super().__init__(
            _ComputeFaceGtHits(label_names),
            area_thres, overlap_thres, max_faces, detector, ret_rects)


@functools.lru_cache()
def _standard_face_pts():
    pts = np.array([
        196.0, 226.0,
        316.0, 226.0,
        256.0, 286.0,
        220.0, 360.4,
        292.0, 360.4], np.float32) / 256.0 - 1.0
    return np.reshape(pts, (5, 2))


class GetFaceAlignMatrices(AugBase):
    """ multi_face_align_points -> [out_shape], tranform_matrices
        or
        single_face_align_points -> [out_shape], transform_matrix
    """

    def __init__(self, target_shape, target_face_scale=1.0,
                 offset_xy=None, target_pts=None, ret_shape=False):
        if target_pts is None:
            std_pts = _standard_face_pts()  # [-1 1]
            h, w, *_ = target_shape
            self.target_pts = (std_pts * target_face_scale + 1) * \
                np.array([w-1, h-1], np.float32) / 2.0
            if offset_xy is not None:
                self.target_pts[:, 0] += offset_xy[0]
                self.target_pts[:, 1] += offset_xy[1]
        else:
            self.target_pts = np.array(target_pts)
        self.ret_shape = ret_shape

    def _estimate_single_face_align_matrix(self, fa_points):
        tform = transform.SimilarityTransform()
        tform.estimate(fa_points, self.target_pts)
        return tform.params

    def process(self, multi_fa_points):
        assert multi_fa_points.shape[-2:] == (5, 2)
        if multi_fa_points.ndim == 3:
            matrix = np.stack([self._estimate_single_face_align_matrix(fa_points)
                               for fa_points in multi_fa_points], 0)
        else:
            matrix = self._estimate_single_face_align_matrix(multi_fa_points)
        if self.ret_shape:
            return self.target_shape, matrix
        return matrix


GetFaceAlignMatrix = GetFaceAlignMatrices


class GetFaceRandomCropBox(AugBase):
    """ imshape, fa_points -> box
    """

    def __init__(self, crop_rescale_mean, crop_rescale_var,
                 crop_rescale_min=0.1, crop_rescale_max=10):
        self.crop_rescale_stats = (
            crop_rescale_mean, crop_rescale_var, crop_rescale_min, crop_rescale_max)

    def process(self, data):
        crop_rescale_mean, crop_rescale_var,\
            crop_rescale_min, crop_rescale_max = self.crop_rescale_stats
        crop_rescale = np.random.normal(
            crop_rescale_mean, crop_rescale_var)
        if crop_rescale < crop_rescale_min:
            crop_rescale = crop_rescale_min
        if crop_rescale > crop_rescale_max:
            crop_rescale = crop_rescale_max
        crop_dx_dy = np.random.uniform(0, 1, size=2)

        imshape, fa_points = data
        assert fa_points.shape == (5, 2)
        face_size = np.linalg.norm(fa_points[0, :] - fa_points[1, :])

        rescaled_im = int(face_size * crop_rescale)
        rescaled_im = min([imshape[0], imshape[1], rescaled_im])

        rand_dx, rand_dy = crop_dx_dy
        rand_dx = int(rand_dx * (imshape[1] - rescaled_im))
        rand_dy = int(rand_dy * (imshape[0] - rescaled_im))
        return np.array([rand_dy, rand_dx, rand_dy + rescaled_im,
                         rand_dx + rescaled_im], dtype=np.int32)
