import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
from sklearn.linear_model import LinearRegression


from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split


def multipleRegression(path):
    df = pd.read_csv(path)
    length = df.shape[0]
    train_length = int(length*0.8)

    train_data = df.iloc[:train_length,:].values
    test_data = df.iloc[train_length:,:].values

    # defining feature matrix(X) and response vector(y)
    X_train = train_data[:,[1,2,3,4,6]]
    y_train = train_data[:,[5]]
    X_test = test_data[:,[1,2,3,4,6]]
    y_test = test_data[:,[5]]

    # splitting X and y into training and testing sets
    # create linear regression object
    reg = LinearRegression()

    # # train the model using the training sets
    reg.fit(X_train, y_train)

    test_predict = reg.predict(X_test)  #check wwith y_test

    # # regression coefficients
    print('Coefficients: ', reg.coef_)

    # # variance score: 1 means perfect prediction
    print('Variance score: {}'.format(reg.score(X_test, y_test)))

    plt.plot(y_test,color = 'b',)
    plt.plot(test_predict,color='r')
    plt.title('Stock Market Prediction using Multiple Regression')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.show()

def polynomialRegression(path):
    # Quadratic Regression 2
    df = pd.read_csv(path)
    length = df.shape[0]
    train_length = int(length*0.8)

    train_data = df.iloc[:train_length,:].values
    test_data = df.iloc[train_length:,:].values

    # defining feature matrix(X) and response vector(y)
    X_train = train_data[:,[1,2,3,4,6]]
    y_train = train_data[:,[5]]
    X_test = test_data[:,[1,2,3,4,6]]
    y_test = test_data[:,[5]]

    clfpoly2 = make_pipeline(PolynomialFeatures(2), Ridge())
    clfpoly2.fit(X_train, y_train)

    # confidencereg = clfreg.score(X_test, y_test)
    confidencepoly2 = clfpoly2.score(X_test,y_test)

    # print('The linear regression confidence is {}'.format(confidencereg))
    print('The quadratic regression 2 confidence is {}'.format(confidencepoly2))


    test_predict2 = clfpoly2.predict(X_test)

    plt.plot(y_test,color = 'b',)
    plt.plot(test_predict2,color='r')
    plt.title('Stock Market Prediction using Polynomial Regression')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.show()

def lassoRegression(path):
    df = pd.read_csv(path)
    length = df.shape[0]
    train_length = int(length*0.8)

    train_data = df.iloc[:train_length,:].values
    test_data = df.iloc[train_length:,:].values

    # defining feature matrix(X) and response vector(y)
    X_train = train_data[:,[1,2,3,4,6]]
    y_train = train_data[:,[5]]
    X_test = test_data[:,[1,2,3,4,6]]
    y_test = test_data[:,[5]]

    lassoReg = linear_model.Lasso(alpha=0.1)
    lassoReg.fit(X_train, y_train)

    test_predictlasso = lassoReg.predict(X_test)
    confidencelasso = lassoReg.score(X_test,y_test)


    print('The lasso confidence is {}'.format(confidencelasso))

    plt.plot(y_test,color = 'b',)
    plt.plot(test_predictlasso,color='r')
    plt.title('Stock Market Prediction using Lasso Regression')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.show()
