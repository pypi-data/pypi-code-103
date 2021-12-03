from typing import Tuple, Union

import numpy as np
import torch
from pykdtree.kdtree import KDTree  # type: ignore


def fscore(
    prediction: torch.Tensor, groundtruth: torch.Tensor, threshold: float = 0.001
) -> Tuple[Union[float, torch.Tensor], Union[float, torch.Tensor], Union[float, torch.Tensor]]:
    """Compute the F1-Score using the treshold as defined in:

    Knapitsch, A., Park, J., Zhou, Q. Y., & Koltun, V. (2017).
    Tanks and temples: Benchmarking large-scale scene reconstruction.
    ACM Transactions on Graphics (ToG), 36(4), 1-13.
    The function uses KdTree to compute the nearest neighbors

    Args:
        prediction: The predicted point cloud with shape ([B,] NUM_POINTS, 3).
        groundtruth: The groundtruth point cloud with shape ([B,] NUM_POINTS, 3).
        threshold: The euclidean distance treshold to use. Defaults to 0.001.

    Returns:
        A Tuple with:
        - The fscore (tensor or single value).
        - The precision (tensor or single value).
        - The recall (tensor or single value).
    """

    def single_sample_fscore(pred: torch.Tensor, gt: torch.Tensor) -> Tuple[float, float, float]:
        pred = pred.numpy()
        gt = gt.numpy()

        kd_tree = KDTree(gt)
        dist_precision, _ = kd_tree.query(pred, k=1)

        kd_tree = KDTree(pred)
        dist_recall, _ = kd_tree.query(gt, k=1)

        fscore, recall, precision = 0.0, 0.0, 0.0

        if len(dist_precision) and len(dist_recall):
            precision = np.sum(dist_precision < threshold) / len(pred)
            recall = np.sum(dist_recall < threshold) / len(gt)

            if recall + precision > 0:
                fscore = 2 * recall * precision / (recall + precision)

        return fscore, precision, recall

    if len(prediction.shape) > 2:
        size_batch = prediction.shape[0]
        b_f_score, b_precision, b_recall = [], [], []

        for i in range(size_batch):
            f_score, precision, recall = single_sample_fscore(prediction[i], groundtruth[i])
            b_f_score.append(f_score)
            b_precision.append(precision)
            b_recall.append(recall)

        f_score_t = torch.tensor(b_f_score, dtype=torch.float)
        precision_t = torch.tensor(b_precision, dtype=torch.float)
        recall_t = torch.tensor(b_recall, dtype=torch.float)

        return f_score_t, precision_t, recall_t
    else:
        return single_sample_fscore(prediction, groundtruth)
