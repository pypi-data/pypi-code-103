from MLVisualizationTools import Analytics, Interfaces, Graphs, Colorizers
from MLVisualizationTools.dashbackend import getTheme, getDashApp
import pandas as pd

try:
    import dash
    from dash import Input, Output
    from dash import dcc
    from dash import html
    import dash_bootstrap_components as dbc
    from dash_tour_component import DashTour
    import plotly
except ImportError:
    raise ImportError("Dash and plotly are required to use this tool. Install them with the [dash] flag"
                      " on installation of this library.")

class App:
    def __init__(self, model, data: pd.DataFrame, title:str = "DashModelVisualizer", theme:str = "dark", folder = None,
                 highcontrast:bool = True, notebook:bool = False, usetunneling:bool = False, mode:str = 'external',
                 host:str = '0.0.0.0', port: bool = None):

        theme, folder, self.figtemplate = getTheme(theme, folder)
        self.app, self.runFunc = getDashApp(title, notebook, usetunneling, host, port, mode, theme, folder)

        self.model = model
        self.df = data
        self.highcontrast = highcontrast

        options = []
        for col in self.df.columns:
            options.append({'label': col, 'value': col})

        self.AR = Analytics.analyzeModel(self.model, self.df)
        self.maxvar = self.AR.maxVariance()

        self.x = self.maxvar[0].name
        self.y = self.maxvar[1].name

        self.fig = self.updateGraph()

        graph = dbc.Card([
            dcc.Graph(id='example-graph', figure=self.fig)
        ], body=True)

        config = dbc.Card([
            dbc.Label("X Axis: "),
            dcc.Dropdown(id='xaxis', options=options, value=self.x),
            html.Br(),
            dbc.Label("Y Axis: "),
            dcc.Dropdown(id='yaxis', options=options, value=self.y),
            html.Br(),
            dbc.Button("Open Tour", id='open_tour_button'),
            html.Br(),
        ], body=True)

        tour = DashTour(steps=[{'selector': '[id="xaxis"]',
                                'content': "This dropdown controls the xaxis, it has been preset with the "
                                           "highest variance value."},
                               {'selector': '[id="yaxis"]',
                                'content': "This dropdown controls the yaxis, it has been preset with the "
                                           "second highest variance value."},
                               {'selector': '[id="example-graph"]',
                                'content': "This graph updates when you change the dropdowns."}],
                        isOpen=False,
                        id="tour_component",
                        children=html.Div(),
                        rounded=7
                        )

        self.app.layout = dbc.Container([
            tour,
            html.H1(title),
            html.Hr(),
            dbc.Row([
                dbc.Col(config, md=4),
                dbc.Col(graph, md=8)]
            ),
            html.P()],
            fluid=True,
            className='dash-bootstrap'
        )

        inputs = [Input('xaxis', "value"), Input('yaxis', 'value')]
        self.app.callback(Output("example-graph", "figure"), inputs)(self.updateGraphFromWebsite)
        self.app.callback(Output('tour_component', 'isOpen'), [Input('open_tour_button', 'n_clicks')],
                          prevent_initial_call=True)(lambda _ : True)

    def run(self):
        self.runFunc()

    def updateGraph(self):
        try:
            data = Interfaces.predictionGrid(self.model, self.x, self.y, self.df)
            data = Colorizers.binary(data, highcontrast=self.highcontrast)
            self.fig = Graphs.plotlyGraph(data)
            self.fig.update_layout(template=self.figtemplate)
        except AssertionError:
            pass #User cleared their selection
        return self.fig

    def updateGraphFromWebsite(self, x, y):
        self.x = x
        self.y = y
        return self.updateGraph()

def visualize(model, data: pd.DataFrame, title:str = "DashModelVisualizer", theme:str = "dark", folder = None,
              highcontrast:bool = True, notebook:bool = False, usetunneling:bool = False, mode:str = 'external',
              host:str = '0.0.0.0', port: bool = None):
    """
    Creates a dash website to visualize an ML model.

    :param model: A tensorflow keras model
    :param data: A pandas dataframe, all df columns must be numerical model inputs
    :param title: Title for website
    :param theme: Theme to load app in, can be a string (light / dark) or a url to load a stylesheet from
    :param folder: Directory to load additional css and js from
    :param highcontrast: Visualizes the model with orange and blue instead of green and red. Great for colorblind people!
    :param notebook: Uses jupyter dash instead of dash
    :param usetunneling: Enables ngrok tunneling for use in notebooks that don't have built in dash support, like kaggle
    :param mode: Use 'external', 'inline', or 'jupyterlab'
    :param host: default hostname for dash
    :param port: None for default port (8050) or (1005)
    """
    App(model, data, title, theme, folder, highcontrast, notebook, usetunneling, mode, host, port).run()
