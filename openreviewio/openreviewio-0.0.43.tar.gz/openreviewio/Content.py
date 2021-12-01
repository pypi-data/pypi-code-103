# This file is part of openreviewio-py.
#
# openreviewio-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# openreviewio-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with openreviewio-py.  If not, see <https://www.gnu.org/licenses/>

from dataclasses import dataclass
from pathlib import Path
import toml
from typing import Union

from .base import ReviewItem


@dataclass
class TextComment(ReviewItem):
    body: str

    def __init__(self, body: str):
        """Text comment related to the whole media.

        :param body: Comment message
        :type body: str
        """
        super().__init__()

        self.body = body


@dataclass
class TextAnnotation(TextComment, ReviewItem):
    frame: int
    duration: int

    def __init__(self, body: str, frame: int, duration: int):
        super().__init__(body)

        self.frame = int(frame)
        self.duration = int(duration)


@dataclass
class Image(ReviewItem):

    __mime__ = {"jpeg", "jpg", "png"}
    path_to_image: Union[Path, str]

    def __init__(self, path_to_image: Union[Path, str]):
        """Image related to the whole media.

        :param path_to_image: Path to image file
        """
        super().__init__()

        self.path_to_image = Path(path_to_image)

        # Check mime for file extension
        if path_to_image:
            file = Path(self.path_to_image)
            if file.suffix.replace(".", "") not in self.__mime__:
                raise TypeError(
                    f"Image file '{file.suffix}' extension format is not valid. "
                    f"Please select either: {', '.join(sorted(self.__mime__))}."
                )


@dataclass
class ImageAnnotation(Image, ReviewItem):
    frame: int
    duration: int
    _reference_image = None
    reference_image: Union[Path, str, Image]

    def __init__(
        self,
        path_to_image: Union[Path, str],
        frame: int,
        duration: int,
        reference_image: Union[Path, str, Image] = "",
    ):
        """Image related to a frame and a duration of the media.

        :param path_to_image: Path to annotation image
        :param frame: Starting frame
        :type frame: int
        :param duration: Frames duration
        :type duration: int
        :param reference_image: Keep an image path as reference for the drawing
        """
        super(ImageAnnotation, self).__init__(path_to_image)

        self.frame = int(frame)
        self.duration = int(duration)

        self.reference_image = reference_image

    # reference image getter
    @property
    def reference_image(self):
        if self._reference_image:
            return self._reference_image.path_to_image
        else:
            return ""

    @reference_image.setter
    def reference_image(self, value):
        # Sentinel for reference image
        if value and value.__class__ is not Image:
            self._reference_image = Image(value)
