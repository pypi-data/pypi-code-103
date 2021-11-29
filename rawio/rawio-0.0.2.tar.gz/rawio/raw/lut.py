# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from imageio import imread
from torch import stack, zeros_like, Tensor
from torch.nn.functional import grid_sample
from torchvision.transforms import ToTensor

def color_sample_1d (input: Tensor, lut: Tensor) -> Tensor:
    """
    Apply a 1D look-up table to an image.

    Parameters:
        input (Tensor): RGB image with shape (N,3,H,W) in range [-1., 1.].
        lut (Tensor): Lookup table with shape (L,) in range [-1., 1.].

    Returns:
        Tensor: Filtered image with shape (N,3,H,W) in range [-1., 1.].
    """
    # Create volume
    batch,_,_,_ = input.shape
    lut = lut.to(input.device)
    volume = lut.repeat(batch, 1, 1, 1)
    # Create grid
    colors = input.permute(0, 2, 3, 1)
    wg = colors.flatten(2)
    hg = zeros_like(wg)
    grid = stack([wg, hg], dim=3)
    # Sample
    result = grid_sample(volume, grid, mode="bilinear", padding_mode="border", align_corners=False)
    result = result.squeeze(dim=1).view_as(colors).permute(0, 3, 1, 2)
    return result

def lutread (path: str) -> Tensor:
    """
    Load a 1D LUT from file.

    The LUT must be encoded as a 16-bit TIFF file.

    Parameters:
        path (str): Path to LUT file.

    Returns:
        Tensor: 1D LUT with shape (L,) in range [-1., 1.].
    """
    # Load
    image = imread(path) / 65536
    lut = ToTensor()(image).float()
    # Slice
    lut = lut[0] if lut.ndim > 2 else lut
    lut = lut[lut.shape[0] // 2]
    # Scale
    lut = 2. * lut - 1.
    return lut