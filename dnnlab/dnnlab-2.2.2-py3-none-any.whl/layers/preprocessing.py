# Copyright 2020 Tobias Höfer
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
# =============================================================================
"""A Preprocessor packages(on-device) the input pipeline specific preprocessing.
The key benefit to appending a Preprocessor Layer to a model is that it makes
your model portable. When all data preprocessing is part of the model, other
people can load and use your model without having to be aware of how each
feature is expected to be encoded & normalized. Your inference model will be
able to process raw images or raw structured data, and will not require users of
the model to be aware of the details of e.g. the tokenization scheme used for
text, the indexing scheme used for categorical features, whether image pixel
values are normalized to [-1, +1] or to [0, 1], etc. This is especially powerful
if you're exporting your model to another runtime, such as TensorFlow.js: you
won't have to reimplement your preprocessing pipeline in JavaScript.

If you initially put your preprocessing layers in your tf.data pipeline, you can
export an inference model that packages the preprocessing. Simply instantiate
a new model that chains your preprocessing layers and your training model.

Crucially, these layers are non-trainable. Their state is not set during
training; it must be set before training, a step called "adaptation".
"""
from typing import List, Tuple
import tensorflow as tf


class Preprocessor(tf.keras.layers.Layer):
    """Applies optinal cropping, optional resizing and rescaling.

    Packages the input specific image preprocessing. Used in conjunction with
    a Model to make it portable to other runtimes and make it on-device.
    With Keras preprocessing layers, you can build and export models that are
    truly end-to-end: models that accept raw images or raw structured data as
    input; models that handle feature normalization or feature value indexing on
    their own."""
    def __init__(self,
                 height: int,
                 width: int,
                 interpolation: str = "bilinear",
                 scale: float = 1. / 127.5,
                 offset: float = -1,
                 cropping: Tuple[Tuple] = None):
        """ Defaults to bilinear resizing and [-1, 1] scale.

        To rescale an input to be in the [-1, 1] range, you would pass:
            scale = 1./127.5 and offset = -1.

        To rescale an input to be in the [0, 1] range, you would pass:
            scale = 1./255. and offset = 0.

        To rescale an input to be in the [0, 255] range, you would pass:
            scale = 1. and offset = 0.

        Args:
            height: New image height. If either height or width is set to None,
                images will keep its original size.
            width: New image width.
            interpolation: Resizing Method.
            scale: Rescale factor.
            offset: Used to shift pixel range.
            cropping:Int, or tuple of 2 ints, or tuple of 2 tuples of 2 ints.
              - If int: the same symmetric cropping
                is applied to height and width.
              - If tuple of 2 ints:
                interpreted as two different
                symmetric cropping values for height and width:
                `(symmetric_height_crop, symmetric_width_crop)`.
              - If tuple of 2 tuples of 2 ints:
                interpreted as
                `((top_crop, bottom_crop), (left_crop, right_crop))`
        """
        super(Preprocessor, self).__init__()
        self.height = height
        self.width = width
        self.interpolation = interpolation
        self.scale = scale
        self.offset = offset
        self.cropping = cropping

    def call(self, input):
        # Scale to [0, 255] using min-max normalization.
        x = tf.math.divide(
            tf.math.subtract(input, tf.reduce_min(input)),
            tf.math.subtract(tf.reduce_max(input),
                             tf.reduce_min(input))) * 255.

        # 2D Cropping.
        if self.cropping is not None:
            x = tf.keras.layers.Cropping2D(self.cropping)(x)

        # Resize using given interpolation method.
        if self.height or self.width is not None:
            x = tf.keras.layers.Resizing(self.height, self.width,
                                         self.interpolation)(x)
        # Rescaling pixel values...
        x = tf.keras.layers.Rescaling(self.scale, self.offset)(x)
        return x
