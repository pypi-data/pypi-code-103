# Code source: Jaques Grobler
# License: BSD 3 clause

import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from numpy import loadtxt

INPUT_DIMENSION = 1260
TEST_SIZE = 360


def main():
    # Load the gold dataset
    dataset = loadtxt('gold_training_data_a.csv', delimiter=',')
    # split into input (X) and output (y) variables
    gold_X = dataset[:, 0:INPUT_DIMENSION]
    gold_y = dataset[:, INPUT_DIMENSION]

    # Split the data into training/testing sets
    gold_X_train = gold_X[:-TEST_SIZE]
    gold_X_test = gold_X[-TEST_SIZE:]

    # Split the targets into training/testing sets
    gold_y_train = gold_y[:-TEST_SIZE]
    gold_y_test = gold_y[-TEST_SIZE:]

    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(gold_X_train, gold_y_train)

    get_results(regr, gold_X_test, gold_y_test)

    # Make predictions using the testing set
    gold_y_pred = regr.predict(gold_X_test)

    # The coefficients
    print("Coefficients: \n", regr.coef_)
    # The mean squared error
    print("Mean squared error: %f" % mean_squared_error(gold_y_test,
                                                          gold_y_pred))
    # The coefficient of determination: 1 is perfect prediction
    print("Coefficient of determination: %f" % r2_score(gold_y_test,
                                                          gold_y_pred))

    # Plot outputs
    # plt.scatter(gold_X_test, gold_y_test, color="black")
    plt.plot(gold_X_test, gold_y_pred, color="blue", linewidth=3)

    plt.xticks(())
    plt.yticks(())

    plt.show()


def get_results(model, x, y):
    r_sq = model.score(x, y)
    print('coefficient of determination:', r_sq)
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)


if __name__ == '__main__':
    main()
