import tensorflow as tf


class DGCNN(tf.keras.layers.Layer):
    """DGCNN layer"""

    def __init__(self, filter_size, window=3, dilation_rate=1, name='dilation_conv', **kwargs):
        """

        :param filter_size: vocab hidden size
        :param window: the high of filter, default 3
        :param dilation_rate: the dilation rate to use for dilated convolution, default 1
        """
        super().__init__(**kwargs)

        self.conv1 = tf.keras.layers.Conv1D(filter_size, window, dilation_rate=dilation_rate, padding='SAME',
                                            name=f'{name}_1')
        self.conv2 = tf.keras.layers.Conv1D(filter_size, window, dilation_rate=dilation_rate, activation=tf.sigmoid,
                                            padding='SAME', name=f'{name}_2')
        self.LayerNorm = tf.keras.layers.LayerNormalization(name=f'{name}_LayerNorm')

    def call(self, inputs, **kwargs):
        x1 = self.conv1(inputs)
        x1 = tf.subtract(x1, inputs)

        x2 = self.conv2(inputs)
        x = inputs + tf.multiply(x1, x2)

        x = self.LayerNorm(x)

        return x
