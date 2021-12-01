"""Copyright Alpine Intuition Sàrl team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import io

import numpy as np
from PIL import Image


def serialize_img(array: np.ndarray) -> bytes:
    """Serialize a numpy array into bytes."""
    if array.max() > 255:
        raise ValueError("Can only serialize 8bits images")
    if array.dtype != "uint8":
        raise ValueError(f"Array dtype must be 'uint8', got '{array.dtype}'")
    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, format="png")
    return buffer.getvalue()


def deserialize_img(serialized_array: bytes) -> np.ndarray:
    """Serialize a bytes variable into numpy array."""
    decoded_array = Image.open(io.BytesIO(bytearray(serialized_array)))
    if decoded_array is None:
        raise ValueError("Fail to decode serialized array")
    return np.array(decoded_array)
