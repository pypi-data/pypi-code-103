# coding: utf-8

# In[1]:


# Import pandas  
import os
from typing import Type 
cmd = "pip install sklearn  pandas numpy"
os.system(cmd)


from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


class bianary_decision_parameter():
    def __init__(self,max_features,X_train,Y_train,X_test,Y_test,a,b):
        self.m= max_features
        self.x=X_train
        self.y=Y_train
        self.x_1=X_test
        self.y_1=Y_test
        self.a=a
        self.b=b
    def parameter(self):
        weights = {0:self.a,1:self.b}
        DL_1=DecisionTreeClassifier(max_features=self.m,class_weight=weights)
        ccp_alphas=list(DL_1.cost_complexity_pruning_path(self.x,self.y, sample_weight=None).ccp_alphas)
        max_depth=[]
        for i in ccp_alphas:
            dl=DecisionTreeClassifier(ccp_alpha=i)
            tr=dl.fit(self.x,self.y)
            max_depth.append(tr.tree_.max_depth)
       
        parameters1={'max_depth':max_depth, ##Complexity parameter used for Minimal Cost-Complexity Pruning.
             'ccp_alpha':ccp_alphas##Complexity parameter used for Minimal Cost-Complexity Pruning.
            }
        clf_re_1 = GridSearchCV(DL_1,#estimator funtions 
                    parameters1,#define parameters
                    scoring='neg_brier_score')
        classic_model=clf_re_1.fit(self.x,self.y)
        tree_best_1=classic_model.best_estimator_.fit(self.x,self.y)
        y_pred=tree_best_1.predict(self.x_1)
        con=confusion_matrix(self.y_1,y_pred)
        true_positive =con[0][0]
        false_positive =con[1][0]
        false_negative=con[0][1]
        true_negative=con[1][1]
        
        precision=true_positive/(true_positive+false_positive)
        Recall =true_positive/(true_positive+false_negative)
        specificity = true_negative/(true_negative+false_negative)
        missclassification = (false_positive+false_negative)/len(y_pred)
        F_measure = (2 * precision * Recall) / (precision + Recall)
        accuracy=1-missclassification
       
        model_detail= pd.DataFrame(
        {
        "accuracy_score": [accuracy], 
        "missclassification": [missclassification],
        "specificity": [specificity],
        "Recall": [Recall],
        "precision": [precision],
        "F_measure": [F_measure],
        "depth":[classic_model.best_estimator_.max_depth],
        "ccp_alpha":[classic_model.best_estimator_.ccp_alpha],
        "max_features":[classic_model.best_estimator_.max_features]
      }
          )
        return model_detail
        
        