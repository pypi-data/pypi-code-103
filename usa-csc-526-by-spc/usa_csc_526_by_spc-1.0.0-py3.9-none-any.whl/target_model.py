# first neural network with keras tutorial
from keras.layers import Dense
from keras.models import Sequential
from numpy import loadtxt

INPUT_DIMENSION = 1260


def main():
    # load the dataset
    dataset = loadtxt('gold_training_data_a.csv', delimiter=',')
    # split into input (X) and output (y) variables
    X = dataset[:, 0:INPUT_DIMENSION]
    y = dataset[:, INPUT_DIMENSION]
    # define the keras model
    model = Sequential()
    model.add(Dense(INPUT_DIMENSION >> 1, input_dim=INPUT_DIMENSION, activation='relu'))
    model.add(Dense(INPUT_DIMENSION >> 2, activation='relu'))
    model.add(Dense(1, activation='linear'))
    # compile the keras model
    model.compile(loss='mean_squared_error', optimizer='adam',
                  metrics=['accuracy'])
    # fit the keras model on the dataset
    model.fit(X, y, epochs=150, batch_size=10)
    # evaluate the keras model
    _, accuracy = model.evaluate(X, y)
    print('Accuracy: %f' % (accuracy * 100))


if __name__ == '__main__':
    main()
