# Copyright © 2020 Greg Tucker <greg.tucker@stfc.ac.uk>
#
# This file is part of brille.
#
# brille is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# brille is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with brille. If not, see <https://www.gnu.org/licenses/>.

"""Python module :py:mod:`brille`
=================================

This module provides access to the C++ brille library which can be used to
interact with spacegroup and pointgroup symmetry operations, to determine the
first Brillouin zone for a given real space crystallographic lattice, to
find *an* irreducible polyhedron from the first Brillouin zone and the
pointgroup operations of a spacegroup, to construct polyhedron-filling connected
point networks, and to perform linear-interpolation of user-provided data for
any reciprocal space point at a symmetry-equivalent position within the
connected point network.

.. currentmodule:: brille

.. autosummary::
    :toctree: _generate
"""


""""""  # start delvewheel patch
def _delvewheel_init_patch_0_0_15():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'brille.libs'))
    if sys.version_info[:2] >= (3, 8):
        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            # backup the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            conda_dll_search_modification_enable = os.environ.get("CONDA_DLL_SEARCH_MODIFICATION_ENABLE")
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE']='1'

        os.add_dll_directory(libs_dir)

        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            # restore the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            if conda_dll_search_modification_enable is None:
                os.environ.pop("CONDA_DLL_SEARCH_MODIFICATION_ENABLE", None)
            else:
                os.environ["CONDA_DLL_SEARCH_MODIFICATION_ENABLE"] = conda_dll_search_modification_enable
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-brille-0.5.7')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_15()
del _delvewheel_init_patch_0_0_15
# end delvewheel patch



try:
    from ._brille import *
except ImportError:
    # In build / tests, _brille might be in another folder on path
    from _brille import *

from . import utils

try:
    from . import plotting
except ModuleNotFoundError:
    # Build servers don't have Matplotlib installed; plotting not tested
    pass