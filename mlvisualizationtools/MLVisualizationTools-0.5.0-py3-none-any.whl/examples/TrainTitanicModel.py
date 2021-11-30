import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #stops agressive error message printing
from tensorflow import keras
import pandas as pd
from MLVisualizationTools.backend import fileloader

# This creates a keras model for use in demo visualizations
# It uses the Datasets/Titanic/train.csv file
# Limited preprocessing is applied
# Model is trained with 50 epochs and batch size of 10
# Evaluation is applied at the end

def getModel():
    model = keras.Sequential()
    model.add(keras.layers.Dense(10, input_dim=7, activation='relu'))
    model.add(keras.layers.Dense(10, activation='relu'))
    model.add(keras.layers.Dense(1, activation='sigmoid'))
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model

def main():
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    #region preprocess
    header = list(df.columns)
    header.remove("Survived")

    X = df[header].values
    Y = df["Survived"].values

    splitpoint = int(len(df)*0.7)
    trainX = X[:splitpoint]
    testX = X[splitpoint:]

    trainY = Y[:splitpoint]
    testY = Y[splitpoint:]
    #endregion

    print("Creating Model")
    model = getModel()
    print("Starting Training")
    model.fit(trainX, trainY, epochs=50, batch_size=10)
    print("Starting Evaluation")
    _, trainaccuracy = model.evaluate(trainX,trainY)
    _, testaccuracy = model.evaluate(testX, testY)
    print()
    print("We achieved an (training) accuracy of:", str(round(trainaccuracy,3) * 100) + "%")
    print("We achieved an (testing) accuracy of:", str(round(testaccuracy,3) * 100) + "%")
    print()
    model.save(fileloader('examples/Models/titanicmodel'))
    print("Model saved to Models/titanicmodel")

if __name__ == '__main__':
    main()