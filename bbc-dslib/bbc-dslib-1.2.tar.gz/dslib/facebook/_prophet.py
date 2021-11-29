from typing import Optional

import pandas as pd

from dslib.utils import deep_suppress_stdout_stderr

try:
    from fbprophet import Prophet
except ImportError as e:
    raise ImportError('Please install "prophet" extra packages.') from e


class FastProphet(Prophet):
    """
    Model using FB-Prophet but without the (slow) Monte-Carlo analysis used to get the confidence
    intervals.
    """

    def fit(self, df: pd.DataFrame, **kwargs) -> None:
        with deep_suppress_stdout_stderr():
            super(FastProphet, self).fit(df, **kwargs)

    def predict(self, X_test: Optional[pd.DataFrame] = None) -> pd.DataFrame:

        df = X_test if X_test is not None else None
        with deep_suppress_stdout_stderr():
            if df is None:
                df = self.history.copy()
            else:
                if df.shape[0] == 0:
                    raise ValueError('Dataframe has no rows.')
                df = self.setup_dataframe(df.copy())

            df['trend'] = self.predict_trend(df)
            seasonal_components = self.predict_seasonal_components(df)

            # Drop columns except y, ds, cap, floor, and trend
            cols = ['ds', 'trend']
            if 'cap' in df:
                cols.append('cap')
            if self.logistic_floor:
                cols.append('floor')
            # Add in forecast components
            df2 = pd.concat((df[cols], seasonal_components), axis=1)
            df2['yhat'] = (df2['trend'] * (1 + df2['multiplicative_terms']) + df2['additive_terms'])

            return df2
