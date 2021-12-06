from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

from credit_card_clients_model.config import config
from credit_card_clients_model.preprocessors import CategoricalReplacer


numeric_transformer = make_pipeline(
    SimpleImputer(strategy="constant", fill_value=0),
)

categorical_transformer = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore"),
)

education_transformer = make_pipeline(
    CategoricalReplacer(
        categories_to_replace=[5, 6, 0],
        value=4,
    ),
)

marriage_transformer = make_pipeline(
    CategoricalReplacer(
        categories_to_replace=[0],
        value=3,
    ),
)

pay_n_transformer = make_pipeline(
    CategoricalReplacer(
        categories_to_replace=[0, -2],
        value=-1,
    ),
)

preprocessor = ColumnTransformer(
    transformers=[
        ("edu", education_transformer, config.CATEGORICAL_FEATURES.EDUCATION.name),
        ("mar", marriage_transformer, config.CATEGORICAL_FEATURES.MARRIAGE.name),
        (
            "pay_n",
            pay_n_transformer,
            [
                config.CATEGORICAL_FEATURES.PAY_0.name,
                config.CATEGORICAL_FEATURES.PAY_2.name,
                config.CATEGORICAL_FEATURES.PAY_3.name,
                config.CATEGORICAL_FEATURES.PAY_4.name,
                config.CATEGORICAL_FEATURES.PAY_5.name,
                config.CATEGORICAL_FEATURES.PAY_6.name,
            ],
        ),
        ("num", numeric_transformer, [e.name for e in config.NUMERICAL_FEATURES]),
        ("cat", categorical_transformer, [e.name for e in config.CATEGORICAL_FEATURES]),
    ]
)

# Append classifier to preprocessing pipeline.
# Now we have a full prediction pipeline.
pipeline = make_pipeline(
    preprocessor,
    RandomForestClassifier(),
)
