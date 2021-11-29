"""
Graph Interface

A set of functions to graph data. Matplotlib and plotly are supported.
"""

#We use just-in-time importing here to improve load times
#Here are the imports:
#import plotly.express as px
#import matplotlib.pyplot as plt
from MLVisualizationTools.types import GraphDataTypes, GraphOutputTypes, ColorizerModes
from MLVisualizationTools import Colorizers 
from MLVisualizationTools.backend import GraphData
from typing import Optional
import copy


class WrongDataFormatException(Exception):
    pass

def graph(data: GraphData, graphtype: GraphOutputTypes = GraphOutputTypes.Auto, title="", legend: bool =True,
          sizekey: Optional[str] = None):
    """
    Calls correct graph type based on data format and mode chosen
    
    :param data: GraphData from interface call
    :param graphtype: Matplotlib or plotly
    :param title: Title for graph
    :param legend: Show a key for the colors used
    :param sizekey: Should match with datainterface sizekey if used
    """

    if graphtype == GraphOutputTypes.Auto:
        try:
            import plotly
            return plotlyGraph(data, title, legend, sizekey)
        except ImportError:
            try:
                import matplotlib
                return matplotlibGraph(data, title, legend, sizekey)
            except ImportError:
                raise ImportError("Either matplotlib or plotly is required to use graphs. Install them with pip.")

    elif graphtype == GraphOutputTypes.Plotly:
        return plotlyGraph(data, title, legend, sizekey)
    elif graphtype == GraphOutputTypes.Matplotlib:
        return matplotlibGraph(data, title, legend, sizekey)
    else:
        raise Exception(f"GraphType {graphtype} not recognized.")

def plotlyGraph(data: GraphData, title="", legend: bool=True, sizekey: Optional[str] = None):
    """
    Calls correct graph type based on data format
    
    :param data: GraphData from interface call
    :param title: Title for graph
    :param legend: Show a key for the colors used
    :param sizekey: Should match with datainterface sizekey if used
    """
    if data.datatype is GraphDataTypes.Grid:
        return plotlyGrid(data, title, legend, sizekey)
    elif data.datatype is GraphDataTypes.Animation:
        return plotlyAnimation(data, title, legend, sizekey)
    else:
        raise Exception(f"DataType {data.datatype} not recognized.")

def matplotlibGraph(data: GraphData, title="", legend: bool=True, sizekey: Optional[str] = None):
    """
    Calls correct graph type based on data format
    
    :param data: GraphData from interface call
    :param title: Title for graph
    :param legend: Show a key for the colors used
    :param sizekey: Should match with datainterface sizekey if used
    """
    
    if data.datatype is GraphDataTypes.Grid:
        return matplotlibGrid(data, title, legend, sizekey)
    elif data.datatype is GraphDataTypes.Animation:
        return matplotlibAnimation(data, title, legend, sizekey) #Unsupported
    else:
        raise Exception(f"DataType {data.datatype} not recognized.")


def _applyDefaultFormat(data: GraphData):
    """Internal function used by graphs to make datapoints stand out"""
    if data.modeldata.colorized == ColorizerModes.NotColorized:
        data = Colorizers.simple(data, 'blue', apply_to_model=True, apply_to_data=False)
    if data.datavalues is not None:
        if data.datavalues.colorized == ColorizerModes.NotColorized:
            data = Colorizers.simple(data, 'black', apply_to_data=True, apply_to_model=False)

        df = data.datavalues.dataframe
        df[data.sizekey] = df[data.sizekey].apply(lambda x: x * 50 / df[data.sizekey].max())

    data.modeldata.dataframe[data.sizekey] = 5
    return data

def _plotlyGraphCore(data: GraphData, title, legend):
    """Internal function for plotly graphing, users should call plotlyGraph() instead"""
    try:
        import plotly.express as px
    except ImportError:
        raise ImportError("Plotly is required to use this graph. Install with `pip install plotly`")
    
    sm = 50 if data.datavalues is not None else None

    cdm = {}
    order = []
    locations = [data.modeldata]
    if data.datavalues is not None:
        locations.append(data.datavalues)

    for datavals in locations:
        for colordata in [datavals.truecolor, datavals.falsecolor, datavals.basecolor]:
            if colordata.color is not None:
                cdm[colordata.message] = colordata.color
                order.append(colordata.message)
                
                df = datavals.dataframe
                df.loc[df[data.colorkey] == colordata.color, data.colorkey] = colordata.message

    if data.datavalues is not None:
        combined_df = data.modeldata.dataframe.append(data.datavalues.dataframe)
    else:
        combined_df = data.modeldata.dataframe

    fig = px.scatter_3d(combined_df, data.x, data.y, data.outputkey, animation_frame=data.anim, color=data.colorkey,
                        color_discrete_map=cdm, category_orders={data.colorkey: order}, opacity=1, size=data.sizekey,
                        title=title, range_z=[combined_df[data.outputkey].min(), combined_df[data.outputkey].max()],
                        size_max=sm)

    fig.update_layout(showlegend=legend and len(order) > 0)
    fig.update_traces(marker={'line_width': 0})
    return fig

