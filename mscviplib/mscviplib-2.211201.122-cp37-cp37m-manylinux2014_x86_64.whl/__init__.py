import os
import os.path as path
import sys
import numpy as np

from PIL import Image
from ._mscviplib import *


# Runner.SetPackageInstallDir(path.dirname(_mscviplib.__file__))
cvipl.set_package_install_dir(path.dirname(_mscviplib.__file__))


def test():
    from  mscviplib.test.Test_ResizeImage import Test_ResizeImage as Test_ResizeImage
    test = Test_ResizeImage()
    test_result = test.run()

    if len(test_result.failures) < 1:
      print("Passed!!!") 
    else:
      print("FAILED!!!")
      sys.exit(1)


def from_pil(img):
    """Get mscviplib.ImageMetadataByte and image buffer from a PIL.Image object.
       call as meta, buffer = mscviplib.get_cvipl_image(img)
    Args:
        image: PIL image object. 

    Returns:
        (ImageMetadataByte, bytep[] buffer).
    """
    numChannels = len(img.mode)
    imgMeta = ImageMetadataByte()
    imgMeta.Height = img.height
    imgMeta.Width = img.width
    imgMeta.Channels = numChannels
    # TASK 8850730: CVIPL: metadata color space says RGB, but internal opencv implementation is BRG - need to fix it across CVIPL
    imgMeta.ColorSpace = ColorSpace.RGB
    stride = imgMeta.Width * numChannels
    stride = (stride + 3) & (-4)  # four byte alignment
    imgMeta.Stride = stride
    # note that we convert to BGR intentionally: OpenCV internal format is BGR
    imgBuffer = img.tobytes('raw', 'BGR', imgMeta.Stride)
    return imgMeta, imgBuffer

def to_pil(meta, buffer, means, std):
    """Create PIL image out of cvipl float buffer.
       NOTE: this is a test-only function. Do not use it in the production code. Need optimized C++
    Args:
        meta: mscviplib.ImageMetadata
        buffer: float (C, H, W) ndarray
        means: float[3] mean values
        std: float[3] std values
        image: PIL image object. 

    Returns:
        PIL image
    """
    assert_msg = 'buffer shall be a 3xHxW float ndarray'
    assert isinstance(buffer, np.ndarray), assert_msg
    assert len(buffer.shape) == 3, assert_msg
    assert buffer.shape[0] == 3, assert_msg

    h = buffer.shape[1]
    w = buffer.shape[2]
    rgb = np.zeros((h,w,3), dtype = np.uint8)

    rgb[:,:,0] = np.clip(255 * (buffer[0,:,:] * std[0] + means[0]), 0, 255).astype(np.uint8)
    rgb[:,:,1] = np.clip(255 * (buffer[1,:,:] * std[1] + means[1]), 0, 255).astype(np.uint8)
    rgb[:,:,2] = np.clip(255 * (buffer[2,:,:] * std[2] + means[2]), 0, 255).astype(np.uint8)

    img = Image.fromarray(rgb, 'RGB')
    return img


# def get_image_data(image):
#     """Get mscviplib.ImageMetadataByte from a PIL.Image object.
  
#     Args:
#         image: PIL image object. 
  
#     Returns:
#         ImageMetadataByte object.
#     """
#     numChannels = len(image.mode)
#     image_metadata = ImageMetadataByte()
#     image_metadata.Height = image.height
#     image_metadata.Width = image.width
#     image_metadata.Channels = numChannels
#     image_metadata.ColorSpace = ColorSpace.RGB
#     image_metadata.Stride = image_metadata.Width * numChannels
#     return image_metadata
