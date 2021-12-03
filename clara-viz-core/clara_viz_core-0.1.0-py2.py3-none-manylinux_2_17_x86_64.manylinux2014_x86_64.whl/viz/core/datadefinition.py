# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .importutil import optional_import
from collections import defaultdict
import json

itk, _ = optional_import("itk")
numpy, _ = optional_import("numpy")


class DataDefinition():
    """Defines the data used by the renderer.

    Attributes:
        arrays: A list of 'Array' elements holding the volume data
        settings: The render settings
    """

    def __init__(self):
        self.arrays = []
        self.settings = {}

    class Array():
        """Defines one array.

        Attributes:
            array: numpy array with the data
            element_size: Physical size of each element, the order is defined by the 'order' field. For
                          elements which have no physical size like 'M' or 'T' the corresponding value is 1.0.
                          Default: [1.0, 1.0, ...]
            order: A string defining the data organization and format. Each character defines
                   a dimension starting with the fastest varying axis and ending with the
                   slowest varying axis. For example a 2D color image is defined as 'CXY',
                   a time sequence of density volumes is defined as 'DXYZT'.
                   Each character can occur only once. Either one of the data element
                   definition characters 'C', 'D' or 'M' and the 'X' axis definition has to
                   be present.
                   - X: width
                   - Y: height
                   - Z: depth
                   - T: time
                   - I: sequence
                   - C: RGB(A) color
                   - D: density
                   - M: mask
            permute_axes: Permutes the given data axes, e.g. to swap x and y of a 3-dimensional
                          density array specify [0, 2, 1, 3]
            flip_axes: Flips the given axes, e.g. to flip the x axis of a 3-dimensional
                       density array specify [False, True, False, False]
        """

        def __init__(self, array=None, order=None):
            """
            Construct an array

            Args:
                array: numpy array with the data
                order: a string defining the data organization and format
            """
            self.array = array
            self.element_size = []
            self.order = order
            self.permute_axes = []
            self.flip_axes = []

    def append(self, filename, order):
        """
        A function to read a volume file with ITK and append it to the DataDefinition

        Args:
            filename: name of the file to read from
            order: a string defining the data organization and format
        """
        array = self.Array()

        array.order = order

        # convert ImageIOBase type to pixel type
        ComponentTypeResolver = defaultdict(lambda: itk.F, {
            itk.CommonEnums.IOComponent_FLOAT: itk.F,
            itk.CommonEnums.IOComponent_LONG: itk.SL,
            itk.CommonEnums.IOComponent_ULONG: itk.UL,
            itk.CommonEnums.IOComponent_SHORT: itk.SS,
            itk.CommonEnums.IOComponent_USHORT: itk.US,
            itk.CommonEnums.IOComponent_CHAR: itk.SC,
            itk.CommonEnums.IOComponent_UCHAR: itk.UC
        })

        # Use image io to get information on the volume
        io = itk.ImageIOFactory.CreateImageIO(filename, itk.CommonEnums.IOFileMode_ReadMode)
        io.SetFileName(filename)
        io.ReadImageInformation()

        dimension = io.GetNumberOfDimensions()
        componentType = io.GetComponentType()

        array.element_size = [1.0]
        for dim in range(dimension):
            array.element_size.append(io.GetSpacing(dim))

        pixelType = ComponentTypeResolver[componentType]
        imageType = itk.Image[pixelType, dimension]

        # get permute and flip axes values for volumes
        orient_filter = itk.OrientImageFilter[imageType, imageType].New()

        dir = [io.GetDirection(0), io.GetDirection(1), io.GetDirection(2)]
        np_dir_vnl = itk.vnl_matrix_from_array(numpy.array(dir))
        direction = itk.Matrix[itk.D, 3, 3](np_dir_vnl)
        orient_filter.SetGivenCoordinateDirection(direction)
        orient_filter.SetDesiredCoordinateOrientation(
            itk.itkSpatialOrientationPython.itkSpatialOrientation_ITK_COORDINATE_ORIENTATION_RIP)

        array.permute_axes.append(0)
        array.flip_axes.append(False)
        for dim in range(io.GetNumberOfDimensions()):
            array.permute_axes.append(orient_filter.GetPermuteOrder()[dim] + 1)
            array.flip_axes.append(orient_filter.GetFlipAxes()[dim])

        # create the reader
        reader = itk.ImageFileReader[imageType].New()
        reader.SetFileName(filename)
        reader.Update()

        array.array = itk.GetArrayViewFromImage(reader.GetOutput())

        self.arrays.append(array)

    def load_settings(self, filename):
        """
        Read settings from a JSON file

        Args:
            filename: name of the JSON file to read
        """
        with open(filename) as f:
            self.settings = json.load(f)
