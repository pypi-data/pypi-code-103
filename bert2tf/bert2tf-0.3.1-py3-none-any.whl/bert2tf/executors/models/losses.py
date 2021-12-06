import tensorflow as tf
from tensorflow.python.keras.utils import losses_utils


class FocalLoss(tf.keras.losses.Loss):
    """
    Focal Loss
    """

    def __init__(self, alpha: float = 0.25, gamma: int = 2, *args, **kwargs):
        super(FocalLoss, self).__init__(*args, **kwargs)
        self.alpha = alpha
        self.gamma = gamma

    def call(self, y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, 1e-8, 1 - 1e-8)
        loss = -self.alpha * y_true * tf.math.log(y_pred) * (1 - y_pred) ** self.gamma - \
               (1 - self.alpha) * (1 - y_true) * tf.math.log(1 - y_pred) * y_pred ** self.gamma
        loss = tf.reduce_sum(loss, axis=1)

        return loss


class RDropLoss(tf.keras.losses.Loss):
    """
    R-Drop loss, it calculates two linked sample KL
    """

    def __init__(self, alpha: int = 4, *args, **kwargs):
        """

        :param alpha: loss amplification factor
        """
        super(RDropLoss, self).__init__(*args, **kwargs)
        self.alpha = alpha

    def call(self, y_true, y_pred):
        y_pred = tf.nn.softmax(y_pred)
        kl_loss = tf.losses.kullback_leibler_divergence(y_pred[::2],
                                                        y_pred[1::2]) + tf.losses.kullback_leibler_divergence(
            y_pred[1::2], y_pred[::2])
        kl_loss = tf.reduce_mean(kl_loss) / 2 * self.alpha

        return kl_loss


class MRCLoss(tf.keras.losses.Loss):
    """Machine reading comprehension loss layer"""

    def __init__(self, seq_length, custom_loss_fn=None, label_smoothing=0.01, **kwargs):
        super().__init__(**kwargs)
        self.seq_length = seq_length
        self.custom_loss_fn = custom_loss_fn
        self.label_smoothing = label_smoothing

    def call(self, y_true, y_pred):
        if self.custom_loss_fn is None:
            self.custom_loss_fn = tf.keras.losses.CategoricalCrossentropy(
                from_logits=True, reduction=losses_utils.ReductionV2.NONE, label_smoothing=self.label_smoothing)

        start_positions = tf.cast(y_true[0], tf.int32)
        end_positions = tf.cast(y_true[1], tf.int32)
        start_positions = tf.reshape(tf.one_hot(start_positions, depth=self.seq_length), [-1, self.seq_length])
        end_positions = tf.reshape(tf.one_hot(end_positions, depth=self.seq_length), [-1, self.seq_length])
        start_loss = self.custom_loss_fn(start_positions, y_pred[0])
        end_loss = self.custom_loss_fn(end_positions, y_pred[1])
        start_loss = tf.reduce_mean(start_loss)
        end_loss = tf.reduce_mean(end_loss)
        loss = start_loss + end_loss
        return loss / 2
