from crikit.cr.types import PointMap
from pyadjoint.enlisting import Enlist
from pyadjoint.overloaded_type import create_overloaded_object, OverloadedType
from pyadjoint_utils.numpy_adjoint.autograd import overloaded_autograd
from scipy.stats import special_ortho_group
from ufl.operators import as_matrix, dot, transpose
import numpy as np
from typing import Iterable, List, Optional


class SpecialOrthoGroup:
    """This class represents the special orthogonal group, which is the group of
    arbitrary rotations without reflections.

    Args:
        dim (int): The dimension of the group, which is usually 2 or 3.
    """

    def __init__(self, dim: int):
        self.dim = dim

    def sample(self) -> OverloadedType:
        """This method returns a sample of the group."""
        return create_overloaded_object(special_ortho_group.rvs(self.dim))

    def apply(self, sample: OverloadedType, tensors: List[np.ndarray], offset=1):
        """This method applies a sample of the group to a group of tensors.

        Each tensor is assumed to be in the form of a NumPy array. The first
        axis of each array is ignored, and the transformation is applied to the
        remaining axes.

        Args:
            sample: a sample from the group.
            tensors: a tensor or list of tensors to apply the transformation to.

        Returns:
            type: returns the transformed tensor(s).

        """
        tensors = Enlist(tensors)
        transformed = [
            apply_coordinate_change(sample, T, offset=offset) for T in tensors
        ]
        return tensors.delist(transformed)


@overloaded_autograd(pointwise=(False, True))
def apply_coordinate_change(Q, T, offset=1):
    """Applies the coordinate transformation matrix Q to the tensor T."""
    shape = T.shape[offset:]
    rank = len(shape)
    covariants = range(rank)
    contravariants = ()

    einsum_args = get_einsum_args(
        rank, contravariants, covariants, Q, None, offset=offset
    )
    return np.einsum(T, *einsum_args)


def get_einsum_args(
    rank: int,
    contravariants: List[int],
    covariants: List[int],
    basis: np.ndarray,
    inv_basis: np.ndarray,
    offset: Optional[int] = 0,
):
    """Generates arguments for a NumPy's einsum function so that calling that
    function with these arguments and a tensor will perform a tensor coordinate
    transformation.

    The tensor is of the given rank, with the given covariant axes and
    contravariants axes. Each specified axis should be in the range [0, rank-1].

    If the coordinate transformation is being performed on a set of tensors
    stored together in the same NumPy array, the first axis (or first few axes)
    of the array is not part of the tensor definition. The offset argument
    specifies how many of the first axes to ignore. For example, if N tensors
    each with shape S are stored in an array of shape (N, S), the offset should
    be set to 1.

    Args:
        rank (int): the rank of the tensor to be transformed.
        contravariants (list): the axes that transform contravariantly.
        covariants (list): the axes that transform covariantly.
        basis: the coordinate basis to use for the transform.
        inv_basis: the inverse of the coordinate basis, used for the contravariant axes.
        offset(int): the first axes will be unchanged.

    Returns:
        tuple: returns a tuple of args to be used with NumPy's einsum function.

    """
    # Offset gives the number of axes that will be ignored.
    num_axes = rank + offset

    # Set the input axes as the full number of axes.
    axes = tuple(range(num_axes))
    args = [axes]

    # Apply the appropriate transformation to each axis.
    for ax in contravariants:
        args.append(inv_basis)
        args.append([ax + offset, ax + num_axes])
    for ax in covariants:
        args.append(basis)
        args.append([ax + offset, ax + num_axes])

    # The output axes are the ignored axes plus the transformed axes.
    new_axes = tuple(range(offset)) + tuple(range(num_axes, num_axes + rank))
    args.append(new_axes)

    return args


class GroupAction(PointMap):
    """This point map applies the action of a group to the given inputs.

    Args:
        group: The group that will be used to perform the action.
        space (Space): The space that the group transformations will be applied to.
        sample: a sample of the group that will be used if no sample is
            specified in the :meth:`__call__` method.
    """

    def __init__(self, group, space, sample=None):
        self.group = group
        self.sample = None
        super().__init__(space, space)

    def __call__(self, inputs, sample=None):
        """Applies the group transformation to the given inputs using the given
        group sample. If no sample is given, the default sample is used."""
        if sample is None:
            sample = self.sample
        return self.group.apply(sample, inputs)
