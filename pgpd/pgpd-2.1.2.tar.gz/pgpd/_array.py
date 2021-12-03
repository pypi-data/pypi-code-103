#
# PyGEOS ExtensionDType & ExtensionArray
#
import numbers
from collections.abc import Iterable
import numpy as np
import pandas as pd
import pygeos
from pandas.api.extensions import ExtensionArray, ExtensionDtype, register_extension_dtype

try:
    from shapely.geometry.base import BaseGeometry as ShapelyGeometry
except ImportError:
    ShapelyGeometry = None

__all__ = ['GeosDtype', 'GeosArray']


@register_extension_dtype
class GeosDtype(ExtensionDtype):
    type = pygeos.lib.Geometry      #: Underlying type of the individual Array elements
    name = 'geos'                   #: Dtype string name
    na_value = pd.NA                #: NA Value that is used on the user-facing side

    @classmethod
    def construct_from_string(cls, string):
        """
        Construct this type from a string (ic. :attr:`~GeosDtype.name`).

        Args:
            string (str): The name of the type.

        Returns:
            GeosDtype: instance of the dtype.

        Raises:
            TypeError: string is not equal to "geos".
        """
        if string == cls.name:
            return cls()
        else:
            raise TypeError(f'Cannot construct a "{cls.__name__}" from "{string}"')

    @classmethod
    def construct_array_type(cls):
        """
        Return the array type associated with this dtype.

        Return:
            GeosArray: Associated ExtensionArray.
        """
        return GeosArray


