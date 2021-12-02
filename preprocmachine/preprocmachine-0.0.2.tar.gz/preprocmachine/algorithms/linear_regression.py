import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error as mse
from sklearn.model_selection import train_test_split as tts


def lr_get_mse(df, target):
    try:
        xtrain, xtest, ytrain, ytest = tts(
            df.loc[:, df.columns != target],
            df.loc[:, target],
            test_size=0.3,
            random_state=69,
        )
        regr = LinearRegression()
        regr.fit(xtrain, ytrain)
        ypred = regr.predict(xtest)
        error = mse(ytest, ypred, squared=False)  # actually RMSE here, not MSE
        return df, error
    except:
        return df, float("inf")
