# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import sys
import numpy as np
try:
    from pyspark.sql import DataFrame
    from pyspark.mllib.evaluation import MulticlassMetrics, RegressionMetrics, BinaryClassificationMetrics
    from pyspark.sql.functions import col, expr
    from pyspark.ml.feature import StringIndexer
    from pyspark.ml import Pipeline
except ImportError as ie:
    pass
from ibm_wos_utils.feedback.batch.utils import constants

class MetricsUtils():
    
    def __init__(self, logger):
        self.logger = logger

    '''
    Find the true label value from the probability. For binary model, true label is always 
    at index position 1 in the probability array.
    '''
    def detect_true_label(self, data, probability_col, prediction_col, sorted_labels):

        # get the first row from the dataset to identify true label which is
        # at index position 1 in the probability array
        result = data.select(probability_col, prediction_col).first()
        probability_val = result[probability_col]
        prediction_val = result[prediction_col]

        self.logger.info("Detecting the true label from the probability array {} and the predicted value is {}".format(
            probability_val, prediction_val))

        prob_arr = np.array(probability_val)
        # get the max value of index location
        win_prob_index_position = np.argmax(prob_arr)
        self.logger.info("Winning Probability Index Position {}".format(
            win_prob_index_position))

        true_label = None
        if win_prob_index_position == 1:
            # If the winning probability is at index 1 then predicted value is the true label
            true_label = prediction_val
            self.logger.info("Winning Probability Index Position: {} and True label: {}".format(
                win_prob_index_position, true_label))
        else:
            # There are only 2 values in the probability array for binary classfication models.
            # If the winning probaility is 0, then find the value from the label's list which is not
            # equal to the predicted value
            for val in sorted_labels:
                if val != prediction_val:
                    true_label = val
                    self.logger.info("Winning Probability Index:  is at {} and True label: {}".format(
                        win_prob_index_position, true_label))

        return true_label


    def get_string_indexer_order_type(self, sorted_labels, true_label):

        label_index = 0
        # default ordering is aplhabetic ascending order
        string_order_type = "alphabetAsc"
        for val in sorted_labels:
            if val == true_label and label_index == 1:
                string_order_type = "alphabetAsc"
                self.logger.info("True label {} and label_index {} assigning string order type {}".
                            format(true_label, label_index, string_order_type))
            elif val == true_label and label_index == 0:
                string_order_type = "alphabetDesc"
                self.logger.info("True label {} and label_index {} assigning string order type {}".
                            format(true_label, label_index, string_order_type))
            label_index = label_index + 1

        return string_order_type

    def mainpulate_data(self, data, model_type, label_col, prediction_col, probability_col):
        
        try:
            label_col_type = dict(data.dtypes)[label_col]
        except KeyError as ex:
            #Fallback to the lowercase, if the label column is not found with original case
            label_col = label_col.lower()
            prediction_col = prediction_col.lower()
            
        label_col_type = dict(data.dtypes)[label_col]
        prediction_col_type = dict(data.dtypes)[prediction_col]

        distinct_labels = []
        if model_type != constants.REGRESSION_MODEL_TYPE:

            if label_col_type in constants.CLASSIFICATION_CAST_DATA_TYPES:
                data = data.withColumn(label_col, col(label_col).cast('string'))

            if model_type == constants.BINARY_CLASSIFICATION_MODEL_TYPE:
                # Find the distinct labels from the label column
                distinct_labels = [x[label_col]
                                for x in data.select(label_col).distinct().collect()]
                sorted_labels = sorted(distinct_labels)
                true_label = self.detect_true_label(
                    data, probability_col, prediction_col, sorted_labels)
                string_order_type = self.get_string_indexer_order_type(
                    sorted_labels, true_label)
            else:
                # Do the ordering in alphabetical ascending order for multi classification models to maintain
                # the consistency of labels across the multiple runs
                string_order_type = "alphabetAsc"

            string_indexer = StringIndexer(
                inputCol=label_col, outputCol=label_col + "_index", stringOrderType=string_order_type)

            string_indexer_model = string_indexer.fit(data)
            distinct_labels = string_indexer_model.labels
            self.logger.info("Distinct Labels:{}".format(distinct_labels))
            df = string_indexer_model.transform(data)

            label_col = label_col + "_index"

            label_map = dict()
            label_encode_index = 0.0
            label_query_str = "case "
            is_prediction_col_space_included = True if prediction_col.count(" ") > 0 else False
            for label in distinct_labels:
                label_map[label] = label_encode_index
                if is_prediction_col_space_included:
                    #put the column name within back-ticks when the column name contains the space
                    label_str = "when `{0}` = '{1}' then {2} ".format(
                        prediction_col, label, float(label_encode_index))
                else:
                    label_str = "when {0} = '{1}' then {2} ".format(
                        prediction_col, label, float(label_encode_index))
                label_query_str += label_str
                label_encode_index += 1

            label_query_str += "else -1 end"
            df = df.withColumn(prediction_col, expr(label_query_str))
            df = df.withColumn(prediction_col, col(prediction_col).cast('double'))
            manipulated_df = df.select(prediction_col, label_col).collect()

        if model_type == constants.REGRESSION_MODEL_TYPE:

            # cast the int/long/float values to double as the spark ml accepts the
            # label and prediction values to be in doouble data type
            # cast the double type column values to double as the column will have both int and double values
            if label_col_type in constants.REGRESSION_MODEL_DATA_TYPES:
                data = data.withColumn(label_col, col(label_col).cast('double'))
            if prediction_col_type in constants.REGRESSION_MODEL_DATA_TYPES:
                data = data.withColumn(prediction_col, col(prediction_col).cast('double'))
                
            manipulated_df = data.select(prediction_col, label_col).collect()
  

        return manipulated_df, distinct_labels

    '''
    Generate the quality metrics  based on the model type using the spark ml library.
    For binary models, it detects the true label from the probability values and 
    true label will always be at index position 1 and same will be considered in the 
    order of labels while generating the confusion matrix. For multiclass, the order of labels 
    will be in ascending order while generating the confusion matrix.
    '''

    def compute_quality_metrics(self, sc, data, model_type, label_col, prediction_col, probability_col, counts):

        self.logger.info("Computing the quality metrics for model type: {}".format(model_type))
        df1, distinct_labels = self.mainpulate_data(data, model_type, label_col, prediction_col, probability_col)
        predictionAndLabels = sc.parallelize(df1)

        metrics = dict()
        quality_metric, confusion_matrix = self.get_metrics(
            model_type, predictionAndLabels)

        metrics["quality_metric"] = quality_metric
        metrics["total_records"] = counts['records_count']
        if 'borrowed_records' in counts:
            metrics["borrowed_records"] = counts["borrowed_records"]
        if model_type != constants.REGRESSION_MODEL_TYPE:
            self.logger.info("Labels {}".format(distinct_labels))
            self.logger.info("confusion_matrix {}".format(confusion_matrix))
            metrics["confusion_matrix"] = confusion_matrix.tolist()
            metrics["labels"] = distinct_labels

        self.logger.info("Quality metrics {} for model type:{}".format(
            quality_metric, model_type))

        return metrics
        
    
    def get_metrics(self, model_type, predictionAndLabels):

        quality_metric = dict()
        confusion_matrix = list()
        # use the set_printoptions to ignore the scientific notation of digits in the confusion matrix
        np.set_printoptions(suppress=True)

        if model_type == constants.MULTI_CLASSIFICATION_MODEL_TYPE:

            metrics_mc = MulticlassMetrics(predictionAndLabels)

            weighted_recall = metrics_mc.weightedRecall
            weighted_precision = metrics_mc.weightedPrecision
            weighted_f_measure = metrics_mc.weightedFMeasure(1.0)
            accuracy = metrics_mc.accuracy
            weighted_false_positive_rate = metrics_mc.weightedFalsePositiveRate
            weighted_true_positive_rate = metrics_mc.weightedTruePositiveRate

            # confusion matrix fetches the labels in ascending
            confusion_matrix = metrics_mc.confusionMatrix().toArray()

            quality_metric["accuracy"] = accuracy
            quality_metric["weighted_true_positive_rate"] = weighted_true_positive_rate
            quality_metric["weighted_recall"] = weighted_recall
            quality_metric["weighted_precision"] = weighted_precision
            quality_metric["weighted_f_measure"] = weighted_f_measure
            quality_metric["weighted_false_positive_rate"] = weighted_false_positive_rate
            # TODO: Need to add a logic to compute the log loss based on the probabilities
            #quality_metric["log_loss"] = quality_metric["log_loss"]

        elif model_type == constants.BINARY_CLASSIFICATION_MODEL_TYPE:
            binary_metrics = BinaryClassificationMetrics(predictionAndLabels)
            mc_metrics = MulticlassMetrics(predictionAndLabels)

            accuracy = mc_metrics.accuracy
            area_under_roc = binary_metrics.areaUnderROC
            area_under_pr = binary_metrics.areaUnderPR

            # Find's the True positive rate for the true label 1.0.
            # True label is always at index position 1 in the array [0.0, 1.0]
            true_positive_rate = mc_metrics.truePositiveRate(1.0)
            # Find's the False positive rate for the true label 1.0.
            false_positive_rate = mc_metrics.falsePositiveRate(1.0)
            # Find's the Recall for the true label 1.0.
            recall = mc_metrics.recall(1.0)
            # Find's the Precision for the true label 1.0.
            precision = mc_metrics.precision(1.0)
            # Find's the f1_measure for the true label 1.0.
            f1_measure = mc_metrics.fMeasure(1.0)

            confusion_matrix = mc_metrics.confusionMatrix().toArray()

            quality_metric["accuracy"] = accuracy
            quality_metric["true_positive_rate"] = true_positive_rate

            quality_metric["recall"] = recall
            quality_metric["precision"] = precision
            quality_metric["false_positive_rate"] = false_positive_rate
            quality_metric["area_under_roc"] = area_under_roc
            quality_metric["area_under_pr"] = area_under_pr
            quality_metric["f1_measure"] = f1_measure
            # TODO: Need to add a logic to compute the log loss based on the probabilities
            #quality_metric["log_loss"] = log_loss(probabilities)

        elif model_type == constants.REGRESSION_MODEL_TYPE:
            metrics = RegressionMetrics(predictionAndLabels)

            explained_variance = metrics.explainedVariance
            mean_absolute_error = metrics.meanAbsoluteError
            mean_squared_error = metrics.meanSquaredError
            r2 = metrics.r2
            root_mean_squared_error = metrics.rootMeanSquaredError

            quality_metric["explained_variance"] = explained_variance
            quality_metric["mean_absolute_error"] = mean_absolute_error
            quality_metric["mean_squared_error"] = mean_squared_error
            quality_metric["r2"] = r2
            quality_metric["root_mean_squared_error"] = root_mean_squared_error

        return quality_metric, confusion_matrix


