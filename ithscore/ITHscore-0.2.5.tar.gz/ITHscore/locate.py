import numpy as np

def get_largest_slice(img3d, mask3d):
    """
    Get the slice with largest tumor area
    Args:
        img3d: Numpy array. The whole CT volume (3D)
        mask3d: Numpy array. Same size as img3d, binary mask with tumor area set as 1, background as 0
    Returns:
        img: Numpy array. The 2D image slice with largest tumor area
        mask: Numpy array. The subset of mask in the same position of sub_img
    """
    area = np.sum(mask3d == 1, axis=(1, 2))
    area_index = np.argsort(area)[-1]
    img = img3d[area_index, :, :]
    mask = mask3d[area_index, :, :]

    return img, mask


def locate_tumor(img, mask, padding=2):
    """
    Locate and extract tumor from CT image using mask
    Args:
        img: Numpy array. The whole image
        mask: Numpy array. Same size as img, binary mask with tumor area set as 1, background as 0
        padding: Int. Number of pixels padded on each side after extracting tumor
    Returns:
        sub_img: Numpy array. The tumor area defined by mask
        sub_mask: Numpy array. The subset of mask in the same position of sub_img
    """
    top_margin = min(np.where(mask == 1)[0])
    bottom_margin = max(np.where(mask == 1)[0])
    left_margin = min(np.where(mask == 1)[1])
    right_margin = max(np.where(mask == 1)[1])
    # padding two pixels at each edges for further computation
    sub_img = img[top_margin - padding:bottom_margin + padding + 1, left_margin - padding:right_margin + padding + 1]
    sub_mask = mask[top_margin - padding:bottom_margin + padding + 1,
                    left_margin - padding:right_margin + padding + 1]

    return sub_img, sub_mask