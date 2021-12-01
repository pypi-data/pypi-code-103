# Copyright 2019 Tobias Höfer
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
"""The code is written using the Keras Model API with a tf.GradientTape
training loop. This module implements an image-to-image training loop using
different losses such as MSE, MAE, SSIM.

In an image-to-image task one can choose between generative models or
mse-based Models. Generative models such as cGANs cycle GANs use an adversarial
loss resulting from a minmax game to learn the mapping. In contrast, mse-based
models solve a numerical optimization problem using gradient descent. MSE-based
models can choose from a set of different loss functions described in:
    - Loss Functions for Image Restoration with Neural Networks. (title)
"""
import logging
import os
import time
from datetime import datetime

import tensorflow as tf

from dnnlab.errors.dnnlab_exceptions import ModelNotCompiledError

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # FATAL
logging.getLogger("tensorflow").setLevel(logging.FATAL)


class NN():
    """Implements a mse-based CNN learning model used for image-to-image
    translation.

        Typical usage example:

        model -> keras.model transforming inputs to outputs.

        # Define forward path.
        nn = NN(model)

        # Define backward path. You can choose from different optimizers and
        # loss functions.
        nn.compile()

        # Start training process.
        nn.fit(train_dataset, valid_dataset, ...)

        # Export  model.
        nn.export()

        use nn.restore("relative_path_to_logs") to continue training after
        a break.

    Attributes:
        model: keras.model. Keras NN transforming inputs to outputs.
        alpha. Float between 0,1. Interpolation weight for combined losses.
    """
    def __init__(self, model, alpha=0.84):
        """ Inits nn with ckpt managers and loggers for tensorboard. alpha
        defaults to 0.84 as suggested by the authors."""
        self.model = model
        self.loss = None
        self.loss_objective = None
        self.optimizer = None
        self.alpha = alpha
        self.init_timestamp = "CNN-" + datetime.now().strftime("%d%m%Y-%H%M%S")
        self.logdir = os.path.join("logs", self.init_timestamp)
        self.tensorboard = os.path.join(self.logdir, "tensorboard")
        self.ckpt_dir = os.path.join(self.logdir, "ckpts")
        self.ckpt_manager = None
        self.checkpoint = None

    @staticmethod
    def _ssim_loss(labels, prediction):
        """Structural similarity index. SSIM evaluates images accounting for the
        fact that the HVS is sensitice to changes in local structure.
        Experimental results have shown the superiority of SSIM-based indexes
        over MSE(l2). As a consequence, SSIM has benn widely employed as a
        metric to evaluate image processing algorithms. Moreover, given that it
        can be used as a differnatial cost function, ssim is an alternative
        choice of loss for image-to-image translation. SSIM has a inverse
        relationship to MSE which means we use DSSIM = 1 - SSIM as a loss
        function to minimize. TODO validate calculation.
        """
        ssim = tf.reduce_mean(
            tf.image.ssim(prediction,
                          labels,
                          max_val=tf.math.reduce_max(labels)))
        dssim = 1 - ssim
        return dssim

    def _ssim_l1_loss(self, labels, prediction):
        """By design, both MS-SSIM and SSIM are not particularly sensitive to
        uniform biases. This can cause changes of brightness or shifts of colors
        , which typically become more dull. However, MS-SSIM and SSIM preserves
        the contrast in high-frequency regions better that the other loss
        functions. To caputre the best of characteristics of both l1 and SSIM,
        we propose to combine them.
        """
        ssim = tf.reduce_mean(
            tf.image.ssim(prediction,
                          labels,
                          max_val=tf.math.reduce_max(labels)))
        dssim = 1 - ssim

        l1 = tf.keras.losses.MeanAbsoluteError()
        dssim_l1 = self.alpha * dssim + (1 - self.alpha) * l1(
            prediction, labels)
        return dssim_l1

    def _ssim_l2_loss(self, labels, prediction):
        """By design, both MS-SSIM and SSIM are not particularly sensitive to
        uniform biases. This can cause changes of brightness or shifts of colors
        , which typically become more dull. However, MS-SSIM and SSIM preserves
        the contrast in high-frequency regions better that the other loss
        functions. To caputre the best of characteristics of both l2 and SSIM,
        we propose to combine them.
        """
        ssim = tf.reduce_mean(
            tf.image.ssim(prediction,
                          labels,
                          max_val=tf.math.reduce_max(labels)))
        dssim = 1 - ssim

        l2 = tf.keras.losses.MeanSquaredError()
        dssim_l2 = self.alpha * dssim + (1 - self.alpha) * l2(
            prediction, labels)
        return dssim_l2

    @staticmethod
    def _ssim(labels, prediction):
        """Used to evaluate image quality in evaluate()"""
        ssim = tf.reduce_mean(
            tf.image.ssim(prediction,
                          labels,
                          max_val=tf.math.reduce_max(labels)))
        return ssim

    def summary(self):
        """Returns a keras model summary on it underlying yolo model."""
        return self.model.summary()

    def predict(self, img):
        """Standard prediciton."""
        return self.model.predict(img)

    def compile(self, loss="l2", optimizer="adam", lr=1e-4,
                loss_scaling=False):
        """Defines the optimization part of the learning algorithm to our
        learning model. Choose between following loss functions:
            - l1 = mean absolute error (mae)
            - l2 = mean squared error (mse)
            - ssim = structural similarity loss function
            - ssim_l1 = ssim + l1
            - ssim_l2 = ssim + l2
            - TODO mssim = multiscale structural similarity
            - TODO mssim_l1 = mssim + l1
            - TODO mssim_l2 = mssim + l2

        Args:
            loss: String. Loss function to use.
            optimizer: String. Optimizer. Defaults to "adam".
            lr: Float. Learning rate. Defaults to 1e4.
            loss_scaling: Boolean. Loss scaling for mixed presicion.
                Defaults to False.
        """
        # Used for tb naming.
        self.loss = loss

        if self.loss == "l1":
            self.loss_objective = tf.keras.losses.MeanAbsoluteError()
        elif self.loss == "l2":
            self.loss_objective = tf.keras.losses.MeanSquaredError()
        elif self.loss == "ssim":
            self.loss_objective = self._ssim_loss
        elif self.loss == "ssim_l1":
            self.loss_objective = self._ssim_l1_loss
        elif self.loss == "ssim_l2":
            self.loss_objective = self._ssim_l2_loss

        if optimizer == "adadelta":
            self.optimizer = tf.keras.optimizers.Adadelta(lr)
        elif optimizer == "adagrad":
            self.optimizer = tf.keras.optimizers.Adagrad(lr)
        elif optimizer == "adam":
            self.optimizer = tf.keras.optimizers.Adam(lr)
        elif optimizer == "adamax":
            self.optimizer = tf.keras.optimizers.Adamax(lr)
        elif optimizer == "ftrl":
            self.optimizer = tf.keras.optimizers.Ftrl(lr)
        elif optimizer == "nadam":
            self.optimizer = tf.keras.optimizers.Nadam(lr)
        elif optimizer == "rmsprop":
            self.optimizer = tf.keras.optimizers.RMSprop(lr)
        elif optimizer == "sgd":
            self.optimizer = tf.keras.optimizers.SGD(lr)

        if loss_scaling:
            self.optimizer = tf.keras.mixed_precision.LossScaleOptimizer(
                self.optimizer)

        if self.checkpoint is None:
            self.checkpoint = tf.train.Checkpoint(optimizer=self.optimizer,
                                                  model=self.model)
            self.ckpt_manager = tf.train.CheckpointManager(self.checkpoint,
                                                           self.ckpt_dir,
                                                           max_to_keep=5)

    def fit(self,
            training_data=None,
            validation_data=None,
            batch_size=None,
            epochs=1,
            len_dataset=None,
            save_ckpt=5,
            verbose=1,
            max_outputs=2,
            initial_step=0,
            mlflow=False):
        """Trains the  model for n EPOCHS. Saves ckpts every n EPOCHS.
        The training loop together with the optimization algorithm define the
        learning algorithm.

        Args:
            training_data: Training data. It should be:
              - A "tf.data" dataset. Should return a tuple of
                "(inputs, targets)"
            validation_data: Validation data. It should be:
              - A "tf.data" dataset. Should return a tuple of
                "(inputs, targets)"
            batch_size: Integer.
                Number of samples per gradient update, only used to build a
                keras progressbar. Datasets should generate batches.
            epochs: Integer. Number of epochs to train the model. An epoch is an
                iteration over the entire "x" and "y" data provided.
            save_ckpt: Integer. Save ckpts every n Epochs.
            verbose: 0, 1, or 2. Verbosity mode.
                0 = silent, 1 = progress bar, 2 = one line per epoch". Defaults
                to 1.
            max_outputs: Integer.  Number of images shown in TB per step.
                Defaults to 2.
            initial_step (int): Step at which to start training. Useful for
                resuming a previous run.
            mlflow: Boolean. Triggers mlflow tracking.

        Raises:
            ModelNotCompiledError: Raise if model is not compiled.
        """
        if self.optimizer is None:
            raise ModelNotCompiledError("use compile() first.")
        if mlflow:
            import mlflow  # pylint:disable=import-outside-toplevel

        # Retrace workaround @function signature only tensors.
        step = tf.Variable(initial_step, name="step", dtype=tf.int64)

        num_batches = len_dataset / batch_size

        # Keras Progbar and file writer setup.
        progbar = tf.keras.utils.Progbar(target=num_batches, verbose=verbose)
        file_writer = tf.summary.create_file_writer(self.tensorboard)
        eval_file_writer = tf.summary.create_file_writer(
            os.path.join(self.tensorboard, "eval"))
        file_writer.set_as_default()

        # Prepare the metrics.
        train_loss_avg = tf.keras.metrics.Mean()
        val_loss_avg = tf.keras.metrics.Mean()

        # Iterate over all epochs.
        for epoch in range(epochs):
            step_float = 1
            start = time.time()
            for examples in training_data:
                images = examples[0]
                labels = examples[1]
                # Performs a training step. Inference + BP and GD.
                prediction, loss = self.train_step(images, labels, batch_size,
                                                   step)

                train_loss_avg.update_state(loss)
                # TODO Workaround. summary image & gpu usage.
                with file_writer.as_default():  #pylint: disable=not-context-manager
                    tf.summary.scalar(self.loss, loss, step=step)
                    tf.summary.image("input",
                                     images,
                                     step=step,
                                     max_outputs=max_outputs)
                    tf.summary.image("prediction",
                                     prediction,
                                     step=step,
                                     max_outputs=max_outputs)
                    tf.summary.image("label",
                                     labels,
                                     step=step,
                                     max_outputs=max_outputs)

                file_writer.flush()
                progbar.update(current=(step_float))
                step_float += 1
                step.assign(step + 1)

            # Save the model every n epochs
            if (epoch + 1) % save_ckpt == 0:
                ckpt_save_path = self.ckpt_manager.save()
                print("\nSaving checkpoint for epoch {} at {}".format(
                    epoch + 1, ckpt_save_path))

            print(" - Epoch: {} - loss {}".format(
                epoch + 1, round(train_loss_avg.result().numpy().item(), 4)))

            print("Start validation loop...")
            for images, labels in validation_data:
                loss, _ = self.test_step(images, labels)
                val_loss_avg.update_state(loss)
            with eval_file_writer.as_default():
                tf.summary.scalar(self.loss, val_loss_avg.result(), step=step)
            eval_file_writer.flush()
            print(" - Epoch: {} - val_loss {}".format(
                epoch + 1, round(val_loss_avg.result().numpy().item(), 4)))

            if mlflow:
                import mlflow  # pylint:disable=import-outside-toplevel
                mlflow.log_metric("val_{}".format(self.loss),
                                  round(val_loss_avg.result().numpy().item(),
                                        4),
                                  step=epoch + 1)

            # Reset training metrics at the end of each epoch
            train_loss_avg.reset_states()
            val_loss_avg.reset_states()

    def restore(self, ckpt_path):
        """Restore model weights from the latest checkpoint.

        Args:
            ckpt_path (str): Relative path to ckpt files.

        Raises:
            ModelNotCompiledError: Raise if model is not compiled.
        """

        restore_path = os.path.dirname(ckpt_path)
        self.logdir = restore_path
        self.tensorboard = os.path.join(self.logdir, "tensorboard")
        self.ckpt_dir = os.path.join(self.logdir, "ckpts")
        if self.ckpt_manager is None:
            raise ModelNotCompiledError("use compile() first.")
        self.ckpt_manager = tf.train.CheckpointManager(self.checkpoint,
                                                       self.ckpt_dir,
                                                       max_to_keep=5)
        # if a checkpoint exists, restore the latest checkpoint.
        if self.ckpt_manager.latest_checkpoint:
            self.checkpoint.restore(self.ckpt_manager.latest_checkpoint)
            print("Latest checkpoint restored!!")
        else:
            print("Can not find ckpt files at {}".format(ckpt_path))

    def export(self, model_format="hdf5"):
        """Exports the trained models in hdf5 or SavedModel format.

        Args:
            model_format (str, optional): SavedModel or HDF5. Defaults to hdf5.
        """
        model_dir = os.path.join(self.logdir, "models")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        if model_format == "hdf5":
            self.model.save(os.path.join(model_dir, "backbone.h5"))
        elif model_format == "SavedModel":
            self.model.save(os.path.join(model_dir, "backbone"))

    @tf.function
    def train_step(self, images, labels, batch_size, step):
        """Decorated function (@tf.function) that creates a callable tensorflow
        graph from a python function. Performs an batch inference steps,
        calculates the gradient using BP and updates the trainable params
        using a predefined optimization technique.

        Args:
            images: Batch of input images.
            labels: Batch of labels.
            batch_size: Number of images in a batch.
            step: Actual training step.

        Returns:
            prediction: Batch of predictions.
            loss: Loss objective value (specified in __init__()).
        """
        with tf.GradientTape() as tape:
            # Predict
            start_time = time.time()
            prediction = self.model(images, training=True)
            end_time = time.time()
            img_per_second = (end_time - start_time) / batch_size
            tf.summary.scalar("inference_time[s]", img_per_second, step=step)

            # Loss
            loss = self.loss_objective(labels, prediction)

        # Calculate gradient.
        gradient = tape.gradient(loss, self.model.trainable_variables)

        # Apply gradient to weights.
        self.optimizer.apply_gradients(
            zip(gradient, self.model.trainable_variables))

        return prediction, loss

    @tf.function
    def test_step(self, images, labels):
        """Decorated function that creates a callable TensorFlow graph from a
        python function. Performs a batch inference step on the validation data.

        Args:
            images: Batch of input images.
            labels: Batch of labels.

        Returns:
            loss: Loss objective value (specified in __init__()).
        """
        prediction = self.model(images, training=False)
        loss = self.loss_objective(labels, prediction)
        return loss, prediction

    def evaluate(self, dataset):
        """Retruns the average mae, mse , ssim, mssim for evaluation purposes.

        Args:
            dataset: Test dataset.

        Returns:
            results: Dict containing all trainable metricies.
        """
        mae = tf.keras.losses.MeanAbsoluteError()
        mse = tf.keras.losses.MeanSquaredError()
        ssim = self._ssim
        # mssim = self._mssim_loss
        print("Start evaluation...")
        mae_metric = tf.keras.metrics.Mean()
        mse_metric = tf.keras.metrics.Mean()
        ssim_metric = tf.keras.metrics.Mean()
        #mssim_metric = tf.keras.metrics.Mean()
        for images, labels in dataset:
            _, prediction = self.test_step(images, labels)
            mae_metric.update_state(mae(labels, prediction))
            mse_metric.update_state(mse(labels, prediction))
            ssim_metric.update_state(ssim(labels, prediction))

        result = {
            "l1": float(mae_metric.result()),
            "l2": float(mse_metric.result()),
            "ssim": float(ssim_metric.result())
        }
        return result
