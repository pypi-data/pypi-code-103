from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class ColumnSelector(TransformerMixin, BaseEstimator):
    """Transformer affecting only selected columns

    :param transformer: scikit-learn transformer
    :param columns: select specific DataFrame columns
    :param columns_regex: select DataFrame columns via regex
        mutually exclusive with parameters `columns` and `columns_like`
    :param columns_like: select DataFrame columns via like
        mutually exclusive with parameters `columns` and `columns_regex`
    :param infer_new_columns: strategy to infer new column names
        "same" = 1-to-1 correspondence between input and output columns
        "auto" = automatically determine new columns based on tranformer's class
            not implemented yet
        "attr" = from transformer's attribute
        "same_attr" = from nested transformer's attribute
        "num" = numerate 1, 2, ...
    :param new_columns_attr: transformer's attribute to infer new columns
        used if `infer_new_columns` = "attr"
    :param new_columns_prefix: prefix for new columns
        used if `infer_new_columns` = "attr" | "num"
    :param remainder: pass through or drop remaining columns
        "passthrough" = leave the remaining columns
        "drop" = drop the remaining columns
    """

    def __init__(
        self,
        transformer=None,
        columns: Optional[list[str]] = None,
        columns_regex: Optional[str] = None,
        columns_like: Optional[str] = None,
        #  infer_new_columns: Literal['same', 'attr', 'same_attr', 'num', 'auto'] = 'same',
        infer_new_columns: str = "same",
        new_columns_attr: Optional[str] = None,
        new_columns_prefix: Optional[str] = None,
        override_dataframe_columns: bool = False,
        #  remainder: Literal['passthrough', 'drop'] = 'passthrough',
        remainder: str = "passthrough",
        copy: bool = True,
    ):
        self.transformer = transformer
        self.columns = columns
        self.columns_regex = columns_regex
        self.columns_like = columns_like
        self.infer_new_columns = infer_new_columns
        self.new_columns_attr = new_columns_attr
        self.new_columns_prefix = new_columns_prefix
        self.override_dataframe_columns = override_dataframe_columns
        self.remainder = remainder
        self.copy = copy

    def fit(self, X: pd.DataFrame, y=None):
        if self.transform is None:
            return self
        self.columns_ = list(X.columns)
        if (self.columns is None) and (self.columns_regex is None) and (self.columns_like is None):
            self.columns_t_ = list(X.columns)
        else:
            self.columns_t_ = X.filter(
                items=self.columns, regex=self.columns_regex, like=self.columns_like, axis=1
            ).columns
        if self.remainder == "passthrough":
            self.columns_l_ = [x for x in X.columns if x not in set(self.columns_t_)]
        elif self.remainder == "drop":
            self.columns_l_ = []
        else:
            raise ValueError(f"{self.remainder}")
        assert (set(self.columns_l_) | set(self.columns_t_)).issubset(set(self.columns_))
        self.transformer.fit(X=X[self.columns_t_], y=y)
        return self

    def _infer_new_column_names(self, X_t: np.ndarray) -> list[str]:
        actual = X_t.shape[1]
        if self.infer_new_columns == "auto":
            raise NotImplementedError(f"{self.infer_new_columns}")
        if self.infer_new_columns == "same":
            expected = len(self.columns_t_)
            if expected != actual:
                raise ValueError(f"Wrong number of transformed columns: {expected} vs {actual}")
            new_columns_t_ = self.columns_t_
        elif self.infer_new_columns == "attr":
            assert self.new_columns_attr is not None
            colattr = getattr(self.transformer, self.new_columns_attr)
            expected = len(colattr)
            if expected != actual:
                raise ValueError(f"Wrong number of transformed columns: {expected} vs {actual}")
            prefix = (
                "_".join(self.columns_t_)
                if self.new_columns_prefix is None
                else self.new_columns_prefix
            )
            new_columns_t_ = [prefix + "_" + str(x) for x in colattr]
        elif self.infer_new_columns == "same_attr":
            assert self.new_columns_attr is not None
            colattr = getattr(self.transformer, self.new_columns_attr)
            expected = sum(len(x) for x in colattr)
            if expected != actual:
                raise ValueError(f"Wrong number of transformed columns: {expected} vs {actual}")
            if len(self.columns_t_) != len(colattr):
                raise ValueError(
                    f"Wrong number of columns: {len(self.columns_t_)} vs {len(colattr)}"
                )
            new_columns_t_ = []
            for col, subcols in zip(self.columns_t_, colattr):
                new_columns_t_.extend([col + "_" + str(sub) for sub in subcols])
        elif self.infer_new_columns == "num":
            prefix = (
                "_".join(self.columns_t_)
                if self.new_columns_prefix is None
                else self.new_columns_prefix
            )
            new_columns_t_ = [prefix + "_" + str(x) for x in range(actual)]
        else:
            raise ValueError(f"{self.infer_new_columns}")
        return new_columns_t_

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if list(X.columns) != self.columns_:
            raise ValueError(
                f"Columns are different from training: "
                f"new={list(X.columns)} vs old={self.columns_}"
            )
        if self.transform is None:
            return X
        if self.copy:
            X = X.copy()
        X_t = self.transformer.transform(X=X[self.columns_t_])
        if isinstance(X_t, pd.DataFrame) and not self.override_dataframe_columns:
            X_t_ = X_t
        else:
            if isinstance(X_t, pd.DataFrame):
                X_t = X_t.values
            new_columns_t_ = self._infer_new_column_names(X_t)
            X_t_ = pd.DataFrame(X_t, index=X.index, columns=new_columns_t_)
        X_l = X[self.columns_l_]
        X_new = pd.concat([X_l, X_t_], axis=1)
        if set(X_new.columns) == set(self.columns_):
            X_new = X_new[self.columns_]
        self.new_columns_ = list(X_new.columns)
        return X_new

    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.transform is None:
            return X
        if hasattr(self.transformer, "inverse_transform"):
            if self.copy:
                X = X.copy()
            X_orig = self.transformer.inverse_transform(X=X[self.columns_t_])
            if isinstance(X_orig, pd.DataFrame):
                for c in self.columns_t_:
                    X[c] = X_orig[c]
            else:
                X.loc[:, self.columns_t_] = X_orig
            return X
        else:
            return None
