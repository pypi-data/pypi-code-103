r"""This is the first task of the mlpractice package.

You should fill in the gaps in the given function templates.
"""
from .linear_classifier import (
    softmax,
    cross_entropy_loss,
    softmax_with_cross_entropy,
    l2_regularization,
    linear_softmax,
    LinearSoftmaxClassifier
)

__all__ = [
    "softmax",
    "cross_entropy_loss",
    "softmax_with_cross_entropy",
    "l2_regularization",
    "linear_softmax",
    "LinearSoftmaxClassifier"
]
