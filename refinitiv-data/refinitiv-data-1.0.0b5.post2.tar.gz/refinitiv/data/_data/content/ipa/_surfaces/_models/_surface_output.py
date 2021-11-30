# coding: utf8

__all__ = ["SurfaceOutput"]

from ..._object_definition import ObjectDefinition
from ._volatility_surface_point import VolatilitySurfacePoint
from .._enums import Format
from .._surface_types import OptFormat, OptVolatilitySurfacePoints
from ...._types import OptStrings, OptInt
from .....tools import create_repr


class SurfaceOutput(ObjectDefinition):
    """

    Parameters
    ---------
    data_points : list of VolatilitySurfacePoint, optional
        Specifies the list of specific data points to be returned
    format : Format, option
        Specifies whether the calculated volatilities are returned as a list or a matrix
    x_values : list of str, optional
        Specifies a list of discrete values for the x-axis
    y_values : list of str, optional
        Specifies a list of discrete values for the y-axis
    z_values : list of str, optional
        Specifies a list of discrete values for the z-axis
    x_point_count : int, optional
        Specifies the number of values that will be generated along the x-axis.
        These values will distributed depending on the available input data and the type
        of volatility
    y_point_count : int, optional
        Specifies the number of values that will be generated along the y-axis.
        These values will distributed depending on the available input data and the type
        of volatility
    z_point_count : int, optional
        Specifies the number of values that will be generated along the z-axis.
        These values will distributed depending on the available input data and the type
        of volatility

    Examples
    -------
    >>> from refinitiv.data.content.ipa.surfaces.surface_fx import SurfaceLayout
    >>> from refinitiv.data.content.ipa.surfaces import surface_fx
    >>> SurfaceLayout(format=surface_fx.Format.MATRIX)
    """

    def __init__(
        self,
        data_points: OptVolatilitySurfacePoints = None,
        format: OptFormat = None,
        x_values: OptStrings = None,
        y_values: OptStrings = None,
        z_values: OptStrings = None,
        x_point_count: OptInt = None,
        y_point_count: OptInt = None,
        z_point_count: OptInt = None,
    ):
        super().__init__()
        self.data_points = data_points
        self.format = format
        self.x_values = x_values
        self.y_values = y_values
        self.z_values = z_values
        self.x_point_count = x_point_count
        self.y_point_count = y_point_count
        self.z_point_count = z_point_count

    def __repr__(self):
        return create_repr(
            self,
            middle_path="content.ipa.surfaces.surface_fx",
            class_name="SurfaceLayout",
        )

    @property
    def data_points(self):
        """
        Specifies the list of specific data points to be returned.
        :return: list VolatilitySurfacePoint
        """
        return self._get_list_parameter(VolatilitySurfacePoint, "dataPoints")

    @data_points.setter
    def data_points(self, value):
        self._set_list_parameter(VolatilitySurfacePoint, "dataPoints", value)

    @property
    def format(self):
        """
        Specifies whether the calculated volatilities are returned as a list or a matrix.
        :return: enum Format
        """
        return self._get_enum_parameter(Format, "format")

    @format.setter
    def format(self, value):
        self._set_enum_parameter(Format, "format", value)

    @property
    def x_values(self):
        """
        Specifies a list of discrete values for the x-axis.
        :return: list string
        """
        return self._get_list_parameter(str, "xValues")

    @x_values.setter
    def x_values(self, value):
        self._set_list_parameter(str, "xValues", value)

    @property
    def y_values(self):
        """
        Specifies a list of discrete values for the y-axis.
        :return: list string
        """
        return self._get_list_parameter(str, "yValues")

    @y_values.setter
    def y_values(self, value):
        self._set_list_parameter(str, "yValues", value)

    @property
    def z_values(self):
        """
        Specifies a list of discrete values for the z-axis.
        :return: list string
        """
        return self._get_list_parameter(str, "zValues")

    @z_values.setter
    def z_values(self, value):
        self._set_list_parameter(str, "zValues", value)

    @property
    def x_point_count(self):
        """
        Specifies the number of values that will be generated along the x-axis.
        These values will distributed depending on the available input data and the type of volatility.
        :return: int
        """
        return self._get_parameter("xPointCount")

    @x_point_count.setter
    def x_point_count(self, value):
        self._set_parameter("xPointCount", value)

    @property
    def y_point_count(self):
        """
        Specifies the number of values that will be generated along the y-axis.
        These values will distributed depending on the available input data and the type of volatility.
        :return: int
        """
        return self._get_parameter("yPointCount")

    @y_point_count.setter
    def y_point_count(self, value):
        self._set_parameter("yPointCount", value)

    @property
    def z_point_count(self):
        """
        Specifies the number of values that will be generated along the z-axis.
        These values will distributed depending on the available input data and the type of volatility.
        :return: int
        """
        return self._get_parameter("zPointCount")

    @z_point_count.setter
    def z_point_count(self, value):
        self._set_parameter("zPointCount", value)
