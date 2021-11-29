from MLVisualizationTools import Analytics, Interfaces, Graphs, Colorizers, DataInterfaces
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

def main(show=True):
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    grid = Colorizers.binary(grid)
    DataInterfaces.addClumpedData(grid, df, 'Survived')

    # plt, _, _ = Graphs.matplotlibGraph(grid, title="Clumped Data")
    # plt.show(block=False)

    fig = Graphs.plotlyGraph(grid)
    if show: # pragma no cover
        fig.show()

    grid = Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    grid = Colorizers.binary(grid)
    DataInterfaces.addPercentageData(grid, df, 'Survived')
    # plt, _, _ = Graphs.matplotlibGraph(grid, title="Percentage Data")
    # plt.show()

    fig = Graphs.plotlyGraph(grid)
    if show:  # pragma no cover
        fig.show()

print("This demo shows data overlay features with plotly.")
print("To run the demo, call DataOverlayDemo.main()")

if __name__ == "__main__":
    main()