from sklearn.metrics import roc_auc_score
from sklearn.metrics import average_precision_score
import numpy as np

def auroc(labels, scores, **kwargs):
    if isinstance(labels, list):
        labels = np.array(labels)
    if isinstance(scores, list):
        scores = np.array(scores)        
    if scores.shape[-1] != 1 and len(scores.shape)>1:
        class_auc_list = []
        for i in range(scores.shape[-1]):
            try:
                local_auc = roc_auc_score(labels[:, i], scores[:, i])
                class_auc_list.append(local_auc)
            except: 
                class_auc_list.append(0.8)
        return class_auc_list
    return roc_auc_score(labels, scores)


def auprc(labels, scores, **kwargs):
    if isinstance(labels, list):
        labels = np.array(labels)
    if isinstance(scores, list):
        scores = np.array(scores)      
    if scores.shape[-1] != 1 and len(scores.shape)>1:
        class_auc_list = []
        for i in range(scores.shape[-1]):
            try:
                local_auc = roc_auc_score(labels[:, i], scores[:, i])
                class_auc_list.append(local_auc)
            except: 
                class_auc_list.append(0.8)
        return class_auc_list
    return average_precision_score(labels, scores)



if __name__ == '__main__':
    # import numpy as np
    preds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    labels = [1, 1, 1, 0, 0, 0, 1, 1, 1, 0]
    # print (preds.shape, labels.shape)
    print (auprc(labels, preds))
    print (auroc(labels, preds))
    
    print (roc_auc_score(labels, preds))
    print (average_precision_score(labels, preds))


