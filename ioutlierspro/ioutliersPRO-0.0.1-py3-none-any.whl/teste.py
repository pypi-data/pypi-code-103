from outliers import detect_numeric_outliers
from iris import data

data = detect_numeric_outliers(data)
import pandas as pd 
pd.DataFrame(data).to_csv("teste.csv")
