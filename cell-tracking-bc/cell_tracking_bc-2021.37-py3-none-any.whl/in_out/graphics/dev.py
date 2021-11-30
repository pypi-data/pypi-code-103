# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from typing import Sequence

import matplotlib.pyplot as pypl
import numpy as nmpy


array_t = nmpy.ndarray


def MatShow(
    *arrays: Sequence[array_t],
    axes_titles: Sequence[str] = None,
    figure_title: str = None,
    should_run_event_loop: bool = True,
    **kwargs
) -> None:
    """"""
    n_arrays = arrays.__len__()
    if axes_titles is None:
        axes_titles = n_arrays * [None]

    figure, all_axes = pypl.subplots(ncols=n_arrays)
    for axes, array, title in zip(all_axes, arrays, axes_titles):
        axes.matshow(array, cmap="gray", **kwargs)
        if title is not None:
            axes.set_title(title)

    if figure_title is not None:
        figure.suptitle(figure_title)
    figure.tight_layout()

    if should_run_event_loop:
        pypl.show()
