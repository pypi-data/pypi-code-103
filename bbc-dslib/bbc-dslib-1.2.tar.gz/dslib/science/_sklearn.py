import logging
import numpy as np
import os

from dslib.utils import log
from typing import Optional

try:
    import dill
    from sklearn.pipeline import Pipeline
    from sklearn.base import TransformerMixin, BaseEstimator
    from sklearn.metrics import roc_auc_score, average_precision_score, recall_score, precision_score, precision_recall_curve
    from matplotlib import pyplot as plt
except ImportError:
    raise ImportError(f'Please install "ml" extra package.')


def predict_with_threshold(clf, df, threshold):
    """
    Perform class prediction with given trained binary classifier and threshold
    :param clf: binary classifier to be used
    :param df: input dataframe to predict on
    :param threshold: threshold to be used for classification
    :return: the classes predicted
    """
    # Assert threshold value is valid
    assert 0 < threshold < 1, 'Your threshold must be in interval ]0,1['
    # Use the model to predict probabilities
    y_prob = clf.predict_proba(df)[:, 1]
    # Choose a class based on the probabilities and the threshold
    return np.abs(np.round(y_prob - (threshold - 0.5)))  # Cut-off moved from 0.5 to threshold


def eval_score(y_true: list, y_pred: list, plot_pr_curve: bool = True,
               threshold: bool = None, logger: Optional[logging.Logger] = None):
    """
    Returns ROC and average precision score as well as PR curve given a vector of scores and labels.
    Give precision and recall if a threshold is provided
    :param y_true: label
    :param y_pred: prediction score
    :param plot_pr_curve: if set to True, will display precision recall (PR) curve (optional - default: True)
    :param threshold: threshold (optional)
    :param logger: logger to use to output results. If None, will use print (optional - default: None)
    """
    auc = roc_auc_score(y_true, y_pred)
    aps = average_precision_score(y_true, y_pred)
    log(f'AUC = {auc:.5}', logger)
    log(f'Average precision score = {aps:.5}', logger)
    log(f'Data size: {len(y_true)}', logger)

    if plot_pr_curve:
        p_ret, r_ret, t_ret = precision_recall_curve(y_true, y_pred)
        plt.plot(r_ret, p_ret)

        plt.legend()
        plt.title('Precision-recall curve')
        plt.xlabel('Recall')
        plt.ylabel('Precision')

    if threshold:
        log(f'Precision: {precision_score(y_true, y_pred > threshold):.5}', logger)
        log(f'Recall: {recall_score(y_true, y_pred > threshold):.5}', logger)


def eval_pipeline(pipeline: Pipeline, X, y_true: list, plot_pr_curve: bool = True, threshold: float = None):
    """
    Evaluate a pipeline using the eval_score method
    :param pipeline to evaluate
    :param X: input test dataset
    :param y_true: label to predict
    :param plot_pr_curve: if set to True, will display precision recall (PR) curve (optional - default: True)
    :param threshold: to use for classification
    """
    y_pred = pipeline.predict_proba(X)[:, 1]
    eval_score(y_true, y_pred, plot_pr_curve, threshold)


class FeatureSelection(BaseEstimator, TransformerMixin):
    """
    Class that performs Feature Selection as  part of a Sklearn's pipeline. Can work
    both as Feature Selection and Feature "dropping"
    """
    def __init__(self, feature_list: list, exclude=False):
        """
        exclude: optional (default = False). If set to True, the list of features given will be dropped instead
        of kept.
        """
        self.feature_list = feature_list
        self.exclude = exclude

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.exclude:
            return X.drop(self.feature_list, axis=1)
        return X[self.feature_list]


def load_dill_model(model_path: str):
    """
    Load model which was saved in a dill format
    :param model_path: path of where to find the model
    """
    with open(model_path, 'rb') as model_file:
        u = dill.Unpickler(model_file)
        u.encoding = 'utf-8'
        return u.load()


def save_dill_model(model_path: str, pipeline, if_exists_replace: bool = False,
                    logger: Optional[logging.Logger] = None):
    """
    Save model in dill format
    :param model_path: path where to store the model
    :param pipeline: object to store
    :param if_exists_replace: boolean. If set to True, will replace file if already exists. If False, will raise
    Error (optional - default False)
    :param logger: logger to use to output results. If None, will use print (optional - default: None)
    """

    if not if_exists_replace:
        if os.path.isfile(model_path):
            raise FileExistsError(
                f"File {model_path} already exists. To overwrite it, set param if_exists_replace to True")

    with open(model_path, 'wb') as model_file:
        u = dill.Pickler(model_file, recurse=True)
        u.encoding = 'utf-8'
        u.dump(pipeline)
    log(f'Model saved at {model_path}', logger)
