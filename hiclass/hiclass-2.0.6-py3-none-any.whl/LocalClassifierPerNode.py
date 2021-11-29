"""
Local classifier per node approach.

Numeric and string output labels are both handled.
"""
from itertools import repeat
from typing import Any, List, Tuple

import networkx as nx
import numpy as np

from hiclass.BinaryPolicies import Policy
from hiclass.Classifier import (
    DuplicateFilter,
    NodeClassifier,
    fit_or_replace,
)
from hiclass.data import NODE_TYPE


def _fit_classifier(
    node: NODE_TYPE,
    classifier: Any,
    policy: Policy,
    data: np.ndarray,
    replace_classifier: bool,
) -> Tuple[NODE_TYPE, Any, str]:
    """Fits a local classifier for a given node, policy and data.

    Parameters
    ----------
    node : int or str
        Node for which the classifier was fitted.
    classifier : Any
        The classifier that is assigned to the given node.
    policy : Policy
        Rules for defining positive and negative training samples.
    data : np.array
        The data that is being used for training the classifier.
    replace_classifier : bool
        Turns on (True) the replacement of classifiers with a constant classifier when trained on only
        a single unique label.

    Returns
    -------
    node : int or str
        Node for which the classifier was fitted.
    classifier : Any
        The classifier that was fitted for the given node.
    warning : str
        The warnings raised.
    """
    classes = np.zeros_like(policy.data, dtype=bool)
    positive_samples = policy.positive_samples(node)
    negative_samples = policy.negative_samples(node)
    all_samples = np.logical_or(positive_samples, negative_samples)
    classes[positive_samples] = 1

    classifier, warning = fit_or_replace(
        replace_classifier, classifier, data[all_samples], classes[all_samples], 2
    )
    return node, classifier, warning


class LocalClassifierPerNode(NodeClassifier):
    """
    Assign local classifiers to each node of the graph, except the root node.

    A local classifier per node is a local hierarchical classifier that fits one local binary classifier
    for each node of the class hierarchy, except for the root node.
    """

    def fit(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        placeholder_label=None,
        replace_classifiers=True,
    ) -> None:
        """
        Fit the local classifiers.

        Parameters
        ----------
        X : np.array of shape(n_samples, n_features)
            The training input samples.
        Y : np.array of shape (n_samples, n_levels)
            The hierarchical labels.
        placeholder_label : int or str, default=None
            Label that corresponds to "no label available for this data point". Defaults will be used if not passed.
        replace_classifiers : bool, default=True
            Turns on (True) the replacement of a local classifier with a constant classifier when trained on only
            a single unique class.
        """
        super().fit(X, Y, placeholder_label, replace_classifiers)

        duplicate_filter = DuplicateFilter()
        self.log.addFilter(duplicate_filter)  # removes possible duplicate warnings

        nodes = list(nx.dfs_preorder_nodes(self.hierarchy, self.root))
        nodes.remove(self.root)
        classifiers = [self.get_classifier(node) for node in nodes]
        fit_args = zip(
            nodes,
            classifiers,
            repeat(self.policy),
            repeat(X),
            repeat(replace_classifiers),
        )

        self._fit_classifier(_fit_classifier, fit_args)

        self.log.removeFilter(duplicate_filter)  # delete duplicate filter

    def _choose_required_prediction_args(
        self,
        local_identifier: NODE_TYPE,
        nodes_to_predict: List[NODE_TYPE],
        selected_rows: np.ndarray,
    ) -> Tuple[np.ndarray, List[NODE_TYPE]]:
        return selected_rows, nodes_to_predict

    def _create_prediction(
        self, data: np.ndarray, selected_rows: np.ndarray, nodes_to_predict: np.ndarray
    ) -> np.ndarray:
        predictions = np.empty(
            (len(nodes_to_predict), np.sum(selected_rows)), dtype=np.float32
        )
        for i in range(len(nodes_to_predict)):
            # take only the probability of true class
            classifier = self.get_classifier(nodes_to_predict[i])
            predictions[i] = self._predict_with_classifier(
                classifier, data[selected_rows]
            )[:, 1]
        return predictions

    def _get_nodes_with_classifier(self) -> List[NODE_TYPE]:
        return [x for x in self.hierarchy.nodes() if self.hierarchy.in_degree(x) != 0]
