# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from cv2 import getPerspectiveTransform, transform
from itertools import product
from numpy import array, diff, float32, ndarray, zeros_like
from numpy.linalg import norm
from scipy.optimize import linprog

def constrain_crop_transform (H: ndarray, width: int, height: int) -> ndarray:
    """
    Compute a transformation which applies a constrain crop to an image under a given transformation.

    Parameters:
        H (ndarray): Input transformation with shape (2,3) or (3,3).
        width (int): Image width.
        height (int): Image height.

    Returns:
        ndarray: Constrain cropping matrix.
    """
    # Compute dst rect
    src_rect = array([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]
    ], dtype=float32)
    dst_rect = transform(src_rect[None,:], H)
    dst_rect = dst_rect[0,:,:2] / dst_rect[0,:,2:] if dst_rect.shape[2] == 3 else dst_rect[0]
    # Compute internal normals
    edges = diff(dst_rect, axis=0, append=dst_rect[:1,:])
    normals = zeros_like(edges)
    normals[:,0] = -edges[:,1]
    normals[:,1] = edges[:,0]
    normals = normals / norm(normals, axis=1, keepdims=True)
    # Define vertex matrices
    aspect = width / height
    P = array([
        [[1., 0., 0.],
        [0., 1., 0.]],
        [[1., 0., 1.],
        [0., 1., 0.]],
        [[1., 0., 1.],
        [0., 1., 1. / aspect]],
        [[1., 0., 0.],
        [0., 1., 1. / aspect]]
    ])
    # Compute linear constraints
    A_ub = []
    b_ub = []
    for p, (n, v) in product(P, zip(normals, dst_rect)):
        A = n @ p
        b = (n * v).sum()
        A_ub.append(A)
        b_ub.append(b)
    A_ub = array(A_ub)
    b_ub = array(b_ub)
    # Optimize
    c = array([ 0., 0., 1. ])
    result = linprog(-c, -A_ub, -b_ub)
    u, v, w = result.x
    # Compute crop scale matrix
    crop_rect = array([ [u, v], [u + w, v], [u + w, v + w / aspect], [u, v + w / aspect] ], dtype=float32)
    T = getPerspectiveTransform(crop_rect, src_rect)
    return T