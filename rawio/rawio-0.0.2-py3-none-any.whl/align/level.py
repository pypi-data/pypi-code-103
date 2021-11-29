# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from cv2 import getRotationMatrix2D, warpPerspective
from lsd import line_segment_detector
from numpy import abs, array, asarray, arctan2, pi, rad2deg, vstack, zeros_like
from PIL import Image
from sklearn.linear_model import RANSACRegressor

from .constrain import constrain_crop_transform

def align_level (image: Image.Image, constrain_crop: bool=True, max_theta: float=4., max_trials: int=2000) -> Image.Image:
    """
    Level an image.

    Parameters:
        image (PIL.Image): Input image.
        constrain_crop (bool): Apply a constrain crop to remove borders.
        max_theta (float): Maximum angle that can be corrected in degrees.
        max_trials (int): Maximum trials for fitting geometry model.

    Returns:
        PIL.Image: Result image.
    """
    # Extract lines
    scale = 1200. / image.width
    min_length = image.width * 0.05
    image_arr = asarray(image)
    lines = line_segment_detector(image_arr, scale=scale, angle_tolerance=18.)
    lines = lines[lines[:,6] > min_length,:4]
    # Get vertical lines
    MAX_ANGLE = 12.
    lines_t = rad2deg(arctan2(lines[:,3] - lines[:,1], lines[:,2] - lines[:,0]) % pi) - 90.
    vertical_mask = abs(lines_t) < MAX_ANGLE
    # Get line intersection points with image midpoint
    mid_line = array([ 0., image.height / 2., image.width, image.height / 2. ])[None,:]
    d_a = lines[:,2:4] - lines[:,0:2]
    d_b = mid_line[:,2:4] - mid_line[:,0:2]
    d_p = lines[:,0:2] - mid_line[:,0:2]
    d_a_perp = zeros_like(d_a)
    d_a_perp[:,0] = -d_a[:,1]
    d_a_perp[:,1] = d_a[:,0]
    projection = (d_a_perp * d_p).sum(axis=1) / (d_a_perp * d_b).sum(axis=1)
    intersection = projection[:,None] * d_b + mid_line[:,0:2]
    lines_x = 2. * intersection[:,0] / image.width - 1.        
    # Regress with RANSAC
    ransac = RANSACRegressor(max_trials=max_trials, random_state=0) # We need to suppress stochasticity
    try:
        ransac.fit(lines_x[vertical_mask].reshape(-1, 1), lines_t[vertical_mask])
    except ValueError:
        print("Failed to fit lines to level image")
        return image
    # Compute rotation
    image_center = (image.width // 2, image.height // 2)
    correction_angle = ransac.estimator_.intercept_
    H = getRotationMatrix2D(image_center, correction_angle, 1.)
    # Check theta
    if correction_angle > max_theta:
        return image
    # Rotate and constrain crop
    T = constrain_crop_transform(H, image.width, image.height)
    H = vstack([H, [0., 0., 1.]])
    H = T @ H if constrain_crop else H
    result = warpPerspective(image_arr, H, image.size)
    # Return
    result = Image.fromarray(result)
    result.info["exif"] = image.info.get("exif")
    return result