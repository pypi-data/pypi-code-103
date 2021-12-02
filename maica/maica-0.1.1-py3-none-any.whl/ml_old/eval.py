import numpy
import copy
import os
import pandas
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import r2_score
from maica.core.env import *
from maica.data_old.base import Dataset
from maica.data_old.preprocessing import merge_datasets
from maica.ml_old.base import Model
from maica.ml_old.util import get_data_loader
from maica.ml_old.util import get_batch_size
from maica.ml_old.util import get_optimizer
from maica.ml_old.util import get_loss_func
from maica.util.visualization import plot_target_dist
from maica.util.visualization import plot_error_dist
from maica.util.visualization import plot_pred_result


class KFoldGenerator:
    def __init__(self,
                 dataset: Dataset,
                 k: int):
        self.sub_datasets = dataset.get_sub_datasets(k=k)

    def get(self,
            idx_fold: int):
        """
        Get training and test datasets for a given ``idx_fold``.

        :param idx_fold: (*int*) An index of the k-fold dataset.
        :return: Training and test datasets.
        """

        list_train_datasets = [self.sub_datasets[i] for i in range(0, len(self.sub_datasets)) if i != idx_fold]
        train_dataset = merge_datasets(list_train_datasets)
        test_dataset = self.sub_datasets[idx_fold]

        return train_dataset, test_dataset


class Metric:
    def __init__(self,
                 targets: numpy.ndarray,
                 preds: numpy.ndarray):
        """
        A data_old class to store evaluation metrics.

        :param targets: (*numpy.ndarray*) The true target values of the prediction.
        :param preds: (*numpy.ndarray*) Predicted target values.
        """

        self.__mae = mean_absolute_error(targets, preds)
        self.__rmse = numpy.sqrt(mean_squared_error(targets, preds))
        self.__mape = mean_absolute_percentage_error(targets, preds)
        self.__r2 = r2_score(targets, preds)

    @property
    def mae(self):
        return self.__mae

    @property
    def rmse(self):
        return self.__rmse

    @property
    def mape(self):
        return self.__mape

    @property
    def r2(self):
        return self.__r2

    def print(self):
        print('#####################################################')
        print('# Evaluation Metrics of the Prediction Results')
        print('#####################################################')
        print('# Mean Absolute Error (MAE): {:.4f}'.format(self.__mae))
        print('# Root Mean Square Error (RMSE): {:.4f}'.format(self.__rmse))
        print('# Mean Absolute Percentage Error (MAPE): {:.4f}'.format(self.__mape))
        print('# R2 Score: {:.4f}'.format(self.__r2))
        print('#####################################################')


def calc_metrics(targets: numpy.ndarray,
                 preds: numpy.ndarray):
    """
    Calculate evaluation metrics for given target values ``targets`` and predicted values ``preds``.
    Four evaluation metrics are calculated:

    - Mean absolute error (MAE).
    - Root mean square error (RMSE).
    - Mean absolute percentage error (MAPE).
    - The coefficient of determination (R2 score).

    Definitions of the evaluation metrics are given in
    `Scikit-learn Regression Metrics <https://mendeleev.readthedocs.io/en/stable/>`_.

    :param targets: (*numpy.ndarray*) Target values of the prediction task.
    :param preds: (*numpy.ndarray*) Predicted values of the machine learning model.
    :return: (*maica.ml_old.util.Metric*) A data_old class to store the evaluation metrics.
    """

    return Metric(targets, preds)


def evaluate(path_dir: str,
             model: Model,
             targets: numpy.ndarray,
             preds: numpy.ndarray,
             idx_data: numpy.ndarray = None):
    """
    Evaluate the machine learning model, and save the evaluation results in a directory of ``path_dir``.

    :param path_dir: (*str*) A path of the directory storing the evaluation results.
    :param model: (*maica.ml_old.base.Model*) A machine learning model that will be evaluated.
    :param targets: (*numpy.ndarray*) Target values of the prediction.
    :param preds: (*numpy.ndarray*) Prediction results of the machine learning model ``model``.
    :param idx_data: (*idx_data, optional*) Indices of the evaluation data_old (*default* = ``None``).
    :return: (*maica.ml_old.eval.Metric*) A Metric object that stores evaluation metrics for the prediction performances.
    """

    __targets = targets.reshape(-1, 1)
    __preds = preds.reshape(-1, 1)

    if idx_data is None:
        __idx_data = numpy.arange(0, targets.shape[0]).reshape(-1, 1)
    else:
        __idx_data = idx_data.reshape(-1, 1)

    if not os.path.exists(path_dir):
        os.mkdir(path_dir)

    # Save the trained model.
    if model.alg_name in ALGS[PIP_JOBLIB]:
        model.save(path_dir + '/model_' + model.alg_name + '.joblib')
    elif model.alg_name in ALGS[PIP_PYTORCH]:
        model.save(path_dir + '/model_' + model.alg_name + '.pt')
    else:
        raise AssertionError('The name of the model {} is unknown.'.format(model.alg_name))

    # Save the prediction results.
    df = pandas.DataFrame(numpy.hstack([__idx_data, __targets, __preds]))
    df.to_excel(path_dir + '/pred_results_' + model.alg_name + '.xlsx',
                index=None, header=['data_index', 'target', 'prediction'])

    # Save the evaluation results and the trained model.
    plot_target_dist(path_dir + '/target_dist.png', __targets)
    plot_error_dist(path_dir + '/error_dist.png', __targets, __preds)
    plot_pred_result(path_dir + '/pred_results.png', __targets, __preds)

    return Metric(__targets, __preds)


