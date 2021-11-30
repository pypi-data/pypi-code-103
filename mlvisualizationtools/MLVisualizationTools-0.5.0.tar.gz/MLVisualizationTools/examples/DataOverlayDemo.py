from MLVisualizationTools import Analytics, Interfaces, Graphs, Colorizers, DataInterfaces
from MLVisualizationTools.backend import fileloader
import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # stops agressive error message printing
from tensorflow import keras
import warnings

hasplotly = False
hasmatplotlib = False

try:
    import plotly
    hasplotly = True
except ImportError:
    try:
        import matplotlib.pyplot
        hasmatplotlib = True
        warnings.warn("Plotly is recommended to run this demo. If you don't have plotly installed, install it"
                      " with `pip install plotly`. Running with matplotlib and limited functionality.")
    except ImportError:
        raise ImportError("Plotly is required to run this demo. If you don't have plotly installed, install it"
                          " with `pip install plotly` or install matplotlib for limited features instead.")
    raise ImportError()

def main(show=True):
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    grid = Colorizers.binary(grid)
    DataInterfaces.addClumpedData(grid, df, 'Survived')

    if hasplotly:
        fig = Graphs.plotlyGraph(grid, title="Clumped Data")
        if show:  # pragma no cover
            fig.show()

    elif hasmatplotlib:
        plt, _, _ = Graphs.matplotlibGraph(grid, title="Clumped Data")
        plt.show(block=False)

    else:
        raise Exception("Plotly and matplotlib missing.")

    grid = Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    grid = Colorizers.binary(grid)
    DataInterfaces.addPercentageData(grid, df, 'Survived')

    if hasplotly:
        fig = Graphs.plotlyGraph(grid, title="Percentage Data")
        if show:  # pragma no cover
            fig.show()

    elif hasmatplotlib:
        plt, _, _ = Graphs.matplotlibGraph(grid, title="Percentage Data")
        plt.show(block=False)

    else:
        raise Exception("Plotly and matplotlib missing.")

print("This demo shows data overlay features with plotly.")
print("To run the demo, call DataOverlayDemo.main()")

if __name__ == "__main__":
    main()