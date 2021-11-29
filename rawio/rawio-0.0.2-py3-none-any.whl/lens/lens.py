# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from lensfunpy import Database, Modifier
from PIL import Image
from torch import from_numpy, Tensor
from torch.nn.functional import grid_sample

def lens_grid (metadata: dict, width: int, height: int) -> Tensor:
    """
    Compute lens correction sample grid.

    This method will return `None` if the grid cannot be computed.

    Parameters:
        metadata (dict): Input image metadata dictionary containing camera and lens data tags.
        width (int): Grid width.
        height (int): Grid height.
        
    Returns:
        Tensor: Sample grid with shape (1,H,W,2).
    """
    # EXIF tags
    CAMERA_MAKER_EXIF_TAG = 271
    CAMERA_MODEL_EXIF_TAG = 272
    LENS_MAKER_EXIF_TAG = 42035
    LENS_MODEL_EXIF_TAG = 42036
    FOCAL_LENGTH_EXIF_TAG = 37386
    F_NUMBER_EXIF_TAG = 33437
    # Get tags
    camera_maker, camera_model = metadata.get(CAMERA_MAKER_EXIF_TAG), metadata.get(CAMERA_MODEL_EXIF_TAG)
    lens_maker, lens_model = metadata.get(LENS_MAKER_EXIF_TAG), metadata.get(LENS_MODEL_EXIF_TAG)
    # Check
    if not all([camera_maker, camera_model, lens_model]):
        return None
    # Find model
    database = Database()
    cameras = database.find_cameras(camera_maker, camera_model)
    if len(cameras) == 0:
        return None
    lenses = database.find_lenses(cameras[0], lens_maker, lens_model)
    if len(lenses) == 0:
        return None
    # Get focal length and f number
    focal_length = metadata.get(FOCAL_LENGTH_EXIF_TAG, 20)
    f_number = metadata.get(F_NUMBER_EXIF_TAG, 8)
    focal_length = focal_length[0] / focal_length[1] if isinstance(focal_length, tuple) else focal_length
    f_number = f_number[0] / f_number[1] if isinstance(f_number, tuple) else f_number
    # Create modifier
    modifier = Modifier(lenses[0], cameras[0].crop_factor, width, height)
    modifier.initialize(focal_length, f_number)
    # Compute sample grid
    sample_grid = modifier.apply_geometry_distortion()          # (H,W,2)
    # Normalize
    sample_grid[:,:,0] = 2. * sample_grid[:,:,0] / width - 1.
    sample_grid[:,:,1] = 2. * sample_grid[:,:,1] / height - 1.
    sample_grid = from_numpy(sample_grid).unsqueeze(dim=0)      # (1,H,W,2)
    return sample_grid

def lens_correction (input: Tensor, grid: Tensor) -> Tensor:
    """
    Appply lens distortion correction to an image.

    Parameters:
        input (Tensor): Input image with shape (N,C,H,W).
        grid (Tensor): Sample grid with shape (N,H,W,2) in range [-1., 1.].

    Returns:
        Tensor: Corrected image with shape (N,C,H,W).
    """
    grid = grid.to(input.device)
    result = grid_sample(input, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
    return result