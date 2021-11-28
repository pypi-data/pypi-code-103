# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Contains the spatial dropout layers."""

# pylint: disable=g-classes-have-attributes,g-direct-tensorflow-import,g-bad-import-order
import tensorflow.compat.v2 as tf
# pylint: enable=g-bad-import-order

import keras.backend as K
from keras.engine.input_spec import InputSpec
from keras.layers.core.dropout import Dropout

from tensorflow.python.util.tf_export import keras_export


@keras_export('keras.layers.SpatialDropout1D')
class SpatialDropout1D(Dropout):
  """Spatial 1D version of Dropout.

  This version performs the same function as Dropout, however, it drops
  entire 1D feature maps instead of individual elements. If adjacent frames
  within feature maps are strongly correlated (as is normally the case in
  early convolution layers) then regular dropout will not regularize the
  activations and will otherwise just result in an effective learning rate
  decrease. In this case, SpatialDropout1D will help promote independence
  between feature maps and should be used instead.

  Args:
    rate: Float between 0 and 1. Fraction of the input units to drop.
  Call arguments:
    inputs: A 3D tensor.
    training: Python boolean indicating whether the layer should behave in
      training mode (adding dropout) or in inference mode (doing nothing).
  Input shape:
    3D tensor with shape: `(samples, timesteps, channels)`
  Output shape: Same as input.
  References: - [Efficient Object Localization Using Convolutional
      Networks](https://arxiv.org/abs/1411.4280)
  """

  def __init__(self, rate, **kwargs):
    super(SpatialDropout1D, self).__init__(rate, **kwargs)
    self.input_spec = InputSpec(ndim=3)

  def _get_noise_shape(self, inputs):
    input_shape = tf.shape(inputs)
    noise_shape = (input_shape[0], 1, input_shape[2])
    return noise_shape


@keras_export('keras.layers.SpatialDropout2D')
class SpatialDropout2D(Dropout):
  """Spatial 2D version of Dropout.

  This version performs the same function as Dropout, however, it drops
  entire 2D feature maps instead of individual elements. If adjacent pixels
  within feature maps are strongly correlated (as is normally the case in
  early convolution layers) then regular dropout will not regularize the
  activations and will otherwise just result in an effective learning rate
  decrease. In this case, SpatialDropout2D will help promote independence
  between feature maps and should be used instead.

  Args:
    rate: Float between 0 and 1. Fraction of the input units to drop.
    data_format: 'channels_first' or 'channels_last'. In 'channels_first' mode,
      the channels dimension (the depth) is at index 1, in 'channels_last' mode
      is it at index 3. It defaults to the `image_data_format` value found in
      your Keras config file at `~/.keras/keras.json`. If you never set it, then
      it will be "channels_last".
  Call arguments:
    inputs: A 4D tensor.
    training: Python boolean indicating whether the layer should behave in
      training mode (adding dropout) or in inference mode (doing nothing).
  Input shape:
    4D tensor with shape: `(samples, channels, rows, cols)` if
      data_format='channels_first'
    or 4D tensor with shape: `(samples, rows, cols, channels)` if
      data_format='channels_last'.
  Output shape: Same as input.
  References: - [Efficient Object Localization Using Convolutional
      Networks](https://arxiv.org/abs/1411.4280)
  """

  def __init__(self, rate, data_format=None, **kwargs):
    super(SpatialDropout2D, self).__init__(rate, **kwargs)
    if data_format is None:
      data_format = K.image_data_format()
    if data_format not in {'channels_last', 'channels_first'}:
      raise ValueError(
          f'`data_format` must be "channels_last" or "channels_first". '
          f'Received: data_format={data_format}.')
    self.data_format = data_format
    self.input_spec = InputSpec(ndim=4)

  def _get_noise_shape(self, inputs):
    input_shape = tf.shape(inputs)
    if self.data_format == 'channels_first':
      return (input_shape[0], input_shape[1], 1, 1)
    elif self.data_format == 'channels_last':
      return (input_shape[0], 1, 1, input_shape[3])


@keras_export('keras.layers.SpatialDropout3D')
class SpatialDropout3D(Dropout):
  """Spatial 3D version of Dropout.

  This version performs the same function as Dropout, however, it drops
  entire 3D feature maps instead of individual elements. If adjacent voxels
  within feature maps are strongly correlated (as is normally the case in
  early convolution layers) then regular dropout will not regularize the
  activations and will otherwise just result in an effective learning rate
  decrease. In this case, SpatialDropout3D will help promote independence
  between feature maps and should be used instead.

  Args:
    rate: Float between 0 and 1. Fraction of the input units to drop.
    data_format: 'channels_first' or 'channels_last'. In 'channels_first' mode,
      the channels dimension (the depth) is at index 1, in 'channels_last' mode
      is it at index 4. It defaults to the `image_data_format` value found in
      your Keras config file at `~/.keras/keras.json`. If you never set it, then
      it will be "channels_last".
  Call arguments:
    inputs: A 5D tensor.
    training: Python boolean indicating whether the layer should behave in
      training mode (adding dropout) or in inference mode (doing nothing).
  Input shape:
    5D tensor with shape: `(samples, channels, dim1, dim2, dim3)` if
      data_format='channels_first'
    or 5D tensor with shape: `(samples, dim1, dim2, dim3, channels)` if
      data_format='channels_last'.
  Output shape: Same as input.
  References: - [Efficient Object Localization Using Convolutional
      Networks](https://arxiv.org/abs/1411.4280)
  """

  def __init__(self, rate, data_format=None, **kwargs):
    super(SpatialDropout3D, self).__init__(rate, **kwargs)
    if data_format is None:
      data_format = K.image_data_format()
    if data_format not in {'channels_last', 'channels_first'}:
      raise ValueError(
          f'`data_format` must be "channels_last" or "channels_first". '
          f'Received: data_format={data_format}.')
    self.data_format = data_format
    self.input_spec = InputSpec(ndim=5)

  def _get_noise_shape(self, inputs):
    input_shape = tf.shape(inputs)
    if self.data_format == 'channels_first':
      return (input_shape[0], input_shape[1], 1, 1, 1)
    elif self.data_format == 'channels_last':
      return (input_shape[0], 1, 1, 1, input_shape[4])
