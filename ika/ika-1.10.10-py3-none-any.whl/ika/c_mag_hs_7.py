from ika.magnetic_stirrer import *
import warnings


class CMAGHS7Interface(MagneticStirrer):
    def __init__(self,
                 device_port: str,
                 save_path:Path = None,
                 datetime_format: str = None,
                 ):
        super().__init__(device_port=device_port,
                         save_path=save_path,
                         datetime_format=datetime_format,
                         )
        warnings.warn(
            'use ika.magnetic_stirrer.MagneticStirrer instead',
            DeprecationWarning,
            stacklevel=2,
        )



class MockCMAGHS7Interface(MockMagneticStirrer):
    def __init__(self):
        super().__init__()
        warnings.warn(
            'use ika.magnetic_stirrer.MockMagneticStirrer instead',
            DeprecationWarning,
            stacklevel=2,
        )