from setuptools import setup
from distutils.core import setup, Extension
from Cython.Build import cythonize
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

ext_modules=[
    Extension("kmer_mapper.mapper",
              ["kmer_mapper/mapper.pyx"],
              libraries=["m"],
              extra_compile_args = ["-O3", "-march=native"],
              )
      ]

setup(name='kmer_mapper',
      version='0.0.1',
      description='Kmer Mapper',
      url='http://github.com/ivargr/kmer_mapper',
      author='Ivar Grytten',
      author_email='',
      license='MIT',
      packages=["kmer_mapper"],
      zip_safe=False,
      install_requires=['numpy', 'cython', 'graph_kmer_index'],
      classifiers=[
            'Programming Language :: Python :: 3'
      ],
      entry_points={
            'console_scripts': ['kmer_mapper=kmer_mapper.command_line_interface:main']
      },
      cmdclass = {"build_ext": build_ext},
      #ext_modules = ext_modules
      include_dirs=np.get_include(),
      ext_modules=cythonize(["kmer_mapper/mapper.pyx"]),
)

"""
python3 setup.py sdist bdist_wheel
auditwheel repair --plat linux_x86_64 dist/*.whl
mv wheelhouse/* dist
"""