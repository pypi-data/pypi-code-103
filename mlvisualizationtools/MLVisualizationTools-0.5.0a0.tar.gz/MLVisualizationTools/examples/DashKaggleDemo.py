from werkzeug.serving import is_running_from_reloader

def main(theme='dark', highcontrast=True, mode='external'):
    """
    Runs the demo by calling DashModelVisualizer

    :param theme: theme, could be 'light' or 'dark'
    :param highcontrast: Use blue and orange coloring instead of red and green
    :param mode: where to put the website, could be 'inline' / 'external' / 'jupyterlab'
    """
    from MLVisualizationTools.express import DashModelVisualizer
    from MLVisualizationTools.backend import fileloader
    import pandas as pd
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # stops agressive error message printing
    from tensorflow import keras

    model = keras.models.load_model(fileloader('examples/Models/titanicmodel'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))
    df = df.drop("Survived", axis=1)
    DashModelVisualizer.visualize(model, df, title="DashKaggleDemo", theme=theme,
                                  highcontrast=highcontrast, notebook=True, mode=mode, usetunneling=True)

if not is_running_from_reloader():
    print("This demo is for use inside a jupyter notebook that does not supports dash natively (such as kaggle).")
    print("It uses the default precompiled model. To run the demo, call DashKaggleDemo.main()")

if __name__ == "__main__":
    main()