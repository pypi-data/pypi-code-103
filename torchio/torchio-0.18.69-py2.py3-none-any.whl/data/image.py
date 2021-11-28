import warnings
from pathlib import Path
from collections import Counter
from collections.abc import Iterable
from typing import Any, Dict, Tuple, Optional, Union, Sequence, List, Callable

import torch
import humanize
import numpy as np
import nibabel as nib
import SimpleITK as sitk
from deprecated import deprecated

from ..utils import get_stem, guess_external_viewer
from ..typing import (
    TypePath,
    TypeData,
    TypeDataAffine,
    TypeTripletInt,
    TypeTripletFloat,
    TypeDirection3D,
)
from ..constants import DATA, TYPE, AFFINE, PATH, STEM, INTENSITY, LABEL
from .io import (
    ensure_4d,
    read_image,
    write_image,
    nib_to_sitk,
    sitk_to_nib,
    check_uint_to_int,
    get_rotation_and_spacing_from_affine,
    get_sitk_metadata_from_ras_affine,
    read_shape,
    read_affine,
)


PROTECTED_KEYS = DATA, AFFINE, TYPE, PATH, STEM
TypeBound = Tuple[float, float]
TypeBounds = Tuple[TypeBound, TypeBound, TypeBound]

deprecation_message = (
    'Setting the image data with the property setter is deprecated. Use the'
    ' set_data() method instead'
)


