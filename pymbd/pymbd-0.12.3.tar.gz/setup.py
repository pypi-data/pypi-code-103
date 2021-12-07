# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pymbd']

package_data = \
{'': ['*']}

install_requires = \
['cffi>=1,<2', 'numpy>=1,<2', 'scipy>=1,<2']

extras_require = \
{'mpi': ['mpi4py>=3,<4'], 'test': ['pytest>=5,<6']}

setup_kwargs = {
    'name': 'pymbd',
    'version': '0.12.3',
    'description': 'Many-body dispersion library',
    'long_description': "# Libmbd\n\n![checks](https://img.shields.io/github/checks-status/libmbd/libmbd/master.svg)\n[![coverage](https://img.shields.io/codecov/c/github/libmbd/libmbd.svg)](https://codecov.io/gh/libmbd/libmbd)\n![python](https://img.shields.io/pypi/pyversions/pymbd.svg)\n[![conda](https://img.shields.io/conda/vn/conda-forge/libmbd.svg)](https://anaconda.org/conda-forge/libmbd)\n[![pypi](https://img.shields.io/pypi/v/pymbd.svg)](https://pypi.org/project/pymbd/)\n[![commits since](https://img.shields.io/github/commits-since/libmbd/libmbd/latest.svg)](https://github.com/libmbd/libmbd/releases)\n[![last commit](https://img.shields.io/github/last-commit/libmbd/libmbd.svg)](https://github.com/libmbd/libmbd/commits/master)\n[![license](https://img.shields.io/github/license/libmbd/libmbd.svg)](https://github.com/libmbd/libmbd/blob/master/LICENSE)\n[![code style](https://img.shields.io/badge/code%20style-black-202020.svg)](https://github.com/ambv/black)\n[![chat](https://img.shields.io/gitter/room/libmbd/community)](https://gitter.im/libmbd/community)\n[![doi](https://img.shields.io/badge/doi-10%2Fg67f-blue)](http://doi.org/g67f)\n\nLibmbd implements the [many-body dispersion](http://dx.doi.org/10.1063/1.4865104) (MBD) method in several programming languages and frameworks:\n\n- The Fortran implementation is the reference, most advanced implementation, with support for analytical gradients and distributed parallelism, and additional functionality beyond the MBD method itself. It provides a low-level and a high-level Fortran API, as well as a C API. Furthermore, Python bindings to the C API are provided.\n- The Python/Numpy implementation is intended for prototyping, and as a high-level language reference.\n- The Python/Tensorflow implementation is an experiment that should enable rapid prototyping of machine learning applications with MBD.\n\nThe Python-based implementations as well as Python bindings to the Libmbd C API are accessible from the Python package called Pymbd.\n\nLibmbd is included in [FHI-aims](https://aimsclub.fhi-berlin.mpg.de), [Quantum Espresso](https://www.quantum-espresso.org), [DFTB+](https://dftbplus.org), and [ESL Bundle](https://esl.cecam.org/bundle/).\n\n## Installing\n\n**TL;DR** Install prebuilt Libmbd binaries via [Conda-forge](https://conda-forge.org) and Pymbd with [Pip](https://pip.pypa.io/en/stable/quickstart/).\n\n```\nconda install -c conda-forge libmbd\npip install pymbd\n```\n\nOne can also install the ScaLAPACK/MPI version.\n\n```\nconda install -c conda-forge 'libmbd=*=mpi_*' mpi4py\npip install pymbd[mpi]\n```\n\nVerify installation with\n\n```\n$ python -m pymbd\nExpected energy:   -0.0002462647623815428\nCalculated energy: -0.0002462647623817456\n```\n\n###  Libmbd\n\nLibmbd uses CMake for compiling and installing, and requires a Fortran compiler, LAPACK, and optionally ScaLAPACK/MPI.\n\nOn Ubuntu:\n\n```bash\napt-get install gfortran libblas-dev liblapack-dev [mpi-default-dev mpi-default-bin libscalapack-mpi-dev]\n```\n\nOn macOS:\n\n```bash\nbrew install gcc [open-mpi scalapack]\n```\n\nThe compiling and installation can then proceed with\n\n```\nmkdir build && cd build\ncmake .. [-DENABLE_SCALAPACK_MPI=ON]\nmake\nmake install\n[make test]\n```\n\nThis installs the Libmbd shared library, C API header file,  high-level Fortran API module file, and Cmake package files, and optionally runs tests.\n\n### Pymbd\n\nPymbd can be installed and updated using [Pip](https://pip.pypa.io/en/stable/quickstart/), but requires installed Libmbd as a dependency (see above).\n\n```\npip install pymbd\n```\n\nTo support Libmbd built with ScaLAPACK/MPI, the `mpi` extras is required, which installs `mpi4py` as an extra dependency. In this case one has to make sure that `mpi4py` is linked against the same MPI library as Libmbd (for instance by compiling both manually, or installing both via Conda-forge).\n\n```\npip install pymbd[mpi]\n```\n\nIf Libmbd is installed in a non-standard location, you can point Pymbd to it with\n\n```\nenv LIBMBD_PREFIX=<path to Libmbd install prefix> pip install pymbd\n```\n\nIf you don’t need the Fortran bindings in Pymbd, you can install it without the C extension, in which case `pymbd.fortran` becomes unimportable:\n\n```\nenv LIBMBD_PREFIX= pip install pymbd\n```\n\n\n## Examples\n\n```python\nfrom pymbd import mbd_energy_species\nfrom pymbd.fortran import MBDGeom\n\n# pure Python implementation\nenergy = mbd_energy_species([(0, 0, 0), (0, 0, 7.5)], ['Ar', 'Ar'], [1, 1], 0.83)\n# Fortran implementation\nenergy = MBDGeom([(0, 0, 0), (0, 0, 7.5)]).mbd_energy_species(\n    ['Ar', 'Ar'], [1, 1], 0.83\n)\n```\n\n```fortran\nuse mbd, only: mbd_input_t, mbd_calc_t\n\ntype(mbd_input_t) :: inp\ntype(mbd_calc_t) :: calc\nreal(8) :: energy, gradients(3, 2)\ninteger :: code\ncharacter(200) :: origin, msg\n\ninp%atom_types = ['Ar', 'Ar']\ninp%coords = reshape([0d0, 0d0, 0d0, 0d0, 0d0, 7.5d0], [3, 2])\ninp%xc = 'pbe'\ncall calc%init(inp)\ncall calc%get_exception(code, origin, msg)\nif (code > 0) then\n    print *, msg\n    stop 1\nend if\ncall calc%update_vdw_params_from_ratios([0.98d0, 0.98d0])\ncall calc%evaluate_vdw_method(energy)\ncall calc%get_gradients(gradients)\ncall calc%destroy()\n```\n\n## Links\n\n- Libmbd documentation: https://libmbd.github.io\n- Pymbd documentation: https://libmbd.github.io/pymbd\n\n## Developing\n\nFor development, a top-level `Makefile` is included, which configures and compiles Libmbd, compiles the Pymbd C extension, and runs both Libmbd and Pymbd tests.\n\n```\ngit clone https://github.com/libmbd/libmbd.git && cd libmbd\npython3 -m venv venv && source venv/bin/activate\nmake\n# development work...\nmake\n```\n",
    'author': 'Jan Hermann',
    'author_email': 'dev@jan.hermann.name',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/libmbd/libmbd',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<3.10',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
