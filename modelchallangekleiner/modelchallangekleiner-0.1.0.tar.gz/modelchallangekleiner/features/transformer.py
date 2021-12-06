"""Transformer module"""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from modelchallangekleiner.features.transformers.custom_transformers import (
    CustomImputer,
)
from modelchallangekleiner.utils.utils import (
    CATEGORICAL_FEATURES,
    EDUCATION,
    MARRIAGE,
    NUMERICAL_FEATURES,
    PAY_0,
    PAY_2,
    PAY_3,
    PAY_4,
    PAY_5,
    PAY_6,
)

numerical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="mean")),
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)

education_transformer = Pipeline(
    steps=[
        ("imputer", CustomImputer(missing_values=[0, 5, 6], value=4)),
    ]
)

marriage_transformer = Pipeline(
    steps=[
        ("imputer", CustomImputer(missing_values=[0], value=3)),
    ]
)

pay_n_transformer = Pipeline(
    steps=[
        ("imputer", CustomImputer(missing_values=[-2, 0], value=-1)),
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        ("education_transformer", education_transformer, EDUCATION),
        ("marriage_transformer", marriage_transformer, MARRIAGE),
        (
            "pay_n_transformer",
            pay_n_transformer,
            [PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6],
        ),
        ("numerical_transformer", numerical_transformer, NUMERICAL_FEATURES),
        ("categorical_transformer", categorical_transformer, CATEGORICAL_FEATURES),
    ]
)


def get_pipeline() -> Pipeline:
    """Get pipeline
    Parameters:
        :param date (str): date for the context files
        :param output_path (str): path to the context files
    """
    pipeline_training = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", RandomForestClassifier())]
    )
    return pipeline_training
