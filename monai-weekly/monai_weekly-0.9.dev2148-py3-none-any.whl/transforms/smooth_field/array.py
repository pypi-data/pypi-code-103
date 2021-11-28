# Copyright 2020 - 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Transforms using a smooth spatial field generated by interpolating from smaller randomized fields."""

from typing import Any, Optional, Sequence, Union

import numpy as np

import monai
from monai.transforms.spatial.array import Resize
from monai.transforms.transform import Randomizable, RandomizableTransform, Transform
from monai.transforms.utils import rescale_array
from monai.utils import InterpolateMode, ensure_tuple
from monai.utils.enums import TransformBackends
from monai.utils.type_conversion import convert_to_dst_type

__all__ = ["SmoothField", "RandSmoothFieldAdjustContrast", "RandSmoothFieldAdjustIntensity"]


class SmoothField(Randomizable):
    """
    Generate a smooth field array by defining a smaller randomized field and then resizing to the desired size. This
    exploits interpolation to create a smoothly varying field used for other applications.

    Args:
        spatial_size: final output size of the array
        rand_size: size of the randomized field to start from
        padder: optional transform to add padding to the randomized field
        mode: interpolation mode to use when upsampling
        align_corners: if True align the corners when upsampling field
        low: low value for randomized field
        high: high value for randomized field
        channels: number of channels of final output
    """

    def __init__(
        self,
        spatial_size: Union[Sequence[int], int],
        rand_size: Union[Sequence[int], int],
        padder: Optional[Transform] = None,
        mode: Union[InterpolateMode, str] = InterpolateMode.AREA,
        align_corners: Optional[bool] = None,
        low: float = -1.0,
        high: float = 1.0,
        channels: int = 1,
    ):
        self.resizer: Transform = Resize(spatial_size, mode=mode, align_corners=align_corners)
        self.rand_size: tuple = ensure_tuple(rand_size)
        self.padder: Optional[Transform] = padder
        self.field: Optional[np.ndarray] = None
        self.low: float = low
        self.high: float = high
        self.channels: int = channels

    def randomize(self, data: Optional[Any] = None) -> None:
        self.field = self.R.uniform(self.low, self.high, (self.channels,) + self.rand_size)  # type: ignore
        if self.padder is not None:
            self.field = self.padder(self.field)

    def __call__(self):
        resized_field = self.resizer(self.field)

        return rescale_array(resized_field, self.field.min(), self.field.max())


class RandSmoothFieldAdjustContrast(RandomizableTransform):
    """
    Randomly adjust the contrast of input images by calculating a randomized smooth field for each invocation. This
    uses SmoothFieldAdjustContrast and SmoothField internally.

    Args:
        spatial_size: size of input array's spatial dimensions
        rand_size: size of the randomized field to start from
        padder: optional transform to add padding to the randomized field
        mode: interpolation mode to use when upsampling
        align_corners: if True align the corners when upsampling field
        prob: probability transform is applied
        gamma: (min, max) range for exponential field
    """

    backend = [TransformBackends.TORCH, TransformBackends.NUMPY]

    def __init__(
        self,
        spatial_size: Union[Sequence[int], int],
        rand_size: Union[Sequence[int], int],
        padder: Optional[Transform] = None,
        mode: Union[InterpolateMode, str] = InterpolateMode.AREA,
        align_corners: Optional[bool] = None,
        prob: float = 0.1,
        gamma: Union[Sequence[float], float] = (0.5, 4.5),
    ):
        super().__init__(prob)

        if isinstance(gamma, (int, float)):
            self.gamma = (0.5, gamma)
        else:
            if len(gamma) != 2:
                raise ValueError("Argument `gamma` should be a number or pair of numbers.")

            self.gamma = (min(gamma), max(gamma))

        self.sfield = SmoothField(spatial_size, rand_size, padder, mode, align_corners, self.gamma[0], self.gamma[1])

    def set_random_state(
        self, seed: Optional[int] = None, state: Optional[np.random.RandomState] = None
    ) -> "RandSmoothFieldAdjustContrast":
        super().set_random_state(seed, state)
        self.sfield.set_random_state(seed, state)
        return self

    def randomize(self, data: Optional[Any] = None) -> None:
        super().randomize(None)

        if self._do_transform:
            self.sfield.randomize()

    def __call__(self, img: np.ndarray, randomize: bool = True):
        """
        Apply the transform to `img`, if `randomize` randomizing the smooth field otherwise reusing the previous.
        """
        if randomize:
            self.randomize()

        if not self._do_transform:
            return img

        img_min = img.min()
        img_max = img.max()
        img_rng = img_max - img_min

        field = self.sfield()
        field, *_ = convert_to_dst_type(field, img)

        img = (img - img_min) / max(img_rng, 1e-10)  # rescale to unit values
        img = img ** field  # contrast is changed by raising image data to a power, in this case the field

        out = (img * img_rng) + img_min  # rescale back to the original image value range

        out, *_ = convert_to_dst_type(out, img, img.dtype)

        return out


class RandSmoothFieldAdjustIntensity(RandomizableTransform):
    """
    Randomly adjust the intensity of input images by calculating a randomized smooth field for each invocation. This
    uses SmoothField internally.

    Args:
        spatial_size: size of input array
        rand_size: size of the randomized field to start from
        padder: optional transform to add padding to the randomized field
        mode: interpolation mode to use when upsampling
        align_corners: if True align the corners when upsampling field
        prob: probability transform is applied
        gamma: (min, max) range of intensity multipliers
    """

    backend = [TransformBackends.TORCH, TransformBackends.NUMPY]

    def __init__(
        self,
        spatial_size: Union[Sequence[int], int],
        rand_size: Union[Sequence[int], int],
        padder: Optional[Transform] = None,
        mode: Union[monai.utils.InterpolateMode, str] = monai.utils.InterpolateMode.AREA,
        align_corners: Optional[bool] = None,
        prob: float = 0.1,
        gamma: Union[Sequence[float], float] = (0.1, 1.0),
    ):
        super().__init__(prob)

        if isinstance(gamma, (int, float)):
            self.gamma = (0.5, gamma)
        else:
            if len(gamma) != 2:
                raise ValueError("Argument `gamma` should be a number or pair of numbers.")

            self.gamma = (min(gamma), max(gamma))

        self.sfield = SmoothField(spatial_size, rand_size, padder, mode, align_corners, self.gamma[0], self.gamma[1])

    def set_random_state(
        self, seed: Optional[int] = None, state: Optional[np.random.RandomState] = None
    ) -> "RandSmoothFieldAdjustIntensity":
        super().set_random_state(seed, state)
        self.sfield.set_random_state(seed, state)
        return self

    def randomize(self, data: Optional[Any] = None) -> None:
        super().randomize(None)

        if self._do_transform:
            self.sfield.randomize()

    def __call__(self, img: np.ndarray, randomize: bool = True):
        """
        Apply the transform to `img`, if `randomize` randomizing the smooth field otherwise reusing the previous.
        """

        if randomize:
            self.randomize()

        if not self._do_transform:
            return img

        img_min = img.min()
        img_max = img.max()

        field = self.sfield()
        rfield, *_ = convert_to_dst_type(field, img)

        out = img * rfield
        out, *_ = convert_to_dst_type(out, img, img.dtype)

        return out
