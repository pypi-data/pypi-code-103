import os
import SimpleITK as sitk

def read_dcm_series(dcm_dir):
    """
    Args:
        dcm_dir: String. Path to dicom series directory
    Returns:
        sitk_image: SimpleITK object of 3D CT volume.
    """
    reader = sitk.ImageSeriesReader()
    series_file_names = reader.GetGDCMSeriesFileNames(dcm_dir)
    reader.SetFileNames(series_file_names)
    sitk_image = reader.Execute()

    return sitk_image


def load_image(path):
    """
    Args:
        path: String. Path to the .nii(.gz) file or dicom series directory
    Returns:
        image: Numpy array. The 3D CT volume.
    """
    if os.path.isdir(path):
        sitk_image = read_dcm_series(path)
    else:
        sitk_image = sitk.ReadImage(path)
    image = sitk.GetArrayFromImage(sitk_image)

    return image


def load_mask(path):
    """
    Args:
        path: String. Path to the .nii or .dcm mask.
    Returns:
        mask: Numpy array. The mask of tumor with the same shape of image.
    """
    sitk_mask = sitk.ReadImage(path)
    mask = sitk.GetArrayFromImage(sitk_mask)

    return mask