def plotlyGrid(data: GraphData, title="", legend: bool=True, sizekey: Optional[str] = None):
    """
    Calls px.scatter_3d with data. Returns a plotly figure.

    :param data: GraphData from interface call
    :param title: Title for graph
    :param legend: Show a key for the colors used
    :param sizekey: Should match with datainterface sizekey if used
    """
    if data.datatype != GraphDataTypes.Grid:
        raise WrongDataFormatException("Data was not formatted in grid.")
    
    if sizekey is not None:
        data.sizekey = sizekey
    data.check_size_key()

    data = _applyDefaultFormat(copy.deepcopy(data))

    # Consistency with plotly animation key style
    locations = [data.modeldata]
    if data.datavalues is not None:
        locations.append(data.datavalues)
    for datavals in locations:
        orig_row = datavals.dataframe.iloc[0]
        for color in [datavals.basecolor, datavals.truecolor, datavals.falsecolor]:  # apply each color
            if color.color is not None:
                row = copy.deepcopy(orig_row)
                row[data.colorkey] = color.color
                row[data.sizekey] = 0
                datavals.dataframe = datavals.dataframe.append(row)

    return _plotlyGraphCore(data, title, legend)

def plotlyAnimation(data: GraphData, title="", legend: bool=True, sizekey: Optional[str] = None):
    """
    Calls px.scatter_3d with data and animation frame. Returns a plotly figure.

    :param data: GraphData from interface call
    :param title: Title for graph
    :param legend: Show a key for the colors used
    :param sizekey: Key to use in dataframe to store size values, should match with datainterface sizekey if used
    """
    if data.datatype != GraphDataTypes.Animation:
        raise WrongDataFormatException("Data was not formatted in animation.")
    
    if sizekey is not None:
        data.sizekey = sizekey
    data.check_size_key()

    data = _applyDefaultFormat(copy.deepcopy(data))

    # plotly animations have a bug where points aren't rendered unless
    # one point of each color is in frame
    locations = [data.modeldata]
    if data.datavalues is not None:
        locations.append(data.datavalues)
    for datavals in locations:
        orig_row = datavals.dataframe.iloc[0]
        for animval in data.modeldata.dataframe[data.anim].unique(): #apply to each frame (use model data for smoother animation)
            for color in [datavals.basecolor, datavals.truecolor, datavals.falsecolor]: #apply each color
                if color.color is not None:
                    row = copy.deepcopy(orig_row)
                    row[data.colorkey] = color.color
                    row[data.sizekey] = 0
                    row[data.anim] = animval
                    datavals.dataframe = datavals.dataframe.append(row)

    return _plotlyGraphCore(data, title, legend)

def matplotlibGrid(data: GraphData, title="", legend: bool = True, sizekey: Optional[str] = None):
    """
    Calls ax.scatter with data. Returns a plt instance, a fig, and the ax.

    :param data: GraphData from interface call
    :param title: Title for graph
    :param legend: Should show legend
    :param sizekey: Unused in this graph form
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        raise ImportError("Matplotlib is required to use this graph. Install with `pip install matplotlib`")

    if data.datatype != GraphDataTypes.Grid:
        raise WrongDataFormatException("Data was not formatted in grid.")

    if sizekey is not None:
        data.sizekey = sizekey
    data.check_size_key()

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    data = _applyDefaultFormat(copy.deepcopy(data))

    if legend:
        patches = []
        locations = [data.modeldata]
        if data.datavalues is not None:
            locations.append(data.datavalues)

        for datavals in locations:
            if datavals.colorized == ColorizerModes.Binary:
                patches.append(mpatches.Patch(color=datavals.truecolor.color, label=datavals.truecolor.message))
                patches.append(mpatches.Patch(color=datavals.falsecolor.color, label=datavals.falsecolor.message))

            if datavals.colorized == ColorizerModes.Simple:
                patches.append(mpatches.Patch(color=datavals.basecolor.color, label=datavals.basecolor.message))

        if len(patches) > 1:
            ax.legend(handles=patches)

    df = data.modeldata.dataframe
    ax.scatter(df[data.x], df[data.y], df[data.outputkey], c=df[data.colorkey])

    if data.datavalues is not None:
        df = data.datavalues.dataframe
        ax.scatter(df[data.x], df[data.y], df[data.outputkey], s=df[data.sizekey], c=df[data.colorkey])

    ax.set_xlabel(data.x)
    ax.set_ylabel(data.y)
    ax.set_zlabel(data.outputkey)
    ax.set_title(title)

    return plt, fig, ax

def matplotlibAnimation(_data: GraphData, _title="", _legend: bool = True, _sizekey: Optional[str] = None):
    """This function is not implemented and is not planned to be implemented in the future."""
    raise NotImplementedError("Matplotib does not support animations cleanly. This is not planned to be added in the "
                              "future. Use plotly instead (`pip install plotly`)")