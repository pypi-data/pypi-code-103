from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from classification_model.config.core import config

pipeline = Pipeline(
    [
        ("scaler", MinMaxScaler()),
        ("knn", KNeighborsClassifier(n_jobs=3)),
    ]
)
