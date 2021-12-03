from importlib.util import find_spec
from pathlib import Path
from typing import Tuple

import torch
from torch import Tensor

from pycarus.geometry.pcd import batchify, unbatchify


def chamfer(
    prediction: Tensor,
    groundtruth: Tensor,
    squared: bool = True,
) -> Tuple[Tensor, Tensor]:
    """Compute the Chamfer Distance defined as in:

    Groueix, T., Fisher, M., Kim, V. G., Russell, B. C., & Aubry, M. (2018).
    A papier-mâché approach to learning 3d surface generation.
    In Proceedings of the IEEE conference on computer vision and pattern recognition (pp. 216-224).

    Args:
        prediction: The source point cloud(s) with shape ([B,] NUM_POINTS, 3).
        groundtruth: The target point cloud(s) with shape ([B,] NUM_POINTS, 3).
        squared: If true return the squared euclidean distance.

    Raises:
        ModuleNotFoundError: If the cuda extension is not installed.

    Returns:
        A tuple containing:
        - A tensor with the average distance from the prediction to the groundtruth.
        - A tensor with the average distance from the groundtruth to the prediction.
    """
    pcd_src = groundtruth
    pcd_trg = prediction

    use_cuda = pcd_src.device != torch.device("cpu")

    batched, [pcd_src, pcd_trg] = batchify([pcd_src, pcd_trg], 3)

    if use_cuda:
        not_chamfer_cuda = find_spec("chamfercuda") is None

        if not_chamfer_cuda:
            pycarus_root = Path(__file__).parent.parent.absolute()
            str_exp = "Chamfer CUDA module not found. Install it running: "
            str_exp += f"source {pycarus_root}/install_cuda_ext.sh {pycarus_root}"
            raise ModuleNotFoundError(str_exp)
        else:
            from pycarus.metrics.external.chamfer_cuda import Chamfer_CUDA  # type: ignore

            chamfer = Chamfer_CUDA()
            dist_x_y, dist_y_x, _, _ = chamfer(pcd_src, pcd_trg)
    else:
        x, y = pcd_src.double(), pcd_trg.double()
        size_batch, num_points_x, _ = x.size()
        size_batch, num_points_y, _ = y.size()

        xx = torch.pow(x, 2).sum(2)
        yy = torch.pow(y, 2).sum(2)
        zz = torch.bmm(x, y.transpose(2, 1))
        rx = xx.unsqueeze(1).expand(size_batch, num_points_y, num_points_x)  # Diagonal elements xx
        ry = yy.unsqueeze(1).expand(size_batch, num_points_x, num_points_y)  # Diagonal elements yy
        corr = rx.transpose(2, 1) + ry - 2 * zz

        dist_x_y = torch.min(corr, 2)[0].float()
        dist_y_x = torch.min(corr, 1)[0].float()

    if not squared:
        dist_x_y, dist_y_x = torch.sqrt(dist_x_y), torch.sqrt(dist_y_x)

    mean_dist_x_y, mean_dist_y_x = dist_x_y.mean(1), dist_y_x.mean(1)
    if batched:
        mean_dist_x_y, mean_dist_y_x = unbatchify([mean_dist_x_y, mean_dist_y_x])

    return mean_dist_x_y, mean_dist_y_x


def chamfer_p(prediction: Tensor, groundtruth: Tensor) -> Tensor:
    """Compute the chamfer distance "P".

    The result is computed as:
        - cd_pred2gt, cd_gt2pred = chamfer(prediction, groundtruth, squared=False)
        - result = (cd_pred2gt + cd_gt2pred) / 2.

    Args:
        prediction: The source point cloud(s) with shape ([B,] NUM_POINTS, 3).
        groundtruth: The target point cloud(s) with shape ([B,] NUM_POINTS, 3).

    Returns:
        The computed chamfer distance "P".
    """
    cds_pred_gt, cds_gt_pred = chamfer(prediction, groundtruth, squared=False)
    return (cds_gt_pred + cds_pred_gt) / 2


def chamfer_t(prediction: Tensor, groundtruth: Tensor) -> Tensor:
    """Compute the chamfer distance "T".

    The result is computed as:
        - cd_pred2gt, cd_gt2pred = chamfer(prediction, groundtruth, squared=True)
        - result = cd_pred2gt + cd_gt2pred.

    Args:
        prediction: The source point cloud(s) with shape ([B,] NUM_POINTS, 3).
        groundtruth: The target point cloud(s) with shape ([B,] NUM_POINTS, 3).

    Returns:
        The computed chamfer distance "T".
    """
    cds_pred_gt_sq, cds_gt_pred_sq = chamfer(prediction, groundtruth, squared=True)
    return cds_pred_gt_sq + cds_gt_pred_sq
