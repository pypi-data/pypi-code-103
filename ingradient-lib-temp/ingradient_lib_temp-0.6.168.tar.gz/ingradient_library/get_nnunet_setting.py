from ingradient_library.patch_transform import *


def get_transform_params(device):
    affine_kwargs = {'degree':[30,30,30], 'axis':[0,1,2], 'scale':[0.7, 1.4], 'use_gpu': True, 'device':device}
    noise_kwargs = {'device': device, 'prob_per_modalities': 0.5}
    blur_kwargs = {'sigma': 1.4, 'width':3, 'device':device}
    contrast_kwargs = {'contrast_range' : [0.65, 1.5], 'preserve_range' : True, 'device':device}
    gamma_kwargs = {'gamma_range': (0.5, 1.5), 'epsilon':1e-7, 'device':device, 'retain_stats':True}
    bright_kwargs = {'device':device , 'rng': [0.7, 1.3]}
    mirror_kwargs = {'x_prob':0.5, 'y_prob':0.5,'z_prob':0.5}
    affine_prob = 0.2
    noise_prob = 0.15
    blur_prob = 0.2
    contrast_prob = 0.15
    gamma_prob = 0.15
    bright_prob = 0.15
    mirror_prob = 0.5
    lowres_prob = 0.2


    affine_transform = Batch_Affine_3D(**affine_kwargs)
    noise_transform = Batch_Gaussian_Noise(**noise_kwargs)
    blur_transform = Batch_Gaussian_Blur_3D(**blur_kwargs)
    contrast_transform = Batch_Contrast(**contrast_kwargs)
    bright_transform = Batch_Brightness(**bright_kwargs)
    gamma_transform = Batch_GammaTransform(**gamma_kwargs)
    mirror_transform = Batch_Mirroring(**mirror_kwargs)
    lowres_transform = Batch_Low_Resolution()

    return [affine_transform, noise_transform, blur_transform, contrast_transform, bright_transform, gamma_transform, mirror_transform, lowres_transform], [affine_prob, noise_prob, blur_prob, contrast_prob, gamma_prob, bright_prob, mirror_prob, lowres_prob]


def get_interactive_params(device):
    affine_kwargs = {'degree':[10,10,10], 'axis':[0,1,2], 'scale':[0.75, 1.25], 'use_gpu': True, 'device':device}
    mirror_kwargs = {'x_prob':0.5, 'y_prob':0.5,'z_prob':0.5}

    affine_prob = 0.66
    mirro_prob = 0.50
    affine_transform = Batch_Affine_3D(**affine_kwargs)
    mirror_transform = Batch_Mirroring(**mirror_kwargs)

    return [affine_transform, mirror_transform], [affine_prob, mirro_prob]


def get_maic_params():
    device = None
    affine_kwargs = {'degree':[10,10,10], 'axis':[0,1,2], 'scale':[0.98, 1.02], 'use_gpu': True, 'device':device}
    noise_kwargs = {'device': device, 'prob_per_modalities': 0.5}
    blur_kwargs = {'sigma': 1.4, 'width':3, 'device':device}
    contrast_kwargs = {'contrast_range' : [0.65, 1.5], 'preserve_range' : True, 'device':device}
    gamma_kwargs = {'gamma_range': (0.5, 1.5), 'epsilon':1e-7, 'device':device, 'retain_stats':True}
    bright_kwargs = {'device':device , 'rng': [0.7, 1.3]}
    mirror_kwargs = {'x_prob':0.5, 'y_prob':0.5,'z_prob':0.5}
    affine_prob = 0.45
    noise_prob = 0.15
    blur_prob = 0.2
    contrast_prob = 0.15
    gamma_prob = 0.15
    bright_prob = 0.15
    mirror_prob = 0.5
    lowres_prob = 0.2


    affine_transform = Batch_Affine_3D(**affine_kwargs)
    noise_transform = Batch_Gaussian_Noise(**noise_kwargs)
    blur_transform = Batch_Gaussian_Blur_3D(**blur_kwargs)
    contrast_transform = Batch_Contrast(**contrast_kwargs)
    bright_transform = Batch_Brightness(**bright_kwargs)
    gamma_transform = Batch_GammaTransform(**gamma_kwargs)
    mirror_transform = Batch_Mirroring(**mirror_kwargs)
    lowres_transform = Batch_Low_Resolution()

    return [affine_transform, noise_transform, blur_transform, contrast_transform, bright_transform, gamma_transform, mirror_transform, lowres_transform], [affine_prob, noise_prob, blur_prob, contrast_prob, gamma_prob, bright_prob, mirror_prob, lowres_prob]