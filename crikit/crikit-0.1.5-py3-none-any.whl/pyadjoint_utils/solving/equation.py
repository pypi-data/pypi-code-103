from ..reduced_function import ReducedFunction
from pyadjoint.enlisting import Enlist
from functools import partial


def _default_apply_bc(bc, u):
    if hasattr(u, "vector"):
        bc.apply(u.vector())
    else:
        bc.apply(u)
    return u


def _is_valid_bc(bc):
    return hasattr(bc, "apply")


class ReducedEquation(object):
    """A class that encapsulates all the information required to formulate a
    reduced equation solve problem."""

    """
        reduced_function: a ReducedFunction that calculates the residual as a function of x.
        bcs: a function or list of functions that apply boundary conditions.
        h_bcs: a function or list of functions that apply homogenenous boundary conditions.
    """

    def __init__(self, reduced_function, bcs=None, h_bcs=None):
        bcs = [] if bcs is None else Enlist(bcs)
        h_bcs = [] if h_bcs is None else Enlist(h_bcs)

        bcs, h_bcs = self._validate_arguments(reduced_function, bcs, h_bcs)

        self.reduced_function = reduced_function
        self.bcs = bcs
        self.h_bcs = h_bcs

    def _validate_arguments(self, reduced_function, bcs, h_bcs):

        if not isinstance(reduced_function, ReducedFunction):
            raise TypeError("reduced_function should be a ReducedFunction")

        for i, bc in enumerate(bcs):
            if not callable(bc):
                if not _is_valid_bc(bc):
                    raise TypeError("Boundary conditions must have an 'apply' method!")
                else:
                    bcs[i] = partial(_default_apply_bc, bc)

        for i, h_bc in enumerate(h_bcs):
            if not callable(bc):
                if not _is_valid_bc(h_bc):
                    raise TypeError(
                        "Homogenized boundary conditions must have an 'apply' method!"
                    )
                else:
                    h_bcs[i] = partial(_default_apply_bc, h_bc)

        return bcs, h_bcs
