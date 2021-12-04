import numpy as np
import tensorflow as tf

class GCNLL(tf.keras.losses.Loss):
    '''
    Negative of the conditional log-likelihood of the
    multivariate Gaussian distribution.

    Attributes
    ----------
        name : str (default="gaussian_conditional_negative_log_likelihood")
            Name of the object.
        residuals : array-like[float]
            Errors of the model.
        cov : array-like[float]
            Estimated conditional covariance matrix.
        NLL : float
            Negative log-likelihood.

    Methods
    -------
        call : 
    '''

    def __init__(self):
        super().__init__()
        self.name = "gaussian_conditional_negative_log_likelihood"

    def call(self, y_true, y_pred):
        pi = tf.cast(np.pi, dtype=tf.float64)
        n = tf.shape(x, out_type=tf.int64)[1]
        n = tf.cast(n, dtype=tf.float64)
        m = tf.shape(x, out_type=tf.int64)[0]
        m = tf.cast(m, dtype=tf.float64) - 1.
        self.residuals = y_true - y_pred
        self.cov = tf.matmul(
            self.residuals,
            self.residuals,
            transpose_a=True
            )
        self.cov = self.cov / m
        cov_inv = tf.linalg.inv(self.cov)
        cov_det = tf.linalg.det(self.cov)
        self.NLL = n * tf.math.log(2 * pi)
        self.NLL = tf.math.log(cov_det) + self.NLL
        for row in self.residuals:
            prod = tf.tensordot(row, cov_inv, 1)
            prod = tf.tensordot(prod, row, 1)
            self.NLL = prod + self.NLL
        self.NLL = self.NLL / 2
        return self.NLL
