"""CONSTANTS"""

from enum import Enum, auto


CONTEXT_DIR = "data/"
DATASET_FILENAME = "dataset.xls"
DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls"
MODELS_DIR = "models/"
MODEL_FILENAME = "credit_card_clients_model.pkl"
VERSION = "1.0.4"

TARGET = "default payment next month"

# input variables

class CATEGORICAL_FEATURES(Enum):
    LIMIT_BAL = auto()
    SEX = auto()
    EDUCATION = auto()
    MARRIAGE = auto()
    PAY_0 = auto()
    PAY_2 = auto()
    PAY_3 = auto()
    PAY_4 = auto()
    PAY_5 = auto()
    PAY_6 = auto()


class NUMERICAL_FEATURES(Enum):
    AGE = auto()
    BILL_AMT1 = auto()
    BILL_AMT2 = auto()
    BILL_AMT3 = auto()
    BILL_AMT4 = auto()
    BILL_AMT5 = auto()
    BILL_AMT6 = auto()
    PAY_AMT1 = auto()
    PAY_AMT2 = auto()
    PAY_AMT3 = auto()
    PAY_AMT4 = auto()
    PAY_AMT5 = auto()
    PAY_AMT6 = auto()


FEATURES = [e.name for e in CATEGORICAL_FEATURES] + [e.name for e in NUMERICAL_FEATURES]