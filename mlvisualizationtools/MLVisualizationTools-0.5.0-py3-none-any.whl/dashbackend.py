from MLVisualizationTools.backend import fileloader

def getTheme(theme, folder=None, figtemplate=None):
    """
    Backend function for loading theme css files.

    Theme can be 'light' or 'dark', and that will autoload the theme from dbc
    If folder is none, it is set based on the theme
    If figtemplate is none, it is set based on the theme

    Returns theme, folder

    :param theme: 'light' / 'dark' or a css url
    :param folder: path to assets folder
    :param figtemplate: Used for putting plotly in dark theme
    """
    import dash_bootstrap_components as dbc
    if theme == "light":
        theme = dbc.themes.FLATLY
        if folder is None:
            folder = fileloader('theme_assets/light_assets')
        if figtemplate is None:
            figtemplate = "plotly"

    elif theme == "dark":
        theme = dbc.themes.DARKLY
        if folder is None:
            folder = fileloader('theme_assets/dark_assets')
        if figtemplate is None:
            figtemplate = "plotly_dark"

    return theme, folder, figtemplate

def getDashApp(title:str, notebook:bool, usetunneling:bool, host:str, port:int, mode: str, theme, folder):
    """
    Creates a dash or jupyter dash app, returns the app and a function to run it

    :param title: Passed to dash app
    :param notebook: Uses jupyter dash with default port of 1005 (instead of 8050)
    :param usetunneling: Enables ngrok tunneling for kaggle notebooks
    :param host: Passed to dash app.run()
    :param port: Can be used to override default ports
    :param mode: Could be 'inline', 'external', or 'jupyterlab'
    :param theme: Passed to dash app external stylesheets
    :param folder: Passed to assets folder to load theme css
    """

    if port is None:
        if notebook:
            port = 1005
        else:
            port = 8050

    if notebook:
        if usetunneling:
            try:
                from pyngrok import ngrok
            except ImportError:
                raise ImportError("Pyngrok is required to run in a kaggle notebook. "
                                  "Use pip install MLVisualizationTools[kaggle-notebook]")
            ngrok.kill() #disconnects active tunnels
            tunnel = ngrok.connect(port)
            print("Running in an ngrok tunnel. This limits you to 40 requests per minute and one active app.",
                  "For full features use google colab instead.")
            url = tunnel.public_url
        else:
            url = None

        try:
            from jupyter_dash import JupyterDash
        except ImportError:
            raise ImportError("JupyterDash is required to run in a notebook. "
                              "Use pip install MLVisualizationTools[dash-notebook]")
        app = JupyterDash(__name__, title=title, server_url=url,
                               external_stylesheets=[theme], assets_folder=folder)

    else:
        from dash import Dash
        app = Dash(__name__, title=title, external_stylesheets=[theme], assets_folder=folder)

    def runApp():
        if notebook:
            app.run_server(host=host, port=port, mode=mode, debug=True)
        else:
            app.run_server(host=host, port=port, debug=True)

    return app, runApp