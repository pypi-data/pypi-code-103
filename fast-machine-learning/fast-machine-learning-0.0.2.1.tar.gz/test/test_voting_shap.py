import sys, numpy as np, pandas as pd
sys.path.append("..")
import joblib
from fml.data import read_data
from fml.ensemble import VotingShap
import shap

voting_model = joblib.load("vr.joblib")
dataset = read_data("C://Users//luktian//OneDrive//钙钛矿数据处理//处理09-20年数据的带隙值//2)//organic_data_3.xlsx", df=False)
vs = VotingShap(voting_model, dataset).fit()
shap_values = vs.shap_values
shap.plots.bar(shap_values)
# X = dataset.iloc[:, 1:]

# columns = []
# column_set = []
# for trainobj in voting_model.trainobjects:
#     columns.append(trainobj.Xnames.tolist())
#     column_set += trainobj.Xnames.tolist()
# column_set = list(set(column_set))
# X = X.loc[:, column_set]

# def predict(X):
#     data = DataObject(X=X.values, Y=np.zeros(X.shape[0]), Xnames=X.columns, Yname=voting_model.trainobjects[0].Yname)
#     predictions = voting_model.predict(data)
#     return predictions

# explainer = Permutation(predict, X, feature_names=X.columns.tolist())
# shap_values = explainer(X)
# shap_values_ = shap_values.values
# # shap.plots.bar(shap_values)
# feature_importance = shap_values.abs.mean(0).values
