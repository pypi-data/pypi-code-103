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
"""A custom keras.callbacks.Callback to log images of image/label-datasets
in Tensorboard during model training.

The callback can be used by setting the callbacks-parameter of the
model.fit(...) method.
"""
from typing import List, Tuple

import io
from random import randrange

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

import tensorflow as tf
from dnnlab.interpretability.grad_cam import GradCam


class TensorboardImageCallback(tf.keras.callbacks.Callback):
    """Enables visualization of input images from a given dataset in Tensorboard
    with optional groundtruth label and prediction.

    This callback logs events for TensorBoard, including:
      * Abitrary/Specific image(s) of given dataset
      * Groundtruth label and model prediction (optional)
      * GradCam version of the input image (optional)

    Examples:
      Basic usage:
      ```python
      tb_img_cb = TensorboardImageLabelCallback(log_dir="./logs", train_dataset,
          grad_cam=True, cmap='gray')
      model.fit(x_train, y_train, epochs=2, callbacks=[tb_img_cb])
      ```
    """

    def __init__(self, log_dir: str, tf_dataset: tf.data.Dataset,
                 images_mode: str = 'random', show_prediction: bool = True,
                 grad_cam: bool = False, cmap: str = None):
        """ Defaults to log an image of the dataset and its groundtruth
        and prediction at each epoch.

        Args:
            log_dir: The path of the directory where to save the
            log files to be parsed by TensorBoard. This directory
            should not be reused by any other callbacks.
            tf_dataset: An image-label tf.data.Dataset.
            images_mode: Valid values are 'random' (default),
            'same' and 'batch'.
                If set to 'random' a random image is logged on
                each epoch.
                If set to 'same' always the first image of the
                dataset is logged at each epoch.
                If set to 'batch' the images of the first batch
                of the dataset is logged at each epoch.
            show_prediction: True if groundtruth label and
            prediction should be added below the plotted image.
            False if only the image should be plotted. Default is True.
            grad_cam: Set to True if the gradCam version of a image
            should be logged instead.
            cmap: Colormap for matplotlib plotting of the input
            image. Default is None
        """
        self.log_dir = log_dir
        self.tf_dataset = tf_dataset
        self.images, self.labels = tuple(zip(*self.tf_dataset))
        self.images_mode = images_mode
        self.show_prediction = show_prediction
        self.grad_cam = grad_cam
        self.cmap = cmap
        self.tensorboard_file_writer = tf.summary.create_file_writer(
            self.log_dir)

    def create_gradcam_image(self, image, alpha=0.4):
        """Creates a GradCam (heatmap) image using the activations
        of the feature extractor's last layer.

        Args:
          image: Input image.
          alpha: Sets the transparency of the heatmap overlay.
          Default is 0.4.
        """
        # create heatmap
        gc = GradCam(model=self.model)
        heatmap = gc.compute_heatmap(
            image=tf.expand_dims(image, 0), target_class_idx=None)

        img = tf.keras.preprocessing.image.img_to_array(image)
        alpha = 0.01
        # rescale heatmap to values between [0, 255]
        heatmap = np.uint8(255 * heatmap)

        # create colormap
        jet = cm.get_cmap("jet")

        # only use RGB values of the colormap
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]

        # create an image with RGB colorized heatmap out of the colormap heatmap
        jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
        jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)

        # superimpose the heatmap on original image
        gradcam_image = jet_heatmap * alpha + img
        return tf.keras.preprocessing.image.array_to_img(gradcam_image)

    def plot_to_image(self, image, label, prediction):
        """Plots image with optional groundtruth label and prediction
        and converts it to a TF image.

        Args:
          image: Input image.
          label: The groundtruth label.
          prediction: The model prediction.
       Returns:
          TF image to log/draw in Tensorboard
        """
        figure = plt.figure(figsize=(10, 10))
        if self.grad_cam:
            gradcam_image = self.create_gradcam_image(image, alpha=0.01)
            plt.subplot(1, 2, 1)
            plt.imshow(image, cmap=self.cmap)
            plt.subplot(1, 2, 2)
            plt.imshow(gradcam_image)
        else:
            plt.imshow(image, cmap=self.cmap)
        if self.show_prediction:
            plt.figtext(0.5, 0.01, "True label:\n "
            + str(label) + "\nPredicted label:\n "
            + str(prediction), ha="center", fontsize=16)

        # Converts the matplotlib plot specified by 'figure' to
        # a PNG image and returns it. The supplied figure
        # is closed and inaccessible after this call.

        # Save the plot to a PNG in memory.
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        # Closing the figure prevents it from being displayed directly inside
        # the notebook.
        plt.close(figure)
        buf.seek(0)
        # Convert PNG buffer to TF image
        image = tf.image.decode_png(buf.getvalue(), channels=4)
        # Add the batch dimension
        image = tf.expand_dims(image, 0)
        return image

    def log_image(self, epoch):
        """Logs image in Tensorboard at each epoch.

        Args:
          epoch: Integer, index of epoch.
          logs: Dict. Currently no data is passed to this
          argument for this method but that may change in the future.
        """
        pred_images = list()
        # Max. number of images displayed in Tensorboard
        max_outputs = 12
        if self.images_mode == 'random':
            batch_idx = randrange(len(self.images))
            img_idx = randrange(len(self.images[0]))
            pred_image = self.plot_image_with_prediction(batch_idx, img_idx)
            pred_images.append(tf.squeeze(pred_image))
        elif self.images_mode == 'same':
            pred_image = self.plot_image_with_prediction(0, 0)
            pred_images.append(tf.squeeze(pred_image))
        elif self.images_mode == 'batch':
            batch_size = len(self.images[0])
            if len(self.images[0]) > max_outputs:
                batch_size = max_outputs
            for index in range(batch_size):
                pred_image = self.plot_image_with_prediction(0, index)
                pred_images.append(tf.squeeze(pred_image))

        # Log the pred_image as an image summary.
        with self.tensorboard_file_writer.as_default():
            tf.summary.image("Image Prediction", pred_images,
                             max_outputs=12, step=epoch)

    def plot_image_with_prediction(self, batch_index, img_index):
        """Plots image from dataset with true label and prediction overlay text

        Args:
          batch_index: Index of of batch within dataset.
          img_index: Index of image within batch
        """
        orig_image = self.images[batch_index][img_index]
        true_label = self.labels[batch_index][img_index].numpy()
        # add batch dimension
        image_with_batchdim = tf.expand_dims(
            self.images[batch_index][img_index], 0)
        prediction = self.model.predict(image_with_batchdim)
        pred_image = self.plot_to_image(orig_image, true_label, prediction)
        return pred_image

    def on_epoch_end(self, epoch, logs=None):
        """Called after each epoch from Tensorboard.

        Args:
          epoch: Integer, index of epoch.
          logs: Dict. Currently no data is passed to this
          argument for this method but that may change in the future.
        """
        self.log_image(epoch)
