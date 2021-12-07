from setuptools import setup
from Cython.Build import cythonize
import numpy as np

# setup(
#     ext_modules=cythonize("mapping_cy.pyx"),
#     include_dirs=[np.get_include()],
# )
setup(
    ext_modules=cythonize(
        ["planning.pyx", "mapping.pyx"],
        language_level=3,
        language="c++",
        compiler_directives={'linetrace': True},
    ),
    include_dirs=[np.get_include()],
)

setup_kwargs.update({
            'ext_modules': cythonize(
                extensions,
                language_level=3,
                language='c++',
                compiler_directives={'linetrace': True},
            ),
            'cmdclass': {'build_ext': build_ext},
            'include_dirs': np.get_include()
        })