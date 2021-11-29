# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from cv2 import cornerHarris, findTransformECC, MOTION_TRANSLATION, TERM_CRITERIA_COUNT, TERM_CRITERIA_EPS
from numpy import argpartition, array, asarray, eye, column_stack, concatenate, float32, ndarray, ones, split, stack as stack_array, unravel_index
from numpy.linalg import norm
from PIL import Image
from sklearn.linear_model import LinearRegression, RANSACRegressor
from torch import cat, linspace, meshgrid, stack, Tensor
from torch.nn.functional import grid_sample
from typing import Tuple

def tca_model (image: Image.Image, order: int=2) -> ndarray:
    """
    Compute a lens model which corrects transverse chromatic aberration.

    Parameters:
        image (PIL.Image): Input image.
        order (int): Polynomial order of lens model. Quadratic or cubic model is ideal.

    Returns:
        ndarray: Red-blue channel lens correction model with shape (2,P) where P is the polynomial order.
    """
    # Find ROI centers
    image_arr = asarray(image)
    roi = compute_roi(image_arr, region_count=8, corner_threshold=0.05)
    # Extract patches
    patch_size = int(min(image.width, image.height) * 0.05)
    patches, centers = extract_patches(image_arr, roi, size=patch_size)
    model = compute_coefficients(patches, centers, image.size, order=order)
    return model

def tca_grid (model: ndarray, width: int, height: int) -> Tensor:
    """
    Compute a sample grid from a lens model.

    Parameters:
        model (ndarray): TCA lens model with shape (2,P).
        width (int): Image width. Note that this must be the same value used to create the TCA model.
        height (int): Image height. Note that this must be the same value used to create the TCA model.

    Returns:
        Tensor: Sample grid with shape (1,2,H,W,2).
    """
    # Construct sample grid
    hg, wg = meshgrid(linspace(-1., 1., height), linspace(-1., 1., width))
    hg = hg.repeat(1, 1, 1).unsqueeze(dim=3)
    wg = wg.repeat(1, 1, 1).unsqueeze(dim=3)
    sample_field = cat([wg, hg], dim=3)
    r_dst = sample_field.norm(dim=3, keepdim=True)
    # Compute distortions
    red_distortion = stack([coeff * r_dst.pow(i) for i, coeff in enumerate(model[0])], dim=0).sum(dim=0)
    blue_distortion = stack([coeff * r_dst.pow(i) for i, coeff in enumerate(model[1])], dim=0).sum(dim=0)
    # Compute sample grids
    red_grid = sample_field * red_distortion
    blue_grid = sample_field * blue_distortion
    # Stack
    grid = stack([red_grid, blue_grid], dim=1)
    return grid

def tca_correction (input: Tensor, grid: Tensor) -> Tensor:
    """
    Appply transverse chromatic aberration correction to an image.

    Parameters:
        input (Tensor): Input image with shape (N,C,H,W).
        grid (Tensor): Sample grid with shape (N,2,H,W,2) in range [-1., 1.].

    Returns:
        Tensor: Corrected image with shape (N,C,H,W).
    """
    # Split grid
    grid = grid.to(input.device)
    red_grid, blue_grid = grid.unbind(dim=1)
    # Sample
    red, green, blue = input.split(1, dim=1)
    red_shifted = grid_sample(red, red_grid, mode="bilinear", padding_mode="border", align_corners=False)
    blue_shifted = grid_sample(blue, blue_grid, mode="bilinear", padding_mode="border", align_corners=False)
    # Combine
    result = cat([red_shifted, green, blue_shifted], dim=1)
    return result

def compute_roi (input: ndarray, region_count: int=8, corner_threshold: float=0.05) -> ndarray:
    """
    Compute regions of interest with chromatic aberration.

    Parameters:
        image (ndarray): Input image with shape (H,W,3).
        region_count (int): Number of independent regions R on each axis to evaluate.
        corner_threshold (float): Minimum cornerness for pixel to be considered ROI, in range [0., 1.].

    Returns:
        ndarray: Region of interest coordinates with shape (N,2).
    """
    # Compute cornerness over entire image
    corner_map = cornerHarris(input[...,1].astype(float32), 2, 3, 0.04)
    corner_threshold = corner_map.max() * corner_threshold
    # Evaluate regions
    height, width, _ = input.shape
    patch_size = array([width, height]) // region_count
    CORNER_COUNT = 1 # Number of corners to extract per region
    roi = []
    for j in range(region_count):
        for i in range(region_count):
            # Extract region
            min = array([i * patch_size[0], j * patch_size[1]])
            max = min + patch_size
            region = input[min[1]:max[1],min[0]:max[0],1]
            # Find corners
            corner_map = cornerHarris(region.astype(float32), 2, 3, 0.04)
            corner_indices = argpartition(corner_map, -CORNER_COUNT, axis=None)[-CORNER_COUNT:]
            y_coords, x_coords = unravel_index(corner_indices, corner_map.shape)
            coords = column_stack([x_coords, y_coords])
            # Threshold
            for coord in coords: # CHECK # Need to vectorize this
                x, y = coord
                if corner_map[y, x] > corner_threshold:
                    roi.append(coord + min)
    roi = stack_array(roi)
    return roi

