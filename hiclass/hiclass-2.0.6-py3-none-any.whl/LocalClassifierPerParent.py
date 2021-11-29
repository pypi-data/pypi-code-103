"""
Local classifier per parent approach.

Numeric and string output labels are both handled.
"""

from itertools import repeat
from typing import Any, Tuple, Optional, Union

import networkx as nx
import numpy as np
from sklearn.base import BaseEstimator

from hiclass import BinaryPolicies
from hiclass.BinaryPolicies import Policy
from hiclass.Classifier import (
    DuplicateFilter,
    NodeClassifier,
    ConstantClassifier,
    fit_or_replace,
)
from hiclass.data import NODE_TYPE


def _fit_classifier(
    node: NODE_TYPE,
    classifier: Any,
    hierarchy: nx.DiGraph,
    policy: Policy,
    data: np.ndarray,
    replace_classifier: bool,
) -> Tuple[NODE_TYPE, Any, str]:
    """Fits a local classifier for a given node.

    Parameters
    ----------
    node : int or str
        Node for which the classifier was fitted.
    classifier : Any
        The classifier that is assigned to the given node.
    policy : Policy
        Rules for defining positive and negative training samples.
    data : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input samples. If a sparse matrix is provided, it will be
        converted into a sparse ``csc_matrix``.
    replace_classifier : bool
        Turns on (True) the replacement of classifiers with a constant classifier when trained on only
        a single unique class.

    Returns
    -------
    node : int or str
        Node for which the classifier was fitted.
    classifier : Any
        The classifier that was fitted for the given node.
    warning : str
        The warnings raised.
    """
    classes = np.zeros_like(policy.data, dtype=int)
    all_samples = np.zeros_like(policy.data, dtype=bool)

    successors = list(hierarchy.successors(node))
    mapping = dict(zip(successors, range(0, len(successors))))
    for successor in successors:
        positive_samples = policy.positive_samples(successor)
        classes[positive_samples] = mapping[successor]
        all_samples[positive_samples] = True

    classifier, warning = fit_or_replace(
        replace_classifier,
        classifier,
        data[all_samples],
        classes[all_samples],
        len(mapping),
    )
    return node, classifier, warning


class LocalClassifierPerParent(NodeClassifier):
    """
    Assign local classifiers to each parent node in a DAG.

    A local classifier per parent is a local hierarchical classifier that fits one local multi-class classifier
    for each node that has children. The labels correspond to its children.
    """

    def __init__(
        self,
        n_jobs: int = 1,
        verbose: int = 0,
        local_classifier: Any = BaseEstimator(),
        hierarchy: Optional[nx.DiGraph] = None,
        unique_taxonomy: bool = True
    ) -> None:
        """
        Initialize a classifier and set the :code:`policy` parameter of its superclass to :code:`SiblingsPolicy`.

        Parameters
        ----------
        n_jobs : int, default=1
            The number of jobs to run in parallel. Only `fit` is parallelized.
        verbose : int, default=0
            Controls the verbosity when fitting and predicting.
            See https://verboselogs.readthedocs.io/en/latest/readme.html#overview-of-logging-levels
            for more information.
        local_classifier : BaseEstimator instance
            The local classifier used to create the collection of local classifier. Needs to have fit, predict and clone
            methods.
        hierarchy : nx.DiGraph, default=None
            Label hierarchy used in prediction and fitting. If None, it will be inferred during training.
        unique_taxonomy : bool, default=True
            True if the elements in the hierarchy have unique names, otherwise it can have unexpected behaviour.
            For example, a->b->c and d->b->e could have different meanings for b, so in that case unique_taxonomy
            should be set to false.
        """
        super().__init__(
            n_jobs=n_jobs,
            verbose=verbose,
            local_classifier=local_classifier,
            hierarchy=hierarchy,
            unique_taxonomy=unique_taxonomy,
            policy=BinaryPolicies.SiblingsPolicy,
        )

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
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The training input samples. If a sparse matrix is provided, it will be
            converted into a sparse ``csc_matrix``.
        Y : array-like of shape (n_samples,) or (n_samples, n_outputs)
            The multi-class hierarchical labels.
        placeholder_label : int or str, default=None
            Label that corresponds to "no label available for this data point".
        replace_classifiers : bool, default=True
            Turns on (True) the replacement of classifiers with a constant classifier when trained on only
            a single unique class.
        """
        super().fit(X, Y, placeholder_label, replace_classifiers)

        duplicate_filter = DuplicateFilter()
        self.log.addFilter(duplicate_filter)  # removes possible duplicate warnings

        nodes = list(nx.dfs_preorder_nodes(self.hierarchy, self.root))
        leaf_nodes = [
            x for x in self.hierarchy.nodes() if self.hierarchy.out_degree(x) == 0
        ]
        for leaf in leaf_nodes:
            nodes.remove(leaf)
        classifiers = [self.get_classifier(node) for node in nodes]
        fit_args = zip(
            nodes,
            classifiers,
            repeat(self.hierarchy),
            repeat(self.policy),
            repeat(X),
            repeat(replace_classifiers),
        )
        self._fit_classifier(_fit_classifier, fit_args)

        self.log.removeFilter(duplicate_filter)  # delete duplicate filter

    def _create_prediction(
        self, data: np.ndarray, selected_rows: np.ndarray, parent_label: NODE_TYPE
    ) -> np.ndarray:
        classifier = self.get_classifier(parent_label)
        return self._predict_with_classifier(classifier, data[selected_rows]).T

    def _get_nodes_with_classifier(self):
        return [x for x in self.hierarchy.nodes() if self.hierarchy.out_degree(x) != 0]
