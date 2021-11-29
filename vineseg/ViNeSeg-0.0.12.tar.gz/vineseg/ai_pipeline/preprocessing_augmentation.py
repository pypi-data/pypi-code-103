import numpy as np
import monai
from monai.transforms import ( AddChanneld
                             , RandRotate90d
                             , ScaleIntensityd
                             , ToTensord
                             , ScaleIntensityRanged
                             , RandFlipd
                             , RandRotate90d
                             , RandSpatialCropd
                             , RandZoomd
                             , Rand2DElasticd
                             , RandAffined
                             , LabelToContourd
                             , ToNumpy
                             , CastToType
                             , RandGaussianNoised
                             )
keys = ["img", "seg"]

                                        
def preprocessing( list_steps):
    preprocessing_list = []
    for step in list_steps:
        if step == "ScaleIntensity":
            preprocessing_list.append(ScaleIntensityd(keys = keys))
    return preprocessing_list

def augmentation(list_steps, size, aug_prob):
    zoom_mode = monai.utils.enums.InterpolateMode.NEAREST
    elast_mode = monai.utils.enums.GridSampleMode.BILINEAR, monai.utils.enums.GridSampleMode.NEAREST
    augmentation_list = []
    for step in list_steps:
        if step == "GaussianNoise":
            augmentation_list.append(RandGaussianNoised(keys = ["img"], prob = aug_prob, mean = 0.0, std = 0.1))
        if step == "SpatialCrop":
            augmentation_list.append(RandSpatialCropd(keys = keys, roi_size = (size, size), random_center = True, random_size=False))
        if step == "Rotate":
            augmentation_list.append(RandRotate90d(keys = keys, prob = aug_prob))
        if step == "Flip":
            augmentation_list.append(RandFlipd(keys = keys, prob = aug_prob))
        if step == "Zoom":
            augmentation_list.append(RandZoomd(keys = keys, prob = aug_prob, mode = zoom_mode))
        if step == "ElasticDeformation":
            augmentation_list.append(Rand2DElasticd(keys = keys, prob = aug_prob, spacing = 10, magnitude_range = (-2, 2), mode = elast_mode))
        if step == "AffineTransformation":
            augmentation_list.append(RandAffined(keys = keys, prob = aug_prob, rotate_range = 1, translate_range = 16, mode = elast_mode))
    return augmentation_list

def convert_to_tensor():
    list_tensor = [ ToTensord(keys=keys)
                  ]
    return list_tensor