#
# Geos Accessor for Series
#
from math import sin, cos, tan
import warnings
import numpy as np
import pandas as pd
import pygeos
from ._array import GeosArray
from ._delegated_series import (
    unary_series,
    unary_series_indexed,
    unary_series_keyed,
    unary_dataframe_indexed,
    unary_dataframe_keyed,
    unary_return,
    unary_none,
    binary,
    enable_dataframe_expand,
)

try:
    import geopandas as gpd
except ImportError:
    gpd = None


__all__ = ['GeosSeriesAccessor']


@pd.api.extensions.register_series_accessor('geos')
class GeosSeriesAccessor:
    """
    Access PyGEOS functionality through the "geos" series accessor keyword.

    Example:
        >>> s = pd.Series(pygeos.points(range(15), 0), dtype='geos')
        >>> s
        0    POINT (0 0)
        1    POINT (1 0)
        2    POINT (2 0)
        3    POINT (3 0)
        4    POINT (4 0)
        5    POINT (5 0)
        6    POINT (6 0)
        7    POINT (7 0)
        8    POINT (8 0)
        9    POINT (9 0)
        dtype: geos
        >>> s.geos.has_z
        0    False
        1    False
        2    False
        3    False
        4    False
        5    False
        6    False
        7    False
        8    False
        9    False
        Name: has_z, dtype: bool
    """
    def __init__(self, obj):
        if gpd is not None and pd.api.types.pandas_dtype('geometry') == obj.dtype:
            obj = pd.Series(GeosArray(obj.array.data), name=obj.name, index=obj.index)
        elif (pd.api.types.pandas_dtype('geos') != obj.dtype):
            try:
                obj = pd.Series(GeosArray._from_sequence(obj.values), name=obj.name, index=obj.index)
            except BaseException as err:
                raise AttributeError(f'Cannot convert "{obj.dtype}" type to geos dtype') from err

        self._obj = obj

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    def from_geopandas(self, copy=False):
        """ DEPRECATED: Use :meth:`~pgpd.GeosSeriesAccessor.to_geos` instead. """
        warnings.warn('from_geopandas() is deprecated; use to_geos().', DeprecationWarning)
        return self.to_geos(copy)

    def to_geos(self, copy=False):
        """
        Transform the series in a PyGEOS geos column.

        Args:
            copy (bool, optional): Whether to copy the data or return a wrapper around the same data; Default **False**

        Returns:
            pandas.Series: Series with a geos dtype.

        Note:
            This function will try and convert the following types to geos:

            - geopandas.GeoSeries
            - shapely geometries
            - strings (wkt)
            - bytes (wkb)
        """
        if copy:
            return self._obj.copy()
        else:
            return self._obj

    def to_geopandas(self, crs=None, copy=False):
        """
        Convert a geos Series into a :class:`geopandas.GeoSeries`.

        Args:
            crs (any, optional): CRS to use with GeoPandas, check the docs for more information; Default **None**
            copy (bool, optional): Whether to copy the data or return a wrapper around the same data; Default **False**

        Returns:
            geopandas.GeoSeries: The geopandas series.

        Raises:
            ImportError: Geopandas is not installed.
            AttributeError: Series is not of geos dtype.
        """
        if gpd is None:
            raise ImportError('Geopandas is required for this function')

        if isinstance(self._obj, gpd.GeoSeries):
            s = self._obj
        else:
            s = gpd.GeoSeries(self._obj.astype(object), crs=crs)

        if copy:
            return s.copy()
        else:
            return s

    @enable_dataframe_expand
    def to_shapely(self, **kwargs):
        data = self._obj.array.to_shapely(**kwargs)
        return pd.Series(data, name='shapely', index=self._obj.index)

    @enable_dataframe_expand
    def to_wkt(self, **kwargs):
        data = self._obj.array.to_wkt(**kwargs)
        return pd.Series(data, name='wkt', index=self._obj.index)

    @enable_dataframe_expand
    def to_wkb(self, **kwargs):
        data = self._obj.array.to_wkb(**kwargs)
        return pd.Series(data, name='wkb', index=self._obj.index)

    # -------------------------------------------------------------------------
    # Geometry
    # -------------------------------------------------------------------------
    get_coordinate_dimension = unary_series_indexed('geometry.get_coordinate_dimension')
    get_dimensions = unary_series_indexed('geometry.get_dimensions')
    get_exterior_ring = unary_series_indexed('geometry.get_exterior_ring', geos=True)
    get_geometry = unary_series_indexed('geometry.get_geometry', geos=True)
    get_interior_ring = unary_series_indexed('geometry.get_interior_ring', geos=True)
    get_num_coordinates = unary_series_indexed('geometry.get_num_coordinates')
    get_num_geometries = unary_series_indexed('geometry.get_num_geometries')
    get_num_interior_rings = unary_series_indexed('geometry.get_num_interior_rings')
    get_num_points = unary_series_indexed('geometry.get_num_points')
    get_parts = unary_series_keyed('geometry.get_parts', geos=True, return_index=True)
    get_point = unary_series_indexed('geometry.get_point', geos=True)
    get_precision = unary_series_indexed('geometry.get_precision')
    get_rings = unary_series_keyed('geometry.get_rings', geos=True, return_index=True)
    get_srid = unary_series_indexed('geometry.get_srid')
    get_type_id = unary_series_indexed('geometry.get_type_id')
    get_x = unary_series_indexed('geometry.get_x')
    get_y = unary_series_indexed('geometry.get_y')
    get_z = unary_series_indexed('geometry.get_z')
    force_2d = unary_series_indexed('geometry.force_2d', geos=True)
    force_3d = unary_series_indexed('geometry.force_3d', geos=True)
    set_precision = unary_none('geometry.set_precision')
    set_srid = unary_none('geometry.set_srid')

    # -------------------------------------------------------------------------
    # Geometry Creation
    # -------------------------------------------------------------------------
    destroy_prepared = unary_none('creation.destroy_prepared')
    prepare = unary_none('creation.prepare')

    # -------------------------------------------------------------------------
    # Measurement
    # -------------------------------------------------------------------------
    area = unary_series_indexed('measurement.area')
    bounds = unary_dataframe_indexed('measurement.bounds', ['xmin', 'ymin', 'xmax', 'ymax'])
    distance = binary('measurement.distance')
    frechet_distance = binary('measurement.frechet_distance')
    hausdorff_distance = binary('measurement.hausdorff_distance')
    length = unary_series_indexed('measurement.length')
    minimum_bounding_radius = unary_series_indexed('measurement.minimum_bounding_radius')
    minimum_clearance = unary_series_indexed('measurement.minimum_clearance')
    total_bounds = unary_series('measurement.total_bounds', ['xmin', 'ymin', 'xmax', 'ymax'])

    # -------------------------------------------------------------------------
    # Predicates
    # -------------------------------------------------------------------------
    contains = binary('predicates.contains')
    contains_properly = binary('predicates.contains_properly')
    covered_by = binary('predicates.covered_by')
    covers = binary('predicates.covers')
    crosses = binary('predicates.crosses')
    disjoint = binary('predicates.disjoint')
    equals = binary('predicates.equals')
    equals_exact = binary('predicates.equals_exact')
    has_z = unary_series_indexed('predicates.has_z')
    intersects = binary('predicates.intersects')
    is_ccw = unary_series_indexed('predicates.is_ccw')
    is_closed = unary_series_indexed('predicates.is_closed')
    is_empty = unary_series_indexed('predicates.is_empty')
    is_geometry = unary_series_indexed('predicates.is_geometry')
    is_missing = unary_series_indexed('predicates.is_missing')
    is_prepared = unary_series_indexed('predicates.is_prepared')
    is_ring = unary_series_indexed('predicates.is_ring')
    is_simple = unary_series_indexed('predicates.is_simple')
    is_valid = unary_series_indexed('predicates.is_valid')
    is_valid_input = unary_series_indexed('predicates.is_valid_input')
    is_valid_reason = unary_series_indexed('predicates.is_valid_reason')
    overlaps = binary('predicates.overlaps')
    relate = binary('predicates.relate')
    relate_pattern = binary('predicates.relate_pattern')
    touches = binary('predicates.touches')
    within = binary('predicates.within')

    # -------------------------------------------------------------------------
    # Set operations
    # -------------------------------------------------------------------------
    coverage_union = binary('set_operations.coverage_union', geos=True)
    coverage_union_all = unary_return('set_operations.coverage_union_all')
    difference = binary('set_operations.difference', geos=True)
    intersection = binary('set_operations.intersection', geos=True)
    intersection_all = unary_return('set_operations.intersection_all')
    symmetric_difference = binary('set_operations.symmetric_difference', geos=True)
    symmetric_difference_all = unary_return('set_operations.symmetric_difference_all')
    union = binary('set_operations.union', geos=True)
    union_all = unary_return('set_operations.union_all')

    # -------------------------------------------------------------------------
    # Constructive operations
    # -------------------------------------------------------------------------
    boundary = unary_series_indexed('constructive.boundary', geos=True)
    buffer = unary_series_indexed('constructive.buffer', geos=True)
    build_area = unary_return('constructive.build_area')
    centroid = unary_series_indexed('constructive.centroid', geos=True)
    clip_by_rect = unary_series_indexed('constructive.clip_by_rect', geos=True)
    convex_hull = unary_series_indexed('constructive.convex_hull', geos=True)
    delaunay_triangles = unary_series_indexed('constructive.delaunay_triangles', geos=True)
    envelope = unary_series_indexed('constructive.envelope', geos=True)
    extract_unique_points = unary_series_indexed('constructive.extract_unique_points', geos=True)
    make_valid = unary_series_indexed('constructive.make_valid', geos=True)
    minimum_bounding_circle = unary_series_indexed('constructive.minimum_bounding_circle', geos=True)
    minimum_rotated_rectangle = unary_series_indexed('constructive.minimum_rotated_rectangle', geos=True)
    normalize = unary_series_indexed('constructive.normalize', geos=True)
    offset_curve = unary_series_indexed('constructive.offset_curve', geos=True)
    oriented_envelope = unary_series_indexed('constructive.oriented_envelope', geos=True)
    point_on_surface = unary_series_indexed('constructive.point_on_surface', geos=True)
    polygonize = unary_return('constructive.polygonize')
    reverse = unary_series_indexed('constructive.reverse', geos=True)
    segmentize = unary_return('constructive.segmentize')
    simplify = unary_series_indexed('constructive.simplify', geos=True)
    snap = unary_series_indexed('constructive.snap', geos=True)
    voronoi_polygons = unary_series_indexed('constructive.voronoi_polygons', geos=True)

    # -------------------------------------------------------------------------
    # Linestring operations
    # -------------------------------------------------------------------------
    line_interpolate_point = unary_series_indexed('linear.line_interpolate_point', geos=True)
    line_locate_point = unary_series_indexed('linear.line_locate_point', geos=True)
    line_merge = unary_series_indexed('linear.line_merge', geos=True)
    shared_paths = binary('linear.shared_paths', geos=True)
    shortest_line = binary('linear.shortest_line', geos=True)

    # -------------------------------------------------------------------------
    # Coordinate operations
    # -------------------------------------------------------------------------
    apply = unary_series_indexed('coordinates.apply', geos=True)
    count_coordinates = unary_series_indexed('coordinates.count_coordinates')
    get_coordinates_2d = unary_dataframe_keyed('coordinates.get_coordinates', ['x', 'y'], include_z=False, return_index=True)
    get_coordinates_3d = unary_dataframe_keyed('coordinates.get_coordinates', ['x', 'y', 'z'], include_z=True, return_index=True)
    set_coordinates = unary_series_indexed('coordinates.set_coordinates', geos=True)

    # -------------------------------------------------------------------------
    # STRTree
    # -------------------------------------------------------------------------
    STRtree = unary_return('strtree.STRtree')

    # -------------------------------------------------------------------------
    # Custom Methods
    # -------------------------------------------------------------------------
    @enable_dataframe_expand
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
            pandas.Series: Transformed geometries.

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
        result = self._obj.array.affine(matrix)
        return pd.Series(result, index=self._obj.index, name='affine')

    @enable_dataframe_expand
    def rotate(self, *angles, origin):
        r"""
        Performs a 2D or 3D rotation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    cos(a) & -sin(a) & x_{off} \\
                    sin(a) & cos(a)  & y_{off} \\
                    0      & 0       & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - x_{origin}*cos(a) + y_{origin}*sin(a) \\
                y_{off} &= y_{origin} - x_{origin}*sin(a) - y_{origin}*cos(a)

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    cos(a_z)*cos(a_y) &
                    cos(a_z)*sin(a_y)*sin(a_x) - sin(a_z)*cos(a_x) &
                    cos(a_z)*sin(a_y)*cos(a_x) + sin(a_z)*sin(a_x) &
                    x_{off} \\
                    sin(a_z)*cos(a_y) &
                    sin(a_z)*sin(a_y)*sin(a_x) + cos(a_z)*cos(a_x) &
                    sin(a_z)*sin(a_y)*cos(a_x) - cos(a_z)*sin(a_x) &
                    y_{off} \\
                    -sin(a_y) &
                    cos(a_y)*sin(a_x) &
                    cos(a_y)*cos(a_x) &
                    z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - (a)*x_{origin} - (b)*y_{origin} - (c)*z_{origin} \\
                y_{off} &= y_{origin} - (d)*x_{origin} - (e)*y_{origin} - (f)*z_{origin} \\
                z_{off} &= z_{origin} - (g)*x_{origin} - (h)*y_{origin} - (i)*z_{origin}

        Args:
            angles (float): 2D rotation angle or X,Y,Z 3D rotation angles in radians.
            origin (pygeos.lib.Geometry or list-like): Origin point for the transformation.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if origin is None:
            origin = (0, 0, 0)
        elif isinstance(origin, pygeos.lib.Geometry):
            if pygeos.get_type_id(origin) != 0:
                raise TypeError('Origin should be a single point geometry')
            origin = np.nan_to_num(pygeos.get_coordinates(origin, True)).squeeze()

        if len(angles) == 1:
            x0, y0 = origin[:2]
            ca = cos(angles[0])
            sa = sin(angles[0])
            result = self._obj.array.affine((
                ca, -sa,
                sa, ca,
                x0 - x0*ca + y0*sa,
                y0 - x0*sa - y0*ca,
            ))
        elif len(angles) == 3:
            x0, y0, z0 = origin[:3]
            cx, cy, cz = (cos(a) for a in angles)
            sx, sy, sz = (sin(a) for a in angles)
            a = cz*cy
            b = cz*sy*sx - sz*cx
            c = cz*sy*cx + sz*sx
            d = sz*cy
            e = sz*sy*sx + cz*cx
            f = sz*sy*cx - cz*sx
            g = -sy
            h = cy*sx
            i = cy*cx
            result = self._obj.array.affine((
                a, b, c,
                d, e, f,
                g, h, i,
                x0 - a*x0 - b*y0 - c*z0,
                y0 - d*x0 - e*y0 - f*z0,
                z0 - g*x0 - h*y0 - i*z0,
            ))
        else:
            raise ValueError('The rotate transformation requires 1 or 3 angles')

        return pd.Series(result, index=self._obj.index, name='rotate')

    @enable_dataframe_expand
    def scale(self, x, y, z=None, *, origin=None):
        r"""
        Performs a 2D or 3D scaling on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    x_s & 0 & x_{off} \\
                    0 & y_s & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - x_{origin}*x_s \\
                y_{off} &= y_{origin} - y_{origin}*y_s

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    x_s & 0 & 0 & x_{off} \\
                    0 & y_s & 0 & y_{off} \\
                    0 & 0 & z_s & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - x_{origin}*x_s \\
                y_{off} &= y_{origin} - y_{origin}*y_s \\
                z_{off} &= z_{origin} - z_{origin}*z_s

        Args:
            x (float): Scaling value in the X direction.
            y (float): Scaling value in the Y direction.
            z (float, optional): Scaling value in the Z direction; Default **None**.
            origin (pygeos.lib.Geometry or list-like): Origin point for the transformation.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if origin is None:
            origin = (0, 0, 0)
        elif isinstance(origin, pygeos.lib.Geometry):
            if pygeos.get_type_id(origin) != 0:
                raise TypeError('Origin should be a single point geometry')
            origin = np.nan_to_num(pygeos.get_coordinates(origin, True)).squeeze()

        if z is None:
            x0, y0 = origin[:2]
            result = self._obj.array.affine((
                x, 0,
                0, y,
                x0 - x * x0,
                y0 - y * y0,
            ))
        else:
            x0, y0, z0 = origin[:3]
            result = self._obj.array.affine((
                x, 0, 0,
                0, y, 0,
                0, 0, z,
                x0 - x * x0,
                y0 - y * y0,
                z0 - z * z0,
            ))

        return pd.Series(result, index=self._obj.index, name='scale')

    @enable_dataframe_expand
    def skew(self, *angles, origin=None):
        r"""
        Performs a 2D or 3D skew/shear transformation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & a_{xy} & x_{off} \\
                    a_{yx} & 1 & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}
                \\
                x_{off} &= -(y_{origin}*a_{xy}) \\
                y_{off} &= -(x_{origin}*a_{yx})

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & a_{xy} & a_{xz} & x_{off} \\
                    a_{yx} & 1 & a_{yz} & y_{off} \\
                    a_{zx} & a_{zy} & 1 & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}
                \\
                x_{off} &= -(y_{origin}*a_{xy} + z_{origin}*a_{xz}) \\
                y_{off} &= -(x_{origin}*a_{yx} + z_{origin}*a_{yz}) \\
                z_{off} &= -(x_{origin}*a_{zx} + y_{origin}*a_{zy})

        Args:
            angles (float): skewing angles (2D: ``[x, y]`` ; 3D: ``[xy, xz, yx, yz, zx, zy]``)
            origin (pygeos.lib.Geometry or list-like): Origin point for the transformation.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if origin is None:
            origin = (0, 0, 0)
        elif isinstance(origin, pygeos.lib.Geometry):
            if pygeos.get_type_id(origin) != 0:
                raise TypeError('Origin should be a single point geometry')
            origin = np.nan_to_num(pygeos.get_coordinates(origin, True)).squeeze()

        if len(angles) == 2:
            x0, y0 = origin[:2]
            x, y = (tan(a) for a in angles)
            result = self._obj.array.affine((
                1, x,
                y, 1,
                -(y0*x),
                -(x0*y),
            ))
        elif len(angles) == 6:
            x0, y0, z0 = origin[:3]
            xy, xz, yx, yz, zx, zy = (tan(a) for a in angles)
            result = self._obj.array.affine((
                1, xy, xz,
                yx, 1, yz,
                zx, zy, 1,
                -(y0*xy + z0*xz),
                -(x0*yx + z0*yz),
                -(x0*zx + y0*zy),
            ))
        else:
            raise ValueError('The skew transformation requires 2 or 6 angles')

        return pd.Series(result, index=self._obj.index, name='skew')

    @enable_dataframe_expand
    def translate(self, x, y, z=None):
        r"""
        Performs a 2D or 3D translation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & 0 & x_t \\
                    0 & 1 & y_t \\
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
                &=
                \begin{bmatrix}
                    1 & 0 & 0 & x_t \\
                    0 & 1 & 0 & y_t \\
                    0 & 0 & 1 & z_t \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}

        Args:
            x (float): Translation value in the X direction.
            y (float): Translation value in the Y direction.
            z (float, optional): Translation value in the Z direction; Default **None**.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if z is None:
            result = self._obj.array.affine((1, 0, 0, 1, x, y))
        else:
            result = self._obj.array.affine((1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z))

        return pd.Series(result, index=self._obj.index, name='translate')

    @enable_dataframe_expand
    def apply_shapely(self, func):
        """
        Applies a function to each geometry as a shapely object.

        Args:
            func (callable): Function that gets a shapely geometry and should return a shapely geometry or None

        Returns:
            pandas.Series: Transformed geometries.

        Note:
            This function is supposed to be used when some functionality from is missing from PyGEOS,
            but is available in shapely.
            However, do note that it is very inneficient.

            1. Transform array to shapely.
            2. Loop over list and apply function.
            3. Transform list of shapely to GeosArray.
            4. Return Series.
        """
        result = GeosArray.from_shapely([func(geom) for geom in self._obj.array.to_shapely()])
        return pd.Series(result, index=self._obj.index, name='shapely')
