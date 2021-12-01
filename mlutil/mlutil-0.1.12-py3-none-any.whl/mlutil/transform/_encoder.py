from __future__ import annotations

# import numpy as np
# import pandas as pd
# from sklearn.preprocessing import OrdinalEncoder as _OrdinalEncoder


class OrdinalEncoder:
    """
    Ordinal Encoder extending sklearn.preprocessing.OrdinalEncoder

    New features:
    - if X is a DataFrame, returns DataFrame
    - if X has categorical columns, returens categorical columns
    - if test data has unknown categories, transforms them to a new category
    """

    pass
