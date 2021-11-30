import numpy as np


def softmax(predictions):
    r"""Computes probabilities of belonging to each of the classes
    from scores.

    Parameters
    ----------
    predictions : ndarray, shape(n_classes) or shape(batch_size, n_classes)
        Classifier output.

    Returns
    -------
    probs : ndarray
        Array with probabilities of belonging to each of the classes,
        with the same shape as `predictions`.
    """
    # TODO: implement softmax
    # Your final implementation shouldn't have any loops
    raise NotImplementedError('Not implemented!')


def cross_entropy_loss(probs, target_index):
    r"""Computes cross-entropy loss.

    Parameters
    ----------
    probs : ndarray, shape(n_classes) or shape(batch_size, n_classes)
        Array with probabilities of belonging to each of the classes.
    target_index : ndarray, shape(1) or shape(batch_size)
        Index(indices) of the true class(es) for given sample(s).

    Returns
    -------
    loss : float
        Computed cross-entropy loss value.
    """
    # TODO: implement cross_entropy_loss
    # Your final implementation shouldn't have any loops
    raise NotImplementedError('Not implemented!')


def softmax_with_cross_entropy(predictions, target_index):
    r"""Computes softmax and cross-entropy loss for model predictions,
    including the gradient.

    Parameters
    ----------
    predictions : ndarray, shape(n_classes) or shape(batch_size, n_classes)
        Classifier output.
    target_index : ndarray, shape(1) or shape(batch_size)
        Index(indices) of the true class(es) for given sample(s).

    Returns
    -------
    loss : float
        Computed cross-entropy loss value.
    dpredictions : ndarray
        Array, with the same shape as `predictions`. Gradient of loss value
        with respect to predictions.
    """
    # TODO: implement softmax_with_cross_entropy
    # Your final implementation shouldn't have any loops
    raise NotImplementedError('Not implemented!')


def l2_regularization(W, reg_strength):
    r"""Computes L2 regularization loss on weights and its gradient.

    Parameters
    ----------
    W : ndarray, shape(n_features, n_classes)
        Weights.
    reg_strength : float
        Strength of regularization.

    Returns
    -------
    loss : float
        L2 regularization loss.
    gradient : ndarray, shape(n_features, n_classes)
        Gradient of L2 loss value with respect to weights.
    """
    # TODO: implement l2_regularization
    # Your final implementation shouldn't have any loops
    raise NotImplementedError('Not implemented!')


def linear_softmax(X, W, target_index):
    r"""Performs linear classification and returns loss and gradient
    with respect to W.

    Parameters
    ----------
    X : `ndarray`, shape(batch_size, n_features)
        Batch of images.
    W : `ndarray`, shape(n_features, n_classes)
        Weights.
    target_index : `ndarray`, shape(batch_size)
        Indices of the true classes for given samples.

    Returns
    -------
    loss : float
        Computed cross-entropy loss value.
    gradient : `ndarray`, shape(n_features, n_classes)
        Gradient of loss with respect to weights.
    """
    # TODO: implement linear_softmax
    # Your final implementation shouldn't have any loops
    predictions = X @ W
    raise NotImplementedError('Not implemented!')


class LinearSoftmaxClassifier:
    r"""Linear softmax classifier class.

    Attributes
    ----------
    W : ndarray
        Weights.
    """
    def __init__(self):
        self.W = None

    def fit(self, X, y, batch_size=100, learning_rate=1e-7,
            reg_strength=1e-5, epochs=1):
        r"""Trains linear classifier.

        Parameters
        ----------
            X : ndarray, shape(n_samples, n_features)
                Training data.
            y : ndarray, shape(n_samples)
                Training data class labels.
            batch_size : int, optional
                The number of samples to use for each batch.
            learning_rate : float, optional
                Learning rate for gradient descent.
            reg_strength : float, optional
                L2 regularization strength.
            epochs : int, optional
                The number of passes over the training data.

        Returns
        -------
            loss_history : array_like
        `loss_history` holds a record of the loss values during training.
        """
        n_train = X.shape[0]
        n_features = X.shape[1]
        n_classes = np.max(y) + 1
        if self.W is None:
            self.W = 0.001 * np.random.randn(n_features, n_classes)

        loss_history = []
        for epoch in range(epochs):
            shuffled_indices = np.arange(n_train)
            np.random.shuffle(shuffled_indices)
            sections = np.arange(batch_size, n_train, batch_size)
            batches_indices = np.array_split(shuffled_indices, sections)

            # TODO: implement generating batches from indices;
            #       compute loss and gradients;
            #       apply gradient to weights using learning rate;
            #       don't forget to add both cross-entropy loss
            #       and regularization!

            # end
            raise NotImplementedError('Not implemented!')
            print(f'Epoch: {epoch}, loss: {loss}')

        return loss_history

    def predict(self, X):
        r"""Predicts classes for `X`.

        Parameters
        ----------
            X : ndarray, shape(n_samples, n_features)
                The input samples.

        Returns
        -------
            y_pred : ndarray, shape(n_samples)
        The predicted classes.
        """
        # TODO: Implement predict
        # Your final implementation shouldn't have any loops
        raise NotImplementedError('Not implemented!')
