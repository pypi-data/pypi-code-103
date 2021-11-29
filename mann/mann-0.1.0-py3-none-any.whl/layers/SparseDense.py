import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Layer

class SparseDense(Layer):

    def __init__(
            self,
            weight,
            bias = None,
            activation = None,
            **kwargs
    ):

        super(SparseDense, self).__init__(**kwargs)
        self.weight = weight
        self.bias = bias
        self.activation = tf.keras.activations.get(activation)

    @property
    def weight(self):
        return self._weight
    @weight.setter
    def weight(self, value):
        if not isinstance(value, tf.sparse.SparseTensor):
            try:
                value = np.asarray(value, dtype = 'float32')
                value = tf.sparse.from_dense(value)
            except:
                raise TypeError('Weights could not be coerced to sparse format')
        self._weight = value

    @property
    def bias(self):
        return self._bias
    @bias.setter
    def bias(self, value):
        if not isinstance(value, tf.sparse.SparseTensor):
            try:
                value = np.asarray(value, dtype = 'float32')
                value = tf.sparse.from_dense(value)
            except:
                raise TypeError('Bias could not be coerced to sparse format')
        self._bias = value
        
    def call(self, inputs):
        ret_val = tf.sparse.sparse_dense_matmul(inputs, self.weight)
        if self.bias is not None:
            ret_val += tf.sparse.to_dense(self.bias)
        return self.activation(ret_val)

    def get_config(self):
        config = super().get_config().copy()
        config.update(
            {
                'weight' : tf.sparse.to_dense(self.weight).numpy().tolist(),
                'bias' : tf.sparse.to_dense(self.bias).numpy().tolist(),
                'activation' : tf.keras.activations.serialize(self.activation),
            }
        )
        return config
