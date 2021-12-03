import sys, numpy as np
sys.path.append("..")
from fml.preprocessing import Preprocessing
from fml.data import read_data

dataset = read_data("data.txt", df=False)
dataset = Preprocessing(corr_criterion=0.90).fit_transform(dataset).to_df()
