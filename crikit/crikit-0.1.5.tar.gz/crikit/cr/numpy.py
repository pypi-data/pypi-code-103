from .types import Space, PointMap
from .space_builders import DirectSum
import numpy as np
from jax import numpy as jnp
from jax.interpreters.xla import DeviceArray


class Ndarrays(Space):
    """This class represents a Space of NumPy arrays of a given shape and
    optionally a specific data type.

    Negative numbers can be used in the shape to indicate that the length of
    that dimension doesn't matter as long as that dimension exists. For example,
    if the given shape is (-1, 2, 5), then arrays with shapes (4, 2, 5) and (1, 2, 5)
    are both points in the space, but (2, 5) is not.

        >>> import numpy as np
        >>> from crikit.cr.numpy import Ndarrays
        >>> space = Ndarrays((-1, 2, 5))
        >>> space.is_point(np.zeros((4, 2, 5)))
        True
        >>> space.is_point(np.zeros((1, 2, 5)))
        True
        >>> space.is_point(np.zeros((2, 5)))
        False

    Args:
        shape (tuple or list): The shape of the arrays.
        dtype (numpy.dtype): A NumPy datatype that further constrains the Space.
            If None, Ndarrays space will not have a specific type.
    """

    def __init__(self, shape, dtype=None):
        self._shape = shape
        self._dtype = dtype
        self._indefinite_axes = np.array(shape) < 0
        self._definite_axes = np.logical_not(self._indefinite_axes)
        self._definite_shape = np.asarray(shape)[self._definite_axes]

    def shape(self):
        return self._shape

    def is_point(self, point):
        """Returns true if the given point is an ndarray and its shape and dtype
        match those of the space.
        """
        if not isinstance(point, (np.ndarray, jnp.ndarray, DeviceArray)):
            return False
        if len(point.shape) != len(self._shape):
            return False
        # Make sure that the shapes are the same along each definite axis
        point_definite_shape = np.asarray(point.shape)[self._definite_axes]
        return np.array_equal(point_definite_shape, self._definite_shape) and (
            self._dtype is None or point.dtype == self._dtype
        )

    def point(self, **kwargs):
        shape = self._shape
        if "near" in kwargs:
            near = kwargs["near"]
            assert self.is_point(near)
            shape = near.shape
        return np.zeros(shape)

    def __eq__(self, other):
        return (
            isinstance(other, Ndarrays)
            and self._shape == other._shape
            and self._dtype == other._dtype
        )

    def __repr__(self):
        if self._dtype is None:
            return f"Ndarrays({self._shape})"
        return f"Ndarrays({self._shape}, dtype={self._dtype})"


class CR_P_LaplacianNumpy(PointMap):
    def __init__(self, p=2, dim=2, input_u=True):
        self._p = p
        self._input_u = input_u
        np_vec_space = Ndarrays((-1, dim))

        if self._input_u:
            np_scalar_space = Ndarrays((-1,))
            source = DirectSum(np_scalar_space, np_vec_space)
        else:
            source = np_vec_space
        super(CR_P_LaplacianNumpy, self).__init__(source, np_vec_space)

    def __call__(self, args, **kwargs):
        if self._input_u:
            gradu = args[1]
        else:
            gradu = args

        mu = (np.sum(gradu * gradu, axis=1) + 1e-12) ** ((self._p - 2) / 2)
        mu = mu[:, None]
        out = mu * gradu

        return out

    def setParams(self, p):
        self._p = p
