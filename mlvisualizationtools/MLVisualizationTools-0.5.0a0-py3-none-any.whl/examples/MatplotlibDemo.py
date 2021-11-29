from MLVisualizationTools import Analytics, Interfaces, Graphs, Colorizers
from MLVisualizationTools.backend import fileloader
import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # stops agressive error message printing
from tensorflow import keras

try:
    import matplotlib.pyplot
except ImportError:
    raise ImportError("Matplotlib is required to run this demo. If you don't have matplotlib installed, install it"
                      " with `pip install matplotlib` or run the plotly demo instead.")

def main():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    grid = Colorizers.simple(grid, 'red')

    plt, _, _ = Graphs.matplotlibGraph(grid, title="Max Variance")
    plt.show(block=False)

    grid = Interfaces.predictionGrid(model, 'Parch', 'SibSp', df, ["Survived"])
    grid = Colorizers.binary(grid, highcontrast=True)
    plt, _, _ = Graphs.matplotlibGraph(grid, title="Parch by SibSp")
    plt.show()

print("This demo shows basic features with tensorflow and matplotlib.")
print("To run the demo, call MatplotlibDemo.main()")

if __name__ == "__main__":
    main()