def k_fold_cross_val(dataset: Dataset,
                     model: Model,
                     k: int):
    """
    Train and evaluate machine learning model based on k-fold cross validation.
    After the training and evaluation, means and standard deviations are printed in the standard I/O device.

    :param dataset: (*maica.data_old.base.Dataset*) A dataset to train machine learning model.
    :param model: (*maica.ml_old.base.Model*) Machine learning model.
    :param k: (*int*) The number of sub-datasets that will be used for k-fold cross validation.
    :return: (*list*) A list of the ``maica.ml_old.util.Metric`` objects storing the evaluation metrics for each fold.
    """

    if model.alg_name in ALGS_UNSUPERVISED:
        raise AssertionError('This implementation of the k-fold cross validation'
                             'is not supported to the unsupervised machine learning algorithm.')

    k_fold = KFoldGenerator(dataset, k=k)
    metrics = list()

    # Perform the k-fold cross validation.
    print('#########################################################################')
    print('\u0007 Model Training and Evaluation Based on The K-Fold Cross Validation')
    print('#########################################################################')
    for i in range(0, k):
        # Get train and test dataset form the k-fold generator.
        dataset_train, dataset_test = k_fold.get(idx_fold=i)

        # Copy initial model.
        __model = copy.deepcopy(model)

        # Train the model.
        if __model.alg_name in ALGS[PIP_JOBLIB]:
            # Sklearn-based models.
            __model.fit(dataset_train.x, dataset_train.y)
            preds_test = __model.predict(dataset_test.x)
        elif __model.alg_name in ALGS[PIP_PYTORCH]:
            # PyTorch-based models.
            batch_size = get_batch_size(dataset_train)
            data_loader_train = get_data_loader(dataset_train.x, dataset_train.y, batch_size=batch_size, shuffle=True)
            data_loader_test = get_data_loader(dataset_test.x, batch_size=batch_size, shuffle=False)
            optimizer = get_optimizer(__model.parameters(), GD_ADAM)
            criterion = get_loss_func(LOSS_MAE)
            for j in range(0, 300):
                train_loss = __model.fit(data_loader_train, optimizer, criterion)
                print('Fold [{}/{}]\tEpoch [{}/{}]\tTrain MAE: {:.4f}'.format(i + 1, k, j + 1, 300, train_loss))
            preds_test = __model.predict(data_loader_test)
        else:
            raise AssertionError('The model has unknown algorithm name {}.'.format(__model.alg_name))

        # Evaluate the trained model.
        metric = calc_metrics(dataset_test.y, preds_test)
        metrics.append(metric)

        print('Fold [{}/{}]\tTest MAE: {:.4f}\tTest R2: {:.4f}'.format(i + 1, k, metric.mae, metric.r2))

    # Collect evaluation metrics.
    list_mae = [m.mae for m in metrics]
    list_rmse = [m.rmse for m in metrics]
    list_mape = [m.mape for m in metrics]
    list_r2 = [m.r2 for m in metrics]

    # Print prediction performances of the model.
    print('#########################################################################')
    print('\u0007 Results of K-Fold Cross Validation')
    print('#########################################################################')
    print('# Average MAE: {:.4f}\u00B1{:.4f}'.format(numpy.mean(list_mae), numpy.std(list_mae)))
    print('# Average RMSE: {:.4f}\u00B1{:.4f}'.format(numpy.mean(list_rmse), numpy.std(list_rmse)))
    print('# Average MAPE: {:.4f}\u00B1{:.4f}'.format(numpy.mean(list_mape), numpy.std(list_mape)))
    print('# Average R2 Score: {:.4f}\u00B1{:.4f}'.format(numpy.mean(list_r2), numpy.std(list_r2)))
    print('#########################################################################')

    return metrics
