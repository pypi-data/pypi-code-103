from setuptools import setup, find_packages
 
setup(
    name                = 'ingradient_lib_temp',
    version             = '0.6.161',
    description         = 'Medical Deep Learning Framework.',
    author              = 'seungyeob.seon',
    author_email        = 'liamseon@gmail.com',
    url                 = 'https://github.com/InGradient/InGradient_AI_Library',
    license             = 'MIT',
    install_requires    =  ['SimpleITK', 'revlib', 'connected-components-3d', 'nibabel'],
    py_modules          = ['data_augmentation', 'dataloads', 'deep_supervision_loss', 'get_imbalance_weight'
                          ,'inference', 'patch_transform', 'preprocessing', 'model', 'visualization', 'sampling'
                          ,'preprocessing', 'trainer', 'transform', 'data_organizer', 'get_nnunet_setting', 'optimizer', 'active_contour_loss'
                          ,'medical_decathlon_organizer', 'nnunet_3D_run', 'maic', 'unet', 'lr_scheduler', 'loss'],
    keywords            = ['pypi deploy'],
    packages            = ['ingradient_library'],
    zip_safe            = False
)
