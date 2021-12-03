import sys, numpy as np
sys.path.append("..")
from fml.data import read_data
from fml.formulars import SplitFormular
from fml.descriptors import HOIP
import pandas as pd
from fml.preprocessing import DeleteNan
from fml.data import DataObject

dataset = read_data("./zsl_0802.xlsx", df=True)

formulars = dataset.formular

splited_formulars, _ = SplitFormular().split_formulars(formulars)

splited_formulars += [
    # [{"XQ": 1}, {"V": 1}, {"I": 3}],
    # [{"FA": 1}, {"V": 1}, {"I": 3}],
    # [{"IA": 1}, {"V": 1}, {"I": 3}],
    # [{"AF": 1}, {"V": 1}, {"I": 3}],
    # [{"MA": 1}, {"P": 1}, {"I": 3}],
    # [{"MA": 1}, {"V": 1}, {"I": 3}],
    # [{"MA": 1}, {"Y": 1}, {"I": 3}],
    # [{"MA": 1}, {"W": 1}, {"I": 3}],
    # [{"FA": 1}, {"P": 1}, {"I": 3}],
    # [{"FA": 1}, {"V": 1}, {"I": 3}],
    # [{"FA": 1}, {"Y": 1}, {"I": 3}],
    # [{"FA": 1}, {"W": 1}, {"I": 3}],
    ]

descriptors = []

hoip = HOIP(other=False)
for formular in splited_formulars:
    
    tmp = hoip.describe_formular(formular, onehot=True)
    descriptors.append(tmp)

descriptors = pd.concat(descriptors, axis=1).T
descriptors = descriptors.convert_dtypes(float)
data = DataObject(X=descriptors.values, Y=dataset.iloc[:, -1], Xnames=descriptors.columns, indexes=descriptors.index, Yname="Bandgap")
# data = DeleteNan().fit_transform(data)
data = data.to_df()
data.to_excel("zsldata_0802.xlsx")