def extract_patches (input: ndarray, centers: ndarray, size: int=0.05) -> Tuple[ndarray, ndarray]:
    """
    Extract image patches centered around a set of coordinates.
    
    Note that the number of returned patches might be less than N, as patches that are not full-size are discarded.

    Parameters:
        input (ndarray): Input image with shape (H,W,3).
        centers (ndarray): Patch center (x,y) coordinates with shape (N,2).
        size (float): Relative patch size in range [0., 1.].

    Returns:
        tuple: Patch stack with shape (M,S,S,3) and patch centers with shape (M,2).
    """
    min_points = centers - size // 2
    patches = [input[y_min:y_max, x_min:x_max] for x_min, y_min, x_max, y_max in concatenate([min_points, min_points + size], axis=1)]
    patches = [(patch, center) for patch, center in zip(patches, centers) if patch.shape[0] == patch.shape[1] == size]
    patches, centers = zip(*patches)
    patches, centers = stack_array(patches), stack_array(centers)
    return patches, centers

def compute_coefficients (patches: ndarray, centers: ndarray, size: tuple, order: int=3) -> ndarray:
    """
    Compute per-patch alignment displacements for N patches.

    Note that the number of returned displacements might be less than N.
    This happens when no suitable displacement can be computed for a given patch.

    Parameters:
        patches (ndarray): Patch stack with shape (N,S,S,3).
        centers (ndarray): Patch center (x,y) coordinates with shape (N,2).
        size (tuple): Image size (W,H).
        order (int): Polynomial order of lens correction model.

    Returns:
        ndarray: Red and blue channel coefficients with shape (2,P) where P is the polynomial order.
    """
    # Check
    if patches.shape[0] < 4:
        return None
    # Constants
    IDENTITY = eye(2, 3, dtype=float32)
    CRITERIA = (TERM_CRITERIA_EPS | TERM_CRITERIA_COUNT, 50, 1e-4)
    # Compute
    displacements = []
    mask = ones(patches.shape[0]).astype(bool)
    for i, patch in enumerate(patches):
        try:
            patch_r, patch_g, patch_b = split(patch, 3, axis=2)
            _, warp_matrix_r = findTransformECC(patch_g, patch_r, IDENTITY.copy(), MOTION_TRANSLATION, CRITERIA, None, 5)
            _, warp_matrix_b = findTransformECC(patch_g, patch_b, IDENTITY.copy(), MOTION_TRANSLATION, CRITERIA, None, 5)
            displacement = -stack_array([warp_matrix_r[:,2], warp_matrix_b[:,2]], axis=0) # invert displacement
            displacements.append(displacement)
        except:
            mask[i] = False
    # Get successful displacements
    displacements = stack_array(displacements)
    centers = centers[mask]
    # Compute radial field
    image_center = array(size) / 2.
    patch_radii = norm((centers - image_center) / image_center, axis=1)
    displaced_radii_red = norm((centers - displacements[:,0] - image_center) / image_center, axis=1)
    displaced_radii_blue = norm((centers - displacements[:,1] - image_center) / image_center, axis=1)
    # Compute coefficients
    regressor_red = RANSACRegressor(base_estimator=LinearRegression(fit_intercept=False))
    regressor_blue = RANSACRegressor(base_estimator=LinearRegression(fit_intercept=False))
    X = stack_array([patch_radii ** i for i in range(1, order + 2)], axis=1)
    regressor_red.fit(X, displaced_radii_red)
    regressor_blue.fit(X, displaced_radii_blue)
    coefficients = stack_array([regressor_red.estimator_.coef_, regressor_blue.estimator_.coef_], axis=0)
    return coefficients