try:
    from mlpractice_solutions.mlpractice_solutions.\
        linear_classifier_solution import softmax_with_cross_entropy
except ImportError:
    softmax_with_cross_entropy = None

import torch
import numpy as np


def test_all(softmax_with_cross_entropy=softmax_with_cross_entropy):
    test_public(softmax_with_cross_entropy)
    test_normalization(softmax_with_cross_entropy)
    test_random(softmax_with_cross_entropy, 100)
    print('All tests passed!')


def test_public(softmax_with_cross_entropy=softmax_with_cross_entropy):
    predictions = np.array([1, 2, 3])
    target_index = np.array([2])

    loss, d_predictions = softmax_with_cross_entropy(predictions, target_index)

    predictions_tensor = torch.from_numpy(predictions[np.newaxis, :]).float()
    predictions_tensor.requires_grad = True

    sample_loss = torch.nn.CrossEntropyLoss(reduction='sum')
    sample_output = sample_loss(predictions_tensor,
                                torch.from_numpy(target_index).long())
    sample_output.backward()

    assert abs(loss - sample_output) < 10 ** -6
    assert np.all(np.abs(d_predictions
                         - predictions_tensor.grad.numpy()) < 10 ** -6)


def test_normalization(softmax_with_cross_entropy=softmax_with_cross_entropy):
    predictions = np.array([0, 0, 10000])
    target_index = np.array([2])

    loss, d_predictions = softmax_with_cross_entropy(predictions, target_index)

    predictions_tensor = torch.from_numpy(predictions[np.newaxis, :]).float()
    predictions_tensor.requires_grad = True

    sample_loss = torch.nn.CrossEntropyLoss(reduction='sum')
    sample_output = sample_loss(predictions_tensor,
                                torch.from_numpy(target_index).long())
    sample_output.backward()

    assert abs(loss - sample_output) < 10 ** -6
    assert np.all(np.abs(d_predictions
                         - predictions_tensor.grad.numpy()) < 10 ** -6)


def test_random(softmax_with_cross_entropy=softmax_with_cross_entropy, iterations=1):
    np.random.seed(42)

    for _ in range(iterations):
        predictions = np.random.rand(3, 4)
        target_index = np.random.randint(0, 4, size=3)

        loss, d_predictions = softmax_with_cross_entropy(predictions,
                                                         target_index)

        predictions_tensor = torch.from_numpy(predictions).float()
        predictions_tensor.requires_grad = True

        sample_loss = torch.nn.CrossEntropyLoss(reduction='sum')

        sample_output = sample_loss(predictions_tensor,
                                    torch.from_numpy(target_index).long())
        sample_output.backward()

        assert abs(loss - sample_output) < 10 ** -6
        assert np.all(np.abs(d_predictions - predictions_tensor.grad.numpy()) <
                      10 ** -6)
