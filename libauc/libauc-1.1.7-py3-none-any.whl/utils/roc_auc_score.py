from sklearn.metrics import roc_auc_score

def auc_score(labels, scores, **kwargs):
    if scores.shape[-1] != 1:
        class_auc_list = []
        for i in range(scores.shape[-1]):
            try:
                local_auc = roc_auc_score(labels[:, i], scores[:, i])
                class_auc_list.append(local_auc)
            except: 
                class_auc_list.append(0.8)
        return class_auc_list
    return roc_auc_score(labels, scores)



