# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from numpy import allclose, array
from pathlib import Path
from PIL import Image
from pkg_resources import resource_filename
from rawpy import imread, DemosaicAlgorithm, HighlightMode, Params
from rawpy.enhance import find_bad_pixels, repair_bad_pixels
from torch import cat, stack
from torchvision.transforms import ToTensor, ToPILImage

from .lut import color_sample_1d, lutread
from .metadata import exifread, exifwrite

def rawread (*image_paths: str) -> Image.Image:
    """
    Load one or more RAW images.

    Parameters:
        image_paths (str | list): Path(s) to image to be loaded.

    Returns:
        PIL.Image | list: Loaded image(s).
    """
    # Check
    if len(image_paths) == 0:
        return None
    # Find bad pixels
    bad_pixels = find_bad_pixels(image_paths)
    # Load
    exposures, metadatas = [], []
    for image_path in image_paths:
        with imread(image_path) as raw:
            # Repair bad pixels
            repair_bad_pixels(raw, bad_pixels, method="median")
            # Compute saturation level
            white_level = array(raw.camera_white_level_per_channel).min()
            saturation_level = raw.white_level if white_level == 0 else white_level
            # Demosaic
            params = Params(
                demosaic_algorithm=DemosaicAlgorithm.AHD,
                use_camera_wb=True,
                no_auto_bright=True,
                user_sat=saturation_level,
                output_bps=8,
                highlight_mode=HighlightMode.Clip,
                gamma=(1, 1)
            )
            rgb = raw.postprocess(params=params)
            exposure = Image.fromarray(rgb)
            exposures.append(exposure)
            # Load metadata
            metadata = exifread(image_path)
            metadatas.append(metadata)
    # Tensorize
    exposures = [ToTensor()(exposure) for exposure in exposures]
    exposure_stack = stack(exposures, dim=0)
    # Chromaticity noise reduction # CHECK # Range [-1., 1.]
    # yuv = rgb_to_yuv(exposure_stack)
    # y, u, v = yuv.split(1, dim=1)
    # u = bilateral_filter_2d(u, (3, 5), grid_size=(8, 1024, 1024))
    # v = bilateral_filter_2d(v, (3, 5), grid_size=(8, 1024, 1024))
    # yuv = cat([y, u, v], dim=1)
    # exposure_stack = yuv_to_rgb(yuv)
    # Gamma correction # CHECK # Range [0., 1.]
    exposure_stack = 2. * exposure_stack.pow(1. / 2.2) - 1.
    # Tone curve
    tone_curve_path = resource_filename("rawio.raw", "data/raw_standard_med.tif")
    tone_curve = lutread(tone_curve_path)
    exposure_stack = color_sample_1d(exposure_stack, tone_curve)
    exposure_stack = (exposure_stack + 1.) / 2.
    # Convert back to PIL
    exposure_stack = exposure_stack.cpu()
    exposures = exposure_stack.split(1, dim=0)
    exposures = [ToPILImage()(exposure.squeeze(dim=0)) for exposure in exposures]
    # Add EXIF metadata
    exposures = [exifwrite(exposure, metadata) for exposure, metadata in zip(exposures, metadatas)]
    return exposures if len(exposures) > 1 else exposures[0]