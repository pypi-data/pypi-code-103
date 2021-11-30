try:
    from mlpractice_solutions.mlpractice_solutions.\
        linear_classifier_solution import l2_regularization
except ImportError:
    l2_regularization = None

import numpy as np
import torch


def test_all(l2_regularization=l2_regularization):
    test_public(l2_regularization)
    test_default(l2_regularization)
    test_random(l2_regularization, 100)
    print('All tests passed!')


def test_public(l2_regularization=l2_regularization):
    weights = np.array([[0, 1],
                        [1, 0]])
    reg_strength = 0.5

    loss, grad = l2_regularization(weights, reg_strength)

    assert abs(loss - 1) < 10 ** -9
    assert np.all(np.abs(grad - weights) < 10 ** -8)


def test_default(l2_regularization=l2_regularization):
    weights = np.array([[1, 2],
                        [3, 4]])
    reg_strength = 0.5

    loss, grad = l2_regularization(weights, reg_strength)

    weights_tensor = torch.from_numpy(weights).float()
    weights_tensor.requires_grad = True

    sample_loss = reg_strength * torch.norm(weights_tensor) ** 2
    sample_loss.backward()
    sample_grad = weights_tensor.grad

    assert abs(loss - sample_loss) < 10 ** -6
    assert np.all(np.abs(grad - sample_grad.numpy()) < 10 ** -6)


def test_random(l2_regularization=l2_regularization, iterations=1):
    np.random.seed(42)

    for _ in range(iterations):
        weights = np.random.rand(3, 4)
        reg_strength = float(np.random.rand())

        loss, grad = l2_regularization(weights, reg_strength)

        weights_tensor = torch.from_numpy(weights).float()
        weights_tensor.requires_grad = True

        sample_loss = reg_strength * torch.norm(weights_tensor) ** 2
        sample_loss.backward()
        sample_grad = weights_tensor.grad

        assert abs(loss - sample_loss) < 10 ** -6
        assert np.all(np.abs(grad - sample_grad.numpy()) < 10 ** -6)
