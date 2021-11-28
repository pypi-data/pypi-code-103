# Imports
from . import CXAI_config
from . import CXAI_dataloader
import tensorflow as tf
# Helper libraries
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import roc_auc_score
import sklearn.metrics
import h5py

import seaborn as sns
from matplotlib import style
style.use('seaborn-white')
print(tf.config.experimental.list_physical_devices('GPU'))
tf.debugging.set_log_device_placement(False)


def load_model_for_eval(modelpath):
    print("Loading model", modelpath)
    foldnr = modelpath.split("fold_")[1].split(".h5")[0]
    model = tf.keras.models.load_model(modelpath)
    return model, foldnr


def get_X_data(xname, datadir):
    with h5py.File(os.path.join(datadir, "selected_patients.hdf5"), "r") as f:
        temp = []
        groups = list(f[xname])
        for group in groups:
            temp.append(list(f.get(xname)[group]))
    return dict(zip(groups, temp))


def generate_confusion_matrix(test_label_, y_pred_, foldnum, modelpath, target_labels=['NOR', 'MINF', 'DCM', 'HCM', 'RV']):
    style.use('seaborn-white')
    cm = confusion_matrix(test_label_, y_pred_)
    df_cm = pd.DataFrame(cm, index=target_labels, columns=target_labels)
    plt.figure(figsize=(10, 7))
    sns.heatmap(df_cm, annot=True, annot_kws={
                "size": 16}, fmt="d", linewidths=.5,)
    
    b, t = plt.ylim()  # discover the values for bottom and top
    b += 0.5  # Add 0.5 to the bottom
    t -= 0.5  # Subtract 0.5 from the top
    plt.ylim(b, t)  # update the ylim(bottom, top) values
    plt.title("Confusion Matrix - Fold " + str(foldnum), fontsize=18)
    plt.xlabel('Predicted Class', fontsize=16)
    plt.ylabel('True Class', fontsize=16)
    # changed model_config.file.modeldir,str(modelname) to datadir
    plt.savefig(os.path.join(
        modelpath + '_confusion_matrix.png'), facecolor='w')
    plt.show()
    return cm  

def cm_details(cm, l):
    # source (modified from): https://stackoverflow.com/a/47907339
    num_classes = len(cm)
    TruePositive = np.diag(cm)

    FalsePositive = []
    for i in range(num_classes):
        FalsePositive.append(sum(cm[:, i]) - cm[i, i])

    FalseNegative = []
    for i in range(num_classes):
        FalseNegative.append(sum(cm[i, :]) - cm[i, i])

    TrueNegative = []
    for i in range(num_classes):
        temp = np.delete(cm, i, 0)   # delete ith row
        temp = np.delete(temp, i, 1)  # delete ith column
        TrueNegative.append(sum(sum(temp)))

    for i in range(num_classes):
        print(TruePositive[i] + FalsePositive[i] +
              FalseNegative[i] + TrueNegative[i] == l)

    return np.asarray(TruePositive, dtype=np.uint16), np.asarray(FalsePositive, dtype=np.uint16), np.asarray(FalseNegative, dtype=np.uint16), np.asarray(TrueNegative, dtype=np.uint16)


def roc_auc_score_multiclass(actual_class, pred_class, average="macro"):
    # creating a set of all the unique classes using the actual class list
    unique_class = set(actual_class)
    roc_auc_dict = {}
    for per_class in unique_class:
        # creating a list of all the classes except the current class
        other_class = [x for x in unique_class if x != per_class]

        # marking the current class as 1 and all other classes as 0
        new_actual_class = [0 if x in other_class else 1 for x in actual_class]
        new_pred_class = [0 if x in other_class else 1 for x in pred_class]

        # using the sklearn metrics method to calculate the roc_auc_score
        roc_auc = roc_auc_score(
            new_actual_class, new_pred_class, average=average)
        roc_auc_dict[per_class] = roc_auc

    return roc_auc_dict