class Image(dict):
    r"""TorchIO image.

    For information about medical image orientation, check out `NiBabel docs`_,
    the `3D Slicer wiki`_, `Graham Wideman's website`_, `FSL docs`_ or
    `SimpleITK docs`_.

    Args:
        path: Path to a file or sequence of paths to files that can be read by
            :mod:`SimpleITK` or :mod:`nibabel`, or to a directory containing
            DICOM files. If :attr:`tensor` is given, the data in
            :attr:`path` will not be read.
            If a sequence of paths is given, data
            will be concatenated on the channel dimension so spatial
            dimensions must match.
        type: Type of image, such as :attr:`torchio.INTENSITY` or
            :attr:`torchio.LABEL`. This will be used by the transforms to
            decide whether to apply an operation, or which interpolation to use
            when resampling. For example, `preprocessing`_ and `augmentation`_
            intensity transforms will only be applied to images with type
            :attr:`torchio.INTENSITY`. Spatial transforms will be applied to
            all types, and nearest neighbor interpolation is always used to
            resample images with type :attr:`torchio.LABEL`.
            The type :attr:`torchio.SAMPLING_MAP` may be used with instances of
            :class:`~torchio.data.sampler.weighted.WeightedSampler`.
        tensor: If :attr:`path` is not given, :attr:`tensor` must be a 4D
            :class:`torch.Tensor` or NumPy array with dimensions
            :math:`(C, W, H, D)`.
        affine: :math:`4 \times 4` matrix to convert voxel coordinates to world
            coordinates. If ``None``, an identity matrix will be used. See the
            `NiBabel docs on coordinates`_ for more information.
        check_nans: If ``True``, issues a warning if NaNs are found
            in the image. If ``False``, images will not be checked for the
            presence of NaNs.
        reader: Callable object that takes a path and returns a 4D tensor and a
            2D, :math:`4 \times 4` affine matrix. This can be used if your data
            is saved in a custom format, such as ``.npy`` (see example below).
            If the affine matrix is ``None``, an identity matrix will be used.
        **kwargs: Items that will be added to the image dictionary, e.g.
            acquisition parameters.

    TorchIO images are `lazy loaders`_, i.e. the data is only loaded from disk
    when needed.

    Example:
        >>> import torchio as tio
        >>> import numpy as np
        >>> image = tio.ScalarImage('t1.nii.gz')  # subclass of Image
        >>> image  # not loaded yet
        ScalarImage(path: t1.nii.gz; type: intensity)
        >>> times_two = 2 * image.data  # data is loaded and cached here
        >>> image
        ScalarImage(shape: (1, 256, 256, 176); spacing: (1.00, 1.00, 1.00); orientation: PIR+; memory: 44.0 MiB; type: intensity)
        >>> image.save('doubled_image.nii.gz')
        >>> numpy_reader = lambda path: np.load(path), np.eye(4)
        >>> image = tio.ScalarImage('t1.npy', reader=numpy_reader)

    .. _lazy loaders: https://en.wikipedia.org/wiki/Lazy_loading
    .. _preprocessing: https://torchio.readthedocs.io/transforms/preprocessing.html#intensity
    .. _augmentation: https://torchio.readthedocs.io/transforms/augmentation.html#intensity
    .. _NiBabel docs: https://nipy.org/nibabel/image_orientation.html
    .. _NiBabel docs on coordinates: https://nipy.org/nibabel/coordinate_systems.html#the-affine-matrix-as-a-transformation-between-spaces
    .. _3D Slicer wiki: https://www.slicer.org/wiki/Coordinate_systems
    .. _FSL docs: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Orientation%20Explained
    .. _SimpleITK docs: https://simpleitk.readthedocs.io/en/master/fundamentalConcepts.html
    .. _Graham Wideman's website: http://www.grahamwideman.com/gw/brain/orientation/orientterms.htm
    """  # noqa: E501
    def __init__(
            self,
            path: Union[TypePath, Sequence[TypePath], None] = None,
            type: str = None,  # noqa: A002
            tensor: Optional[TypeData] = None,
            affine: Optional[TypeData] = None,
            check_nans: bool = False,  # removed by ITK by default
            reader: Callable = read_image,
            **kwargs: Dict[str, Any],
            ):
        self.check_nans = check_nans
        self.reader = reader

        if type is None:
            warnings.warn(
                'Not specifying the image type is deprecated and will be'
                ' mandatory in the future. You can probably use'
                ' tio.ScalarImage or tio.LabelMap instead'
            )
            type = INTENSITY  # noqa: A001

        if path is None and tensor is None:
            raise ValueError('A value for path or tensor must be given')
        self._loaded = False

        tensor = self._parse_tensor(tensor)
        affine = self._parse_affine(affine)
        if tensor is not None:
            self.set_data(tensor)
            self.affine = affine
            self._loaded = True
        for key in PROTECTED_KEYS:
            if key in kwargs:
                message = f'Key "{key}" is reserved. Use a different one'
                raise ValueError(message)
        if 'channels_last' in kwargs:
            message = (
                'The "channels_last" keyword argument is deprecated after'
                ' https://github.com/fepegar/torchio/pull/685 and will be'
                ' removed in the future'
            )
            warnings.warn(message, DeprecationWarning)

        super().__init__(**kwargs)
        self.path = self._parse_path(path)

        self[PATH] = '' if self.path is None else str(self.path)
        self[STEM] = '' if self.path is None else get_stem(self.path)
        self[TYPE] = type

    def __repr__(self):
        properties = []
        properties.extend([
            f'shape: {self.shape}',
            f'spacing: {self.get_spacing_string()}',
            f'orientation: {"".join(self.orientation)}+',
        ])
        if self._loaded:
            properties.append(f'dtype: {self.data.type()}')
            natural = humanize.naturalsize(self.memory, binary=True)
            properties.append(f'memory: {natural}')
        else:
            properties.append(f'path: "{self.path}"')

        properties = '; '.join(properties)
        string = f'{self.__class__.__name__}({properties})'
        return string

    def __getitem__(self, item):
        if item in (DATA, AFFINE):
            if item not in self:
                self.load()
        return super().__getitem__(item)

    def __array__(self):
        return self.data.numpy()

    def __copy__(self):
        kwargs = {
            'tensor': self.data,
            'affine': self.affine,
            'type': self.type,
            'path': self.path,
        }
        for key, value in self.items():
            if key in PROTECTED_KEYS:
                continue
            kwargs[key] = value  # should I copy? deepcopy?
        return self.__class__(**kwargs)

    @property
    def data(self) -> torch.Tensor:
        """Tensor data. Same as :class:`Image.tensor`."""
        return self[DATA]

    @data.setter  # type: ignore
    @deprecated(version='0.18.16', reason=deprecation_message)
    def data(self, tensor: TypeData):
        self.set_data(tensor)

    def set_data(self, tensor: TypeData):
        """Store a 4D tensor in the :attr:`data` key and attribute.

        Args:
            tensor: 4D tensor with dimensions :math:`(C, W, H, D)`.
        """
        self[DATA] = self._parse_tensor(tensor, none_ok=False)

    @property
    def tensor(self) -> torch.Tensor:
        """Tensor data. Same as :class:`Image.data`."""
        return self.data

    @property
    def affine(self) -> np.ndarray:
        """Affine matrix to transform voxel indices into world coordinates."""
        # If path is a dir (probably DICOM), just load the data
        # Same if it's a list of paths (used to create a 4D image)
        is_dir = isinstance(self.path, Path) and self.path.is_dir()
        if self._loaded or is_dir:
            affine = self[AFFINE]
        else:
            affine = read_affine(self.path)
        return affine

    @affine.setter
    def affine(self, matrix):
        self[AFFINE] = self._parse_affine(matrix)

    @property
    def type(self) -> str:  # noqa: A003
        return self[TYPE]

    @property
    def shape(self) -> Tuple[int, int, int, int]:
        """Tensor shape as :math:`(C, W, H, D)`."""
        custom_reader = self.reader is not read_image
        multipath = not isinstance(self.path, (str, Path))
        if self._loaded or custom_reader or multipath or self.path.is_dir():
            shape = tuple(self.data.shape)
        else:
            shape = read_shape(self.path)
        return shape

    @property
    def spatial_shape(self) -> TypeTripletInt:
        """Tensor spatial shape as :math:`(W, H, D)`."""
        return self.shape[1:]

    def check_is_2d(self) -> None:
        if not self.is_2d():
            message = f'Image is not 2D. Spatial shape: {self.spatial_shape}'
            raise RuntimeError(message)

    @property
    def height(self) -> int:
        """Image height, if 2D."""
        self.check_is_2d()
        return self.spatial_shape[1]

    @property
    def width(self) -> int:
        """Image width, if 2D."""
        self.check_is_2d()
        return self.spatial_shape[0]

    @property
    def orientation(self) -> Tuple[str, str, str]:
        """Orientation codes."""
        return nib.aff2axcodes(self.affine)

    @property
    def direction(self) -> TypeDirection3D:
        _, _, direction = get_sitk_metadata_from_ras_affine(
            self.affine, lps=False)
        return direction

    @property
    def spacing(self) -> Tuple[float, float, float]:
        """Voxel spacing in mm."""
        _, spacing = get_rotation_and_spacing_from_affine(self.affine)
        return tuple(spacing)

    @property
    def origin(self) -> Tuple[float, float, float]:
        """Center of first voxel in array, in mm."""
        return tuple(self.affine[:3, 3])

    @property
    def itemsize(self):
        """Element size of the data type."""
        return self.data.element_size()

    @property
    def memory(self) -> float:
        """Number of Bytes that the tensor takes in the RAM."""
        return np.prod(self.shape) * self.itemsize

    @property
    def bounds(self) -> np.ndarray:
        """Position of centers of voxels in smallest and largest indices."""
        ini = 0, 0, 0
        fin = np.array(self.spatial_shape) - 1
        point_ini = nib.affines.apply_affine(self.affine, ini)
        point_fin = nib.affines.apply_affine(self.affine, fin)
        return np.array((point_ini, point_fin))

    @property
    def num_channels(self) -> int:
        """Get the number of channels in the associated 4D tensor."""
        return len(self.data)

    def axis_name_to_index(self, axis: str) -> int:
        """Convert an axis name to an axis index.

        Args:
            axis: Possible inputs are ``'Left'``, ``'Right'``, ``'Anterior'``,
                ``'Posterior'``, ``'Inferior'``, ``'Superior'``. Lower-case
                versions and first letters are also valid, as only the first
                letter will be used.

        .. note:: If you are working with animals, you should probably use
            ``'Superior'``, ``'Inferior'``, ``'Anterior'`` and ``'Posterior'``
            for ``'Dorsal'``, ``'Ventral'``, ``'Rostral'`` and ``'Caudal'``,
            respectively.

        .. note:: If your images are 2D, you can use ``'Top'``, ``'Bottom'``,
            ``'Left'`` and ``'Right'``.
        """
        # Top and bottom are used for the vertical 2D axis as the use of
        # Height vs Horizontal might be ambiguous

        if not isinstance(axis, str):
            raise ValueError('Axis must be a string')
        axis = axis[0].upper()

        # Generally, TorchIO tensors are (C, W, H, D)
        if axis in 'TB':  # Top, Bottom
            return -2
        else:
            try:
                index = self.orientation.index(axis)
            except ValueError:
                index = self.orientation.index(self.flip_axis(axis))
            # Return negative indices so that it does not matter whether we
            # refer to spatial dimensions or not
            index = -3 + index
            return index

    @staticmethod
    def flip_axis(axis: str) -> str:
        """Return the opposite axis label. For example, ``'L'`` -> ``'R'``.

        Args:
            axis: Axis label, such as ``'L'`` or ``'left'``.
        """
        labels = 'LRPAISTBDV'
        first = labels[::2]
        last = labels[1::2]
        flip_dict = {a: b for a, b in zip(first + last, last + first)}
        axis = axis[0].upper()
        flipped_axis = flip_dict.get(axis)
        if flipped_axis is None:
            values = ', '.join(labels)
            message = f'Axis not understood. Please use one of: {values}'
            raise ValueError(message)
        return flipped_axis

    def get_spacing_string(self) -> str:
        strings = [f'{n:.2f}' for n in self.spacing]
        string = f'({", ".join(strings)})'
        return string

    def get_bounds(self) -> TypeBounds:
        """Get minimum and maximum world coordinates occupied by the image."""
        first_index = 3 * (-0.5,)
        last_index = np.array(self.spatial_shape) - 0.5
        first_point = nib.affines.apply_affine(self.affine, first_index)
        last_point = nib.affines.apply_affine(self.affine, last_index)
        array = np.array((first_point, last_point))
        bounds_x, bounds_y, bounds_z = array.T.tolist()
        return bounds_x, bounds_y, bounds_z

    @staticmethod
    def _parse_single_path(
            path: TypePath
            ) -> Path:
        try:
            path = Path(path).expanduser()
        except TypeError:
            message = (
                f'Expected type str or Path but found {path} with type'
                f' {type(path)} instead'
            )
            raise TypeError(message)
        except RuntimeError:
            message = (
                f'Conversion to path not possible for variable: {path}'
            )
            raise RuntimeError(message)

        if not (path.is_file() or path.is_dir()):   # might be a dir with DICOM
            raise FileNotFoundError(f'File not found: "{path}"')
        return path

    def _parse_path(
            self,
            path: Union[TypePath, Sequence[TypePath], None]
            ) -> Optional[Union[Path, List[Path]]]:
        if path is None:
            return None
        if isinstance(path, Iterable) and not isinstance(path, str):
            return [self._parse_single_path(p) for p in path]
        else:
            return self._parse_single_path(path)

    def _parse_tensor(
            self,
            tensor: Optional[TypeData],
            none_ok: bool = True,
            ) -> Optional[torch.Tensor]:
        if tensor is None:
            if none_ok:
                return None
            else:
                raise RuntimeError('Input tensor cannot be None')
        if isinstance(tensor, np.ndarray):
            tensor = check_uint_to_int(tensor)
            tensor = torch.as_tensor(tensor)
        elif not isinstance(tensor, torch.Tensor):
            message = (
                'Input tensor must be a PyTorch tensor or NumPy array,'
                f' but type "{type(tensor)}" was found'
            )
            raise TypeError(message)
        ndim = tensor.ndim
        if ndim != 4:
            raise ValueError(f'Input tensor must be 4D, but it is {ndim}D')
        if tensor.dtype == torch.bool:
            tensor = tensor.to(torch.uint8)
        if self.check_nans and torch.isnan(tensor).any():
            warnings.warn('NaNs found in tensor', RuntimeWarning)
        return tensor

    @staticmethod
    def _parse_tensor_shape(tensor: torch.Tensor) -> TypeData:
        return ensure_4d(tensor)

    @staticmethod
    def _parse_affine(affine: Optional[TypeData]) -> np.ndarray:
        if affine is None:
            return np.eye(4)
        if isinstance(affine, torch.Tensor):
            affine = affine.numpy()
        if not isinstance(affine, np.ndarray):
            bad_type = type(affine)
            raise TypeError(f'Affine must be a NumPy array, not {bad_type}')
        if affine.shape != (4, 4):
            bad_shape = affine.shape
            raise ValueError(f'Affine shape must be (4, 4), not {bad_shape}')
        return affine.astype(np.float64)

    def load(self) -> None:
        r"""Load the image from disk.

        Returns:
            Tuple containing a 4D tensor of size :math:`(C, W, H, D)` and a 2D
            :math:`4 \times 4` affine matrix to convert voxel indices to world
            coordinates.
        """
        if self._loaded:
            return
        paths = self.path if isinstance(self.path, list) else [self.path]
        tensor, affine = self.read_and_check(paths[0])
        tensors = [tensor]
        for path in paths[1:]:
            new_tensor, new_affine = self.read_and_check(path)
            if not np.array_equal(affine, new_affine):
                message = (
                    'Files have different affine matrices.'
                    f'\nMatrix of {paths[0]}:'
                    f'\n{affine}'
                    f'\nMatrix of {path}:'
                    f'\n{new_affine}'
                )
                warnings.warn(message, RuntimeWarning)
            if not tensor.shape[1:] == new_tensor.shape[1:]:
                message = (
                    f'Files shape do not match, found {tensor.shape}'
                    f'and {new_tensor.shape}'
                )
                RuntimeError(message)
            tensors.append(new_tensor)
        tensor = torch.cat(tensors)
        self.set_data(tensor)
        self.affine = affine
        self._loaded = True

    def read_and_check(self, path: TypePath) -> TypeDataAffine:
        tensor, affine = self.reader(path)
        tensor = self._parse_tensor_shape(tensor)
        tensor = self._parse_tensor(tensor)
        affine = self._parse_affine(affine)
        if self.check_nans and torch.isnan(tensor).any():
            warnings.warn(f'NaNs found in file "{path}"', RuntimeWarning)
        return tensor, affine

    def save(self, path: TypePath, squeeze: Optional[bool] = None) -> None:
        """Save image to disk.

        Args:
            path: String or instance of :class:`pathlib.Path`.
            squeeze: Whether to remove singleton dimensions before saving.
                If ``None``, the array will be squeezed if the output format is
                JP(E)G, PNG, BMP or TIF(F).
        """
        write_image(
            self.data,
            self.affine,
            path,
            squeeze=squeeze,
        )

    def is_2d(self) -> bool:
        return self.shape[-1] == 1

    def numpy(self) -> np.ndarray:
        """Get a NumPy array containing the image data."""
        return np.asarray(self)

    def as_sitk(self, **kwargs) -> sitk.Image:
        """Get the image as an instance of :class:`sitk.Image`."""
        return nib_to_sitk(self.data, self.affine, **kwargs)

    @classmethod
    def from_sitk(cls, sitk_image):
        """Instantiate a new TorchIO image from a :class:`sitk.Image`.

        Example:
            >>> import torchio as tio
            >>> import SimpleITK as sitk
            >>> sitk_image = sitk.Image(20, 30, 40, sitk.sitkUInt16)
            >>> tio.LabelMap.from_sitk(sitk_image)
            LabelMap(shape: (1, 20, 30, 40); spacing: (1.00, 1.00, 1.00); orientation: LPS+; memory: 93.8 KiB; dtype: torch.IntTensor)
            >>> sitk_image = sitk.Image((224, 224), sitk.sitkVectorFloat32, 3)
            >>> tio.ScalarImage.from_sitk(sitk_image)
            ScalarImage(shape: (3, 224, 224, 1); spacing: (1.00, 1.00, 1.00); orientation: LPS+; memory: 588.0 KiB; dtype: torch.FloatTensor)
        """  # noqa: E501
        tensor, affine = sitk_to_nib(sitk_image)
        return cls(tensor=tensor, affine=affine)

    def as_pil(self, transpose=True):
        """Get the image as an instance of :class:`PIL.Image`.

        .. note:: Values will be clamped to 0-255 and cast to uint8.
        .. note:: To use this method, `Pillow` needs to be installed:
            `pip install Pillow`.
        """
        try:
            from PIL import Image as ImagePIL
        except ModuleNotFoundError as e:
            message = (
                'Please install Pillow to use Image.as_pil():'
                ' pip install Pillow'
            )
            raise RuntimeError(message) from e

        self.check_is_2d()
        tensor = self.data
        if len(tensor) == 1:
            tensor = torch.cat(3 * [tensor])
        if len(tensor) != 3:
            raise RuntimeError('The image must have 1 or 3 channels')
        if transpose:
            tensor = tensor.permute(3, 2, 1, 0)
        else:
            tensor = tensor.permute(3, 1, 2, 0)
        array = tensor.clamp(0, 255).numpy()[0]
        return ImagePIL.fromarray(array.astype(np.uint8))

    def to_gif(
            self,
            axis: int,
            duration: float,  # of full gif
            output_path: TypePath,
            loop: int = 0,
            rescale: bool = True,
            optimize: bool = True,
            reverse: bool = False,
            ) -> None:
        """Save an animated GIF of the image.

        Args:
            axis: Spatial axis (0, 1 or 2).
            duration: Duration of the full animation in seconds.
            output_path: Path to the output GIF file.
            loop: Number of times the GIF should loop.
                ``0`` means that it will loop forever.
            rescale: Use :class:`~torchio.transforms.preprocessing.intensity.rescale.RescaleIntensity`
                to rescale the intensity values to :math:`[0, 255]`.
            optimize: If ``True``, attempt to compress the palette by
                eliminating unused colors. This is only useful if the palette
                can be compressed to the next smaller power of 2 elements.
            reverse: Reverse the temporal order of frames.
        """  # noqa: E501
        from ..visualization import make_gif  # avoid circular import
        make_gif(
            self.data,
            axis,
            duration,
            output_path,
            loop=loop,
            rescale=rescale,
            optimize=optimize,
            reverse=reverse,
        )

    def get_center(self, lps: bool = False) -> TypeTripletFloat:
        """Get image center in RAS+ or LPS+ coordinates.

        Args:
            lps: If ``True``, the coordinates will be in LPS+ orientation, i.e.
                the first dimension grows towards the left, etc. Otherwise, the
                coordinates will be in RAS+ orientation.
        """
        size = np.array(self.spatial_shape)
        center_index = (size - 1) / 2
        r, a, s = nib.affines.apply_affine(self.affine, center_index)
        if lps:
            return (-r, -a, s)
        else:
            return (r, a, s)

    def set_check_nans(self, check_nans: bool) -> None:
        self.check_nans = check_nans

    def plot(self, **kwargs) -> None:
        """Plot image."""
        if self.is_2d():
            self.as_pil().show()
        else:
            from ..visualization import plot_volume  # avoid circular import
            plot_volume(self, **kwargs)

    def show(self, viewer_path: Optional[TypePath] = None) -> None:
        """Open the image using external software.

        Args:
            viewer_path: Path to the application used to view the image. If
                ``None``, the value of the environment variable
                ``SITK_SHOW_COMMAND`` will be used. If this variable is also
                not set, TorchIO will try to guess the location of
                `ITK-SNAP <http://www.itksnap.org/pmwiki/pmwiki.php>`_ and
                `3D Slicer <https://www.slicer.org/>`_.

        Raises:
            RuntimeError: If the viewer is not found.
        """
        sitk_image = self.as_sitk()
        image_viewer = sitk.ImageViewer()
        # This is so that 3D Slicer creates segmentation nodes from label maps
        if self.__class__.__name__ == 'LabelMap':
            image_viewer.SetFileExtension('.seg.nrrd')
        if viewer_path is not None:
            image_viewer.SetApplication(str(viewer_path))
        try:
            image_viewer.Execute(sitk_image)
        except RuntimeError as e:
            viewer_path = guess_external_viewer()
            if viewer_path is None:
                message = (
                    'No external viewer has been found. Please set the'
                    ' environment variable SITK_SHOW_COMMAND to a viewer of'
                    ' your choice'
                )
                raise RuntimeError(message) from e
            image_viewer.SetApplication(str(viewer_path))
            image_viewer.Execute(sitk_image)


class ScalarImage(Image):
    """Image whose pixel values represent scalars.

    Example:
        >>> import torch
        >>> import torchio as tio
        >>> # Loading from a file
        >>> t1_image = tio.ScalarImage('t1.nii.gz')
        >>> dmri = tio.ScalarImage(tensor=torch.rand(32, 128, 128, 88))
        >>> image = tio.ScalarImage('safe_image.nrrd', check_nans=False)
        >>> data, affine = image.data, image.affine
        >>> affine.shape
        (4, 4)
        >>> image.data is image[tio.DATA]
        True
        >>> image.data is image.tensor
        True
        >>> type(image.data)
        torch.Tensor

    See :class:`~torchio.Image` for more information.
    """
    def __init__(self, *args, **kwargs):
        if 'type' in kwargs and kwargs['type'] != INTENSITY:
            raise ValueError('Type of ScalarImage is always torchio.INTENSITY')
        kwargs.update({'type': INTENSITY})
        super().__init__(*args, **kwargs)

    def hist(self, **kwargs) -> None:
        """Plot histogram."""
        from ..visualization import plot_histogram
        x = self.data.flatten().numpy()
        plot_histogram(x, **kwargs)


class LabelMap(Image):
    """Image whose pixel values represent categorical labels.

    Example:
        >>> import torch
        >>> import torchio as tio
        >>> labels = tio.LabelMap(tensor=torch.rand(1, 128, 128, 68) > 0.5)
        >>> labels = tio.LabelMap('t1_seg.nii.gz')  # loading from a file
        >>> tpm = tio.LabelMap(                     # loading from files
        ...     'gray_matter.nii.gz',
        ...     'white_matter.nii.gz',
        ...     'csf.nii.gz',
        ... )

    Intensity transforms are not applied to these images.

    Nearest neighbor interpolation is always used to resample label maps,
    independently of the specified interpolation type in the transform
    instantiation.

    See :class:`~torchio.Image` for more information.
    """
    def __init__(self, *args, **kwargs):
        if 'type' in kwargs and kwargs['type'] != LABEL:
            raise ValueError('Type of LabelMap is always torchio.LABEL')
        kwargs.update({'type': LABEL})
        super().__init__(*args, **kwargs)

    def count_nonzero(self) -> int:
        """Get the number of voxels that are not 0."""
        return self.data.count_nonzero().item()

    def count_labels(self) -> Dict[int, int]:
        """Get the number of voxels in each label."""
        values_list = self.data.flatten().tolist()
        counter = Counter(values_list)
        counts = {label: counter[label] for label in sorted(counter)}
        return counts