class GeosArray(ExtensionArray):
    dtype = GeosDtype()     #: Dtype for this ExtensionArray
    ndim = 1                #: Number of dimensions of this ExtensionArray

    # -------------------------------------------------------------------------
    # (De-)Serialization
    # -------------------------------------------------------------------------
    def __init__(self, data):
        """
        Create a GeosArray from PyGeos data.

        Args:
            data (Iterable): PyGeos data (see Note)

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.

        Raises:
            ValueError: data is not of correct type

        Note:
            The ``data`` argument can be one of different types:

            - *GeosArray* |br|
                Shallow copy of the internal data.
            - *None or pygeos.lib.Geometry* |br|
                Wrap data in an array.
            - *Iterable of pygeos.lib.Geometry* |br|
                use ``np.asarray(data)``.
        """
        if isinstance(data, self.__class__):
            self.data = data.data
        elif data is None or isinstance(data, self.dtype.type):
            self.data = np.array((data,))
        elif isinstance(data, Iterable):
            val = next((d for d in data if d is not None), None)
            if val is None or isinstance(val, self.dtype.type):
                self.data = np.asarray(data)
            else:
                raise TypeError(f'Data should be an iterable of {self.dtype.type}')
        else:
            raise ValueError(f'Data should be an iterable of {self.dtype.type}')

        self.data[pd.isna(self.data)] = None

    @classmethod
    def from_shapely(cls, data, **kwargs):
        """
        Create a GeosArray from shapely data. |br|
        This function is a simple wrapper around :func:`pygeos.io.from_shapely`.

        Args:
            data: Shapely data or list of shapely data.
            kwargs: Keyword arguments passed to :func:`~pygeos.io.from_shapely`.

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.
        """
        data = pygeos.io.from_shapely(data, **kwargs)
        return cls(data)

    @classmethod
    def from_wkb(cls, data, **kwargs):
        """
        Create a GeosArray from WKB data. |br|
        This function is a simple wrapper around :func:`pygeos.io.from_wkb`.

        Args:
            data: WKB data or list of WKB data.
            kwargs: Keyword arguments passed to :func:`~pygeos.io.from_wkb`.

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.
        """
        data = pygeos.io.from_wkb(data, **kwargs)
        return cls(data)

    @classmethod
    def from_wkt(cls, data, **kwargs):
        """
        Create a GeosArray from WKT data. |br|
        This function is a simple wrapper around :func:`pygeos.io.from_wkt`.

        Args:
            data: WKT data or list of WKT data.
            kwargs: Keyword arguments passed to :func:`~pygeos.io.from_wkt`.

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.
        """
        data = pygeos.io.from_wkt(data, **kwargs)
        return cls(data)

    def to_shapely(self, **kwargs):
        """
        Transform the GeosArray to a NumPy array of shapely objects.

        Returns:
            numpy.ndarray: Array with the shapely data.
        """
        return pygeos.io.to_shapely(self.data, **kwargs)

    def to_wkb(self, **kwargs):
        """
        Transform the GeosArray to a NumPy array of WKB bytes. |br|
        This function is a simple wrapper around :func:`pygeos.io.to_wkb`.

        Args:
            kwargs: Keyword arguments passed to :func:`~pygeos.io.to_wkb`.

        Returns:
            numpy.ndarray: Array with the WKB data.
        """
        return pygeos.io.to_wkb(self.data, **kwargs)

    def to_wkt(self, **kwargs):
        """
        Transform the GeosArray to a NumPy array of WKT strings. |br|
        This function is a simple wrapper around :func:`pygeos.io.to_wkt`.

        Args:
            kwargs: Keyword arguments passed to :func:`~pygeos.io.to_wkt`.

        Returns:
            numpy.ndarray: Array with the WKT data.
        """
        return pygeos.io.to_wkt(self.data, **kwargs)

    # -------------------------------------------------------------------------
    # ExtensionArray Specific
    # -------------------------------------------------------------------------
    @classmethod
    def _from_sequence(cls, scalars, dtype=None, copy=False):
        if isinstance(scalars, (str, bytes)) or not isinstance(scalars, Iterable):
            scalars = (scalars,)

        values = np.array(scalars)
        if copy:
            values = values.copy()
        val = next((v for v in values if v is not None), None)

        if isinstance(val, str):
            return cls.from_wkt(values)
        elif isinstance(val, bytes):
            return cls.from_wkb(values)
        elif ShapelyGeometry is not None and isinstance(val, ShapelyGeometry):
            return cls.from_shapely(values)

        return cls(values)

    def _values_for_factorize(self):
        return self.data, None

    @classmethod
    def _from_factorized(cls, values, original):
        return cls(values)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return self.data[key]

        key = pd.api.indexers.check_array_indexer(self, key)
        if isinstance(key, (Iterable, slice)):
            return GeosArray(self.data[key])
        else:
            raise TypeError('Index type not supported', key)

    def __setitem__(self, key, value):
        key = pd.api.indexers.check_array_indexer(self, key)

        if isinstance(key, (slice, list, np.ndarray)):
            if isinstance(value, self.__class__):
                value = value.data
            else:
                value = self._from_sequence(value)

            self.data[key] = value
        else:
            if isinstance(value, Iterable):
                raise ValueError('cannot set a single element with an array')

            if pd.isna(value):
                self.data[key] = None
            elif isinstance(value, str):
                self.data[key] = pygeos.io.from_wkt(value)
            elif isinstance(value, bytes):
                self.data[key] = pygeos.io.from_wkb(value)
            elif ShapelyGeometry is not None and isinstance(value, ShapelyGeometry):
                self.data[key] = pygeos.io.from_shapely(value)
            else:
                self.data[key] = value

    def __len__(self):
        return self.data.shape[0]

    def __eq__(self, other):
        if isinstance(other, (pd.Series, pd.Index, pd.DataFrame)):
            return NotImplemented

        if isinstance(other, self.__class__):
            return self.data == other.data

        return self.data == other

    @property
    def nbytes(self):
        return self.data.nbytes

    def isna(self):
        return pygeos.is_missing(self.data)

    def take(self, indices, allow_fill=False, fill_value=None):
        from pandas.core.algorithms import take

        if allow_fill:
            if fill_value is None or pd.isna(fill_value):
                fill_value = None
            elif not isinstance(fill_value, self.dtype.type):
                raise TypeError('Provide geometry or None as fill value')

        result = take(self.data, indices, allow_fill=allow_fill, fill_value=fill_value)

        if allow_fill and fill_value is None:
            result[pd.isna(result)] = None

        return self.__class__(result)

    def copy(self, order='C'):
        return GeosArray(self.data.copy(order))

    @classmethod
    def _concat_same_type(cls, to_concat):
        data = np.concatenate([c.data for c in to_concat])
        return cls(data)

    def _values_for_argsort(self):
        """
        Return values for sorting.

        Raises:
            TypeError: Geometries are not sortable.
        """
        raise TypeError('geometries are not sortable')

    # -------------------------------------------------------------------------
    # NumPy Specific
    # -------------------------------------------------------------------------
    @property
    def size(self):
        return self.data.size

    @property
    def shape(self):
        return self.data.shape

    def __array__(self, dtype=None):
        """ Return internal NumPy array. """
        return self.data

    # -------------------------------------------------------------------------
    # Custom Methods
    # -------------------------------------------------------------------------
    def affine(self, matrix):
        r"""
        Performs a 2D or 3D affine transformation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                =
                \begin{bmatrix}
                    a & b & x_{off} \\
                    d & e & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                =
                \begin{bmatrix}
                    a & b & c & x_{off} \\
                    d & e & f & y_{off} \\
                    g & h & i & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}

        Args:
            matrix (numpy.ndarray or list-like): Affine transformation matrix.

        Returns:
            pgpd.GeosArray: Transformed geometries

        Note:
            The transformation matrix can be one of the following types:

            - numpy.ndarray <3x3 or 2x3> |br|
              Performs a 2D affine transformation, where the last row of homogeneous coordinates can optionally be discarded.
            - list-like <6> |br|
              Performs a 2D affine transformation, where the `matrix` represents **(a, b, d, e, xoff, yoff)**.
            - numpy.ndarray <4x4 or 3x4> |br|
              Performs a 3D affine transformation, where the last row of homogeneous coordinates can optionally be discarded.
            - list-like <12> |br|
              Performs a 3D affine transformation, where the `matrix` represents **(a, b, c, d, e, f, g, h, i, xoff, yoff, zoff)**.
        """
        # Get Correct Affine transformation matrix
        if isinstance(matrix, np.ndarray):
            r, c = matrix.shape
            zdim = c == 4
            if r == 2:
                matrix = np.append(matrix, [[0, 0, 1]], axis=0)
            elif c == 4 and r == 3:
                matrix = np.append(matrix, [[0, 0, 0, 1]], axis=0)
        elif len(matrix) == 6:
            zdim = False
            matrix = np.array([
                [matrix[0], matrix[1], matrix[4]],
                [matrix[2], matrix[3], matrix[5]],
                [0,         0,         1],
            ])
        elif len(matrix) == 12:
            zdim = True
            matrix = np.array([
                [matrix[0], matrix[1], matrix[2], matrix[9]],
                [matrix[3], matrix[4], matrix[5], matrix[10]],
                [matrix[6], matrix[7], matrix[8], matrix[11]],
                [0,         0,         0,         1],
            ])

        matrix = matrix[None, ...]

        # Coordinate Function
        def _affine(points):
            points = np.c_[points, np.ones(points.shape[0])][..., None]
            return (matrix @ points)[:, :-1, 0]

        return self.__class__(pygeos.coordinates.apply(self.data, _affine, zdim))

    def __add__(self, other):
        """
        Performs an addition between the coordinates array and other.

        Args:
            other (array-like): Item to add to the coordinates (max 2-dimensional).

        Note:
            When adding the coordinates array and `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we perform two checks before adding the arrays.

            Firstly, we decide whether to use the Z-dimension for the computation, depending on the shape of `other`:

            - `other.ndim >= 2 and other.shape[1] == 2`: Do not use Z-dimension.
            - `other.ndim >= 2 and other.shape[1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.

            Secondly, if `other.shape[0] == self.data.shape[0]`,
            we automatically repeat each coordinate pair to the number of coordinates of its corresponding polygon.
            This allows you to easily add different coordinate pairs to each polygon.

        Example:
            >>> import pygeos
            >>> import pgpd
            >>> data = pgpd.GeosArray(pygeos.box(range(4), 0, range(10,14), 10))
            >>> data
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
             <pygeos.Geometry POLYGON ((11 0, 11 10, 1 10, 1 0, 11 0))>,
             <pygeos.Geometry POLYGON ((12 0, 12 10, 2 10, 2 0, 12 0))>,
             <pygeos.Geometry POLYGON ((13 0, 13 10, 3 10, 3 0, 13 0))>]
            Length: 4, dtype: geos

            Providing values for each coordinate:
            >>> other = np.tile([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], 4).reshape(20, 2)
            >>> other
            array([[0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1]])
            >>> data + other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 1, 12 13, 4 15, 6 7, 10 1))>,
             <pygeos.Geometry POLYGON ((11 1, 13 13, 5 15, 7 7, 11 1))>,
             <pygeos.Geometry POLYGON ((12 1, 14 13, 6 15, 8 7, 12 1))>,
             <pygeos.Geometry POLYGON ((13 1, 15 13, 7 15, 9 7, 13 1))>]
            Length: 4, dtype: geos

            Provide coordinates for each polygon:
            >>> other = np.array([[0, 1], [2, 3], [4, 5], [6, 7]])
            >>> data + other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 1, 10 11, 0 11, 0 1, 10 1))>,
             <pygeos.Geometry POLYGON ((13 3, 13 13, 3 13, 3 3, 13 3))>,
             <pygeos.Geometry POLYGON ((16 5, 16 15, 6 15, 6 5, 16 5))>,
             <pygeos.Geometry POLYGON ((19 7, 19 17, 9 17, 9 7, 19 7))>]
            Length: 4, dtype: geos

            NumPy broadcasting still works:
            >>> # Broadcast X,Y(,Z)
            >>> other = np.array([1,2,3,4])[..., None]
            >>> other.shape
            (4, 1)
            >>> data + other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((11 1, 11 11, 1 11, 1 1, 11 1))>,
             <pygeos.Geometry POLYGON ((13 2, 13 12, 3 12, 3 2, 13 2))>,
             <pygeos.Geometry POLYGON ((15 3, 15 13, 5 13, 5 3, 15 3))>,
             <pygeos.Geometry POLYGON ((17 4, 17 14, 7 14, 7 4, 17 4))>]
            Length: 4, dtype: geos
            >>> # Broadcast coordinates
            >>> other = np.array([10,10])
            >>> other.shape
            (2,)
            >>> data + other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((20 10, 20 20, 10 20, 10 10, 20 10))>,
             <pygeos.Geometry POLYGON ((21 10, 21 20, 11 20, 11 10, 21 10))>,
             <pygeos.Geometry POLYGON ((22 10, 22 20, 12 20, 12 10, 22 10))>,
             <pygeos.Geometry POLYGON ((23 10, 23 20, 13 20, 13 10, 23 10))>]
            Length: 4, dtype: geos
        """
        other = np.asarray(other)
        if other.ndim > 2:
            raise ValueError('Other cannot have more than 2 dimensions.')

        # Check whether we use Z-dimension
        zshape = other.ndim == 2 and other.shape[1]
        if zshape == 2:
            zdim = False
        elif zshape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        # Expand other to number of coords per shape
        pshape = other.ndim >= 1 and other.shape[0]
        if pshape == self.data.shape[0]:
            other = np.repeat(other, pygeos.get_num_coordinates(self.data), 0)

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt + other,
            zdim,
        ))

    def __sub__(self, other):
        """
        Performs a subtraction between the coordinates array and other.

        Args:
            other (array-like): Item to subtract from the coordinates (max 2-dimensional).

        Note:
            When subtracting `other` from the coordinates array, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we perform two checks before adding the arrays.

            Firstly, we decide whether to use the Z-dimension for the computation, depending on the shape of `other`:

            - `other.ndim >= 2 and other.shape[1] == 2`: Do not use Z-dimension.
            - `other.ndim >= 2 and other.shape[1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.

            Secondly, if `other.shape[0] == self.data.shape[0]`,
            we automatically repeat each coordinate pair to the number of coordinates of its corresponding polygon.
            This allows you to easily add different coordinate pairs to each polygon.

        Example:
            >>> import pygeos
            >>> import pgpd
            >>> data = pgpd.GeosArray(pygeos.box(range(4), 0, range(10,14), 10))
            >>> data
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
             <pygeos.Geometry POLYGON ((11 0, 11 10, 1 10, 1 0, 11 0))>,
             <pygeos.Geometry POLYGON ((12 0, 12 10, 2 10, 2 0, 12 0))>,
             <pygeos.Geometry POLYGON ((13 0, 13 10, 3 10, 3 0, 13 0))>]
            Length: 4, dtype: geos

            Providing values for each coordinate:
            >>> other = np.tile([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], 4).reshape(20, 2)
            >>> other
            array([[0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1]])
            >>> data - other
            <GeosArray>
            [ <pygeos.Geometry POLYGON ((10 -1, 8 7, -4 5, -6 -7, 10 -1))>,
              <pygeos.Geometry POLYGON ((11 -1, 9 7, -3 5, -5 -7, 11 -1))>,
             <pygeos.Geometry POLYGON ((12 -1, 10 7, -2 5, -4 -7, 12 -1))>,
             <pygeos.Geometry POLYGON ((13 -1, 11 7, -1 5, -3 -7, 13 -1))>]
            Length: 4, dtype: geos

            Provide coordinates for each polygon:
            >>> other = np.array([[0, 1], [2, 3], [4, 5], [6, 7]])
            >>> data - other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 -1, 10 9, 0 9, 0 -1, 10 -1))>,
              <pygeos.Geometry POLYGON ((9 -3, 9 7, -1 7, -1 -3, 9 -3))>,
              <pygeos.Geometry POLYGON ((8 -5, 8 5, -2 5, -2 -5, 8 -5))>,
              <pygeos.Geometry POLYGON ((7 -7, 7 3, -3 3, -3 -7, 7 -7))>]
            Length: 4, dtype: geos

            NumPy broadcasting still works:
            >>> # Broadcast X,Y(,Z)
            >>> other = np.array([1,2,3,4])[..., None]
            >>> other.shape
            (4, 1)
            >>> data - other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((9 -1, 9 9, -1 9, -1 -1, 9 -1))>,
             <pygeos.Geometry POLYGON ((9 -2, 9 8, -1 8, -1 -2, 9 -2))>,
             <pygeos.Geometry POLYGON ((9 -3, 9 7, -1 7, -1 -3, 9 -3))>,
             <pygeos.Geometry POLYGON ((9 -4, 9 6, -1 6, -1 -4, 9 -4))>]
            Length: 4, dtype: geos
            >>> # Broadcast coordinates
            >>> other = np.array([10,10])
            >>> other.shape
            (2,)
            >>> data - other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((0 -10, 0 0, -10 0, -10 -10, 0 -10))>,
               <pygeos.Geometry POLYGON ((1 -10, 1 0, -9 0, -9 -10, 1 -10))>,
               <pygeos.Geometry POLYGON ((2 -10, 2 0, -8 0, -8 -10, 2 -10))>,
               <pygeos.Geometry POLYGON ((3 -10, 3 0, -7 0, -7 -10, 3 -10))>]
            Length: 4, dtype: geos
        """
        other = np.asarray(other)
        if other.ndim > 2:
            raise ValueError('Other cannot have more than 2 dimensions.')

        # Check whether we use Z-dimension
        zshape = other.ndim == 2 and other.shape[1]
        if zshape == 2:
            zdim = False
        elif zshape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        # Expand other to number of coords per shape
        pshape = other.ndim >= 1 and other.shape[0]
        if pshape == self.data.shape[0]:
            other = np.repeat(other, pygeos.get_num_coordinates(self.data), 0)

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt - other,
            zdim,
        ))

    def __mul__(self, other):
        """
        Performs a multiplication between the coordinates array and other.

        Args:
            other (array-like): Item to multiply with the coordinates (max 2-dimensional).

        Note:
            When multiplying the coordinates array and `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we perform two checks before adding the arrays.

            Firstly, we decide whether to use the Z-dimension for the computation, depending on the shape of `other`:

            - `other.ndim >= 2 and other.shape[1] == 2`: Do not use Z-dimension.
            - `other.ndim >= 2 and other.shape[1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.

            Secondly, if `other.shape[0] == self.data.shape[0]`,
            we automatically repeat each coordinate pair to the number of coordinates of its corresponding polygon.
            This allows you to easily add different coordinate pairs to each polygon.

        Example:
            >>> import pygeos
            >>> import pgpd
            >>> data = pgpd.GeosArray(pygeos.box(range(4), 0, range(10,14), 10))
            >>> data
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
             <pygeos.Geometry POLYGON ((11 0, 11 10, 1 10, 1 0, 11 0))>,
             <pygeos.Geometry POLYGON ((12 0, 12 10, 2 10, 2 0, 12 0))>,
             <pygeos.Geometry POLYGON ((13 0, 13 10, 3 10, 3 0, 13 0))>]
            Length: 4, dtype: geos

            Providing values for each coordinate:
            >>> other = np.tile([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], 4).reshape(20, 2)
            >>> other
            array([[0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1]])
            >>> data * other
            <GeosArray>
            [  <pygeos.Geometry POLYGON ((0 0, 20 30, 0 50, 0 0, 0 0))>,
               <pygeos.Geometry POLYGON ((0 0, 22 30, 4 50, 6 0, 0 0))>,
              <pygeos.Geometry POLYGON ((0 0, 24 30, 8 50, 12 0, 0 0))>,
             <pygeos.Geometry POLYGON ((0 0, 26 30, 12 50, 18 0, 0 0))>]
            Length: 4, dtype: geos

            Provide coordinates for each polygon:
            >>> other = np.array([[0, 1], [2, 3], [4, 5], [6, 7]])
            >>> data * other
            <GeosArray>
            [     <pygeos.Geometry POLYGON ((0 0, 0 10, 0 10, 0 0, 0 0))>,
               <pygeos.Geometry POLYGON ((22 0, 22 30, 2 30, 2 0, 22 0))>,
               <pygeos.Geometry POLYGON ((48 0, 48 50, 8 50, 8 0, 48 0))>,
             <pygeos.Geometry POLYGON ((78 0, 78 70, 18 70, 18 0, 78 0))>]
            Length: 4, dtype: geos

            NumPy broadcasting still works:
            >>> # Broadcast X,Y(,Z)
            >>> other = np.array([1,2,3,4])[..., None]
            >>> other.shape
            (4, 1)
            >>> data * other
            <GeosArray>
            [  <pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
               <pygeos.Geometry POLYGON ((22 0, 22 20, 2 20, 2 0, 22 0))>,
               <pygeos.Geometry POLYGON ((36 0, 36 30, 6 30, 6 0, 36 0))>,
             <pygeos.Geometry POLYGON ((52 0, 52 40, 12 40, 12 0, 52 0))>]
            Length: 4, dtype: geos
            >>> # Broadcast coordinates
            >>> other = np.array([10,10])
            >>> other.shape
            (2,)
            >>> data * other
            <GeosArray>
            [  <pygeos.Geometry POLYGON ((100 0, 100 100, 0 100, 0 0, 100 0))>,
             <pygeos.Geometry POLYGON ((110 0, 110 100, 10 100, 10 0, 110 0))>,
             <pygeos.Geometry POLYGON ((120 0, 120 100, 20 100, 20 0, 120 0))>,
             <pygeos.Geometry POLYGON ((130 0, 130 100, 30 100, 30 0, 130 0))>]
            Length: 4, dtype: geos
        """
        other = np.asarray(other)
        if other.ndim > 2:
            raise ValueError('Other cannot have more than 2 dimensions.')

        # Check whether we use Z-dimension
        zshape = other.ndim == 2 and other.shape[1]
        if zshape == 2:
            zdim = False
        elif zshape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        # Expand other to number of coords per shape
        pshape = other.ndim >= 1 and other.shape[0]
        if pshape == self.data.shape[0]:
            other = np.repeat(other, pygeos.get_num_coordinates(self.data), 0)

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt * other,
            zdim,
        ))

    def __truediv__(self, other):
        """
        Performs a division between the coordinates array and other.

        Args:
            other (array-like): Item to divide the coordinates with (max 2-dimensional).

        Note:
            When dividing the coordinates array by `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we perform two checks before adding the arrays.

            Firstly, we decide whether to use the Z-dimension for the computation, depending on the shape of `other`:

            - `other.ndim >= 2 and other.shape[1] == 2`: Do not use Z-dimension.
            - `other.ndim >= 2 and other.shape[1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.

            Secondly, if `other.shape[0] == self.data.shape[0]`,
            we automatically repeat each coordinate pair to the number of coordinates of its corresponding polygon.
            This allows you to easily add different coordinate pairs to each polygon.

        Example:
            >>> import pygeos
            >>> import pgpd
            >>> data = pgpd.GeosArray(pygeos.box(range(4), 0, range(10,14), 10))
            >>> data
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
             <pygeos.Geometry POLYGON ((11 0, 11 10, 1 10, 1 0, 11 0))>,
             <pygeos.Geometry POLYGON ((12 0, 12 10, 2 10, 2 0, 12 0))>,
             <pygeos.Geometry POLYGON ((13 0, 13 10, 3 10, 3 0, 13 0))>]
            Length: 4, dtype: geos

            Providing values for each coordinate:
            >>> other = np.tile([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], 4).reshape(20, 2)
            >>> other
            array([[0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1]])
            >>> data / other
            <GeosArray>
            [         <pygeos.Geometry POLYGON ((inf 0, 5 3.33, 0 2, 0 0, inf 0))>,
             <pygeos.Geometry POLYGON ((inf 0, 5.5 3.33, 0.25 2, 0.167 0, inf 0))>,
                <pygeos.Geometry POLYGON ((inf 0, 6 3.33, 0.5 2, 0.333 0, inf 0))>,
               <pygeos.Geometry POLYGON ((inf 0, 6.5 3.33, 0.75 2, 0.5 0, inf 0))>]
            Length: 4, dtype: geos

            Provide coordinates for each polygon:
            >>> other = np.array([[0, 1], [2, 3], [4, 5], [6, 7]])
            >>> data / other
            <GeosArray>
            [     <pygeos.Geometry POLYGON ((inf 0, inf 10, -nan 10, -nan 0, inf 0))>,
                <pygeos.Geometry POLYGON ((5.5 0, 5.5 3.33, 0.5 3.33, 0.5 0, 5.5 0))>,
                            <pygeos.Geometry POLYGON ((3 0, 3 2, 0.5 2, 0.5 0, 3 0))>,
             <pygeos.Geometry POLYGON ((2.17 0, 2.17 1.43, 0.5 1.43, 0.5 0, 2.17 0))>]
            Length: 4, dtype: geos

            NumPy broadcasting still works:
            >>> # Broadcast X,Y(,Z)
            >>> other = np.array([1,2,3,4])[..., None]
            >>> other.shape
            (4, 1)
            >>> data / other
            <GeosArray>
            [              <pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
                      <pygeos.Geometry POLYGON ((5.5 0, 5.5 5, 0.5 5, 0.5 0, 5.5 0))>,
                  <pygeos.Geometry POLYGON ((4 0, 4 3.33, 0.667 3.33, 0.667 0, 4 0))>,
             <pygeos.Geometry POLYGON ((3.25 0, 3.25 2.5, 0.75 2.5, 0.75 0, 3.25 0))>]
            Length: 4, dtype: geos
            >>> # Broadcast coordinates
            >>> other = np.array([10,10])
            >>> other.shape
            (2,)
            >>> data / other
            <GeosArray>
            [          <pygeos.Geometry POLYGON ((1 0, 1 1, 0 1, 0 0, 1 0))>,
             <pygeos.Geometry POLYGON ((1.1 0, 1.1 1, 0.1 1, 0.1 0, 1.1 0))>,
             <pygeos.Geometry POLYGON ((1.2 0, 1.2 1, 0.2 1, 0.2 0, 1.2 0))>,
             <pygeos.Geometry POLYGON ((1.3 0, 1.3 1, 0.3 1, 0.3 0, 1.3 0))>]
            Length: 4, dtype: geos
        """
        other = np.asarray(other)
        if other.ndim > 2:
            raise ValueError('Other cannot have more than 2 dimensions.')

        # Check whether we use Z-dimension
        zshape = other.ndim == 2 and other.shape[1]
        if zshape == 2:
            zdim = False
        elif zshape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        # Expand other to number of coords per shape
        pshape = (other.ndim >= 1 and other.shape[0])
        if pshape == self.data.shape[0]:
            other = np.repeat(other, pygeos.get_num_coordinates(self.data), 0)

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt / other,
            zdim,
        ))

    def __floordiv__(self, other):
        """
        Performs a division between the coordinates array and other.

        Args:
            other (array-like): Item to divide the coordinates with (max 2-dimensional).

        Note:
            When dividing the coordinates array by `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we perform two checks before adding the arrays.

            Firstly, we decide whether to use the Z-dimension for the computation, depending on the shape of `other`:

            - `other.ndim >= 2 and other.shape[1] == 2`: Do not use Z-dimension.
            - `other.ndim >= 2 and other.shape[1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.

            Secondly, if `other.shape[0] == self.data.shape[0]`,
            we automatically repeat each coordinate pair to the number of coordinates of its corresponding polygon.
            This allows you to easily add different coordinate pairs to each polygon.

        Example:
            >>> import pygeos
            >>> import pgpd
            >>> data = pgpd.GeosArray(pygeos.box(range(4), 0, range(10,14), 10))
            >>> data
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
             <pygeos.Geometry POLYGON ((11 0, 11 10, 1 10, 1 0, 11 0))>,
             <pygeos.Geometry POLYGON ((12 0, 12 10, 2 10, 2 0, 12 0))>,
             <pygeos.Geometry POLYGON ((13 0, 13 10, 3 10, 3 0, 13 0))>]
            Length: 4, dtype: geos

            Providing values for each coordinate:
            >>> other = np.tile([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], 4).reshape(20, 2)
            >>> other
            array([[0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1],
                   [0, 1],
                   [2, 3],
                   [4, 5],
                   [6, 7],
                   [0, 1]])
            >>> data // other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((inf 0, 5 3, 0 2, 0 0, inf 0))>,
             <pygeos.Geometry POLYGON ((inf 0, 5 3, 0 2, 0 0, inf 0))>,
             <pygeos.Geometry POLYGON ((inf 0, 6 3, 0 2, 0 0, inf 0))>,
             <pygeos.Geometry POLYGON ((inf 0, 6 3, 0 2, 0 0, inf 0))>]
            Length: 4, dtype: geos

            Provide coordinates for each polygon:
            >>> other = np.array([[0, 1], [2, 3], [4, 5], [6, 7]])
            >>> data // other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((inf 0, inf 10, -nan 10, -nan 0, inf 0))>,
                           <pygeos.Geometry POLYGON ((5 0, 5 3, 0 3, 0 0, 5 0))>,
                           <pygeos.Geometry POLYGON ((3 0, 3 2, 0 2, 0 0, 3 0))>,
                           <pygeos.Geometry POLYGON ((2 0, 2 1, 0 1, 0 0, 2 0))>]
            Length: 4, dtype: geos

            NumPy broadcasting still works:
            >>> # Broadcast X,Y(,Z)
            >>> other = np.array([1,2,3,4])[..., None]
            >>> other.shape
            (4, 1)
            >>> data // other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))>,
                  <pygeos.Geometry POLYGON ((5 0, 5 5, 0 5, 0 0, 5 0))>,
                  <pygeos.Geometry POLYGON ((4 0, 4 3, 0 3, 0 0, 4 0))>,
                  <pygeos.Geometry POLYGON ((3 0, 3 2, 0 2, 0 0, 3 0))>]
            Length: 4, dtype: geos
            >>> # Broadcast coordinates
            >>> other = np.array([10,10])
            >>> other.shape
            (2,)
            >>> data // other
            <GeosArray>
            [<pygeos.Geometry POLYGON ((1 0, 1 1, 0 1, 0 0, 1 0))>,
             <pygeos.Geometry POLYGON ((1 0, 1 1, 0 1, 0 0, 1 0))>,
             <pygeos.Geometry POLYGON ((1 0, 1 1, 0 1, 0 0, 1 0))>,
             <pygeos.Geometry POLYGON ((1 0, 1 1, 0 1, 0 0, 1 0))>]
            Length: 4, dtype: geos
        """
        other = np.asarray(other)
        if other.ndim > 2:
            raise ValueError('Other cannot have more than 2 dimensions.')

        # Check whether we use Z-dimension
        zshape = other.ndim == 2 and other.shape[1]
        if zshape == 2:
            zdim = False
        elif zshape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        # Expand other to number of coords per shape
        pshape = (other.ndim >= 1 and other.shape[0])
        if pshape == self.data.shape[0]:
            other = np.repeat(other, pygeos.get_num_coordinates(self.data), 0)

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt // other,
            zdim,
        ))