def classification_evaluation(model_config, modelpath, test_img=None, test_label=None):
    model, foldnum = load_model_for_eval(modelpath)

    if test_img is None or test_label is None:
        _, _, test_img, test_label, _, _, _ = CXAI_dataloader.cv_dataloader(
            model_config).generate_ds_form_cv_list(numOfPass=foldnum)

    test = tf.data.Dataset.from_tensor_slices((test_img, test_label))
    test_batches = test.batch(model_config.model.batch_size)

    y_pred = model.predict(test_batches)

    y_pred_ = np.argmax(y_pred, axis=1)
    test_label_ = np.argmax(test_label, axis=1)

    class_report = classification_report(test_label_, y_pred_, output_dict=True, target_names=sorted(
        model_config.data.diagnosis_dict, key=model_config.data.diagnosis_dict.get))
    print(class_report)

    cm = generate_confusion_matrix(test_label_, y_pred_, foldnum, modelpath, target_labels=sorted(
        model_config.data.diagnosis_dict, key=model_config.data.diagnosis_dict.get))

    df = pd.DataFrame.from_dict(class_report, orient='columns')
    df.reset_index(inplace=True)
    startidx = len(df)

    TP, FP, FN, TN = cm_details(cm, len(test_label_))
    TNR = TN/(TN+FP)  # specificity or true negative rate
    NPV = TN/(TN+FN)  # negative prediction value
    FOR = FN/(FN+TN)  # false omission rate

    metric_names = ['specificity', 'negative_prediction_value',
                    'false_omission_rate', 'TP', 'FP', 'FN', 'TN']
    metrics = [TNR, NPV, FOR, TP, FP, FN, TN]

    for j, metric in enumerate(metric_names):
        df.loc[startidx + j, 'index'] = metric
        for i, dia in enumerate(model_config.data.diagnosis_dict):
            df.loc[startidx + j, dia] = metrics[j][i]

    df.to_csv(os.path.join(model_config.file.modeldir,
              'performance_metrics_fold'+str(foldnum)+'.csv'))

    lr_roc_auc_multiclass = roc_auc_score_multiclass(test_label_, y_pred_)
    print(lr_roc_auc_multiclass)

    return class_report, cm, metrics, test_label, y_pred


def calc_roc_auc_scores(y_test, y_pred, n_classes=5):  # changed n_classes
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = sklearn.metrics.roc_curve(
            y_test[:, i], y_pred[:, i])
        roc_auc[i] = sklearn.metrics.auc(fpr[i], tpr[i])

    return fpr, tpr, roc_auc


def plot_roc_auc_single(fpr, tpr, roc_auc, target_labels, modelpath,  titleaddition=""):  # * OK
    plt.figure(figsize=(8, 6))
    ax = plt.axes()
    n_classes = len(target_labels)
    ax.set_prop_cycle('color', [plt.cm.Set1(i)
                      for i in np.linspace(0, 1, n_classes)])

    for i in range(len(fpr)):
        plt.plot(fpr[i], tpr[i],  label='ROC curve for %s (area = %0.2f)' % (
            list(target_labels.items())[i][0], roc_auc[i]))  # alpha=0.55,

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([-0.01, 1.01])
    plt.ylim([-0.01, 1.01])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.title('Receiver operating characteristic' + str(titleaddition))
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(modelpath + '_roc_auc.png'), facecolor='w')
    plt.show()

def classification_evaluation_with_auc(model_config, modelpath, test_img=None, test_label=None):
    roc = []
    model, foldnum = load_model_for_eval(modelpath)

    if test_img is None or test_label is None:
        _, _, test_img, test_label, _, _, _ = CXAI_dataloader.cv_dataloader(
            model_config).generate_ds_form_cv_list(numOfPass=foldnum)

    test = tf.data.Dataset.from_tensor_slices((test_img, test_label))
    test_batches = test.batch(model_config.model.batch_size)

    y_pred = model.predict(test_batches)

    y_pred_ = np.argmax(y_pred, axis=1)
    test_label_ = np.argmax(test_label, axis=1)

    class_report = classification_report(
        test_label_, y_pred_, output_dict=True, target_names=model_config.data.diagnosis_dict)
    print(class_report)

    cm = generate_confusion_matrix(
        test_label_, y_pred_, foldnum, modelpath, model_config.data.diagnosis_dict)

    df = pd.DataFrame.from_dict(class_report, orient='columns')
    df.reset_index(inplace=True)
    startidx = len(df)

    fpr, tpr, auc = calc_roc_auc_scores(
        test_label, y_pred, len(model_config.data.diagnosis_dict))
    plot_roc_auc_single(
        fpr, tpr, auc, model_config.data.diagnosis_dict, modelpath, " fold "+str(foldnum))
    roc.append([fpr, tpr, auc])

    TP, FP, FN, TN = cm_details(cm, len(test_label_))

    TNR = TN/(TN+FP)  # specificity or true negative rate
    NPV = TN/(TN+FN)  # negative prediction value
    FOR = FN/(FN+TN)  # false omission rate

    metric_names = ['specificity', 'negative_prediction_value',
                    'false_omission_rate', 'TP', 'FP', 'FN', 'TN', 'AUC']
    metrics = [TNR, NPV, FOR, TP, FP, FN, TN, auc]

    for j, metric in enumerate(metric_names):
        df.loc[startidx + j, 'index'] = metric
        for i, dia in enumerate(sorted(model_config.data.diagnosis_dict, key=model_config.data.diagnosis_dict.get)):
            df.loc[startidx + j, dia] = metrics[j][i]

    df.to_csv(os.path.join(model_config.file.modeldir,
              'performance_metrics_fold'+str(foldnum)+'.csv'))

    lr_roc_auc_multiclass = roc_auc_score_multiclass(test_label_, y_pred_)
    print(lr_roc_auc_multiclass)

    return class_report, cm, metrics, roc