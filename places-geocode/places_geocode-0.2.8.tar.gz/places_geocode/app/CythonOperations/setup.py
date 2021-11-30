from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("../../dprk/*.pyx")
)
# setup(ext_modules=cythonize("coordinate_conv_package.pyx"))