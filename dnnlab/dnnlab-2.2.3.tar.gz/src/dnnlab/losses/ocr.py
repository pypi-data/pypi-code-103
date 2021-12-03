# Copyright 2021 Tobias Höfer
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
"""This module tries to improve the reconstruction quality of neural nets using
a specificly weighted MSE function. Key pixels are within a certain neighborhood
of characters. Both the white and black pixels inside the neighborhood are
important because they represent information. All pixel outside this
neighborhood are considered background pixels. Most of the binary prescriptions
contain approximately 5 % black pixels (after resizing), and therefore only a
small subset of pixels contains actual information. A two-tier system is
advantageous, because if we detect all pixels of one class, the remaining pixels
belong to the other class."""
import tensorflow as tf


class OCRLoss(tf.keras.losses.Loss):
    """Weighted MSE Loss that weighs key pixel values in a defined neighborhood
    around characters higher than plain background pixel values. A key pixel
    contains information (black color) or is in its close neighbourhood. The
    label is preprocessed with a 2-D convolution and a box blur filter kernel.
    A box blurr computes each pixel as the average of the surrounding pixels."""

    def __init__(self,
                 neighbourhood: int = 9,
                 background_weight: float = 0.7,
                 sensitivity: float = 0.001,
                 **kwargs):
        """ Defaults to a 9x9 neighbourhood and a 1.0 / 0.7 weight different for
        key and background pixels.

        Args:
            neighbourhood: The filter size for the box blurr filter. This
                parameter defines the range of key pixels around a character.
            background_weight: The weight for every background pixel. Key pixels
                are weighted with 1.0.
            sensitivity: Do not mess with this parameter!

        """
        super(OCRLoss, self).__init__(**kwargs)
        self.neighbourhood = neighbourhood
        self.background_weight = background_weight
        self.sensitivity = sensitivity

    def call(self, y_true, y_pred):
        y_pred = tf.convert_to_tensor(y_pred)
        y_true = tf.cast(y_true, y_pred.dtype)

        # Box blurr filter.
        key_filter = tf.ones(shape=[self.neighbourhood, self.neighbourhood, 1],
                             dtype=tf.float32) * 1 / (self.neighbourhood**2)
        # Custom padding
        h_pad = tf.math.ceil(tf.cast((self.neighbourhood / 2) - 1, tf.float16))
        w_pad = tf.math.ceil(tf.cast((self.neighbourhood / 2) - 1, tf.float16))
        paddings = [[0, 0], [h_pad, h_pad], [w_pad, w_pad], [0, 0]]
        padded_y_true = tf.cast(tf.pad(y_true, paddings, "SYMMETRIC"),
                                tf.float32)
        # Correct dims for conv2d: (height, width, channel, batch)
        key_filter = tf.expand_dims(key_filter, axis=2)
        weights = tf.nn.conv2d(padded_y_true,
                               filters=key_filter,
                               strides=[1, 1, 1, 1],
                               padding="VALID")

        # Mask + Threshold -> Binarization
        mask = tf.ones(shape=[
            tf.shape(y_true)[0],
            tf.shape(y_true)[1],
            tf.shape(y_true)[2]
        ]) * (tf.cast(tf.reduce_max(y_true), weights.dtype) *
              (1.0 - self.sensitivity))
        mask = tf.expand_dims(mask, axis=-1)
        weights = (tf.cast(tf.math.less(weights, mask), dtype=tf.float32) *
                   (1.0 - self.background_weight)) + self.background_weight

        tf.summary.image("weights", weights)
        # Weighted MSE Loss.
        loss_fn = tf.keras.losses.MeanSquaredError(reduction=self.reduction)
        return loss_fn(y_true=y_true, y_pred=y_pred, sample_weight=weights)
