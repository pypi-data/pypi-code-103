import pandas as pd
import matplotlib.pyplot as plt

import bluebelt.core.graph
import bluebelt.core.helpers

def _get_data(_obj, **kwargs):

    columns = kwargs.get('columns', None)

    if isinstance(_obj, pd.DataFrame) and isinstance(columns, (str, list)):
        return _obj[columns]
    elif isinstance(_obj, pd.Series):
        return pd.DataFrame(_obj)
    else:
        return _obj

def _get_name(_obj, **kwargs):

    if isinstance(_obj, pd.Series):
        return _obj.name
    elif isinstance(_obj, pd.DataFrame):
        names = []
        for col in _obj.columns:
            names.append(col)
        return bluebelt.core.helpers._get_nice_list(names)
    else:
        return None
    
    
def line(_obj, **kwargs):
    """
    Make a line plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """

    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{_get_name(_obj)} line plot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    frame = _get_data(_obj, **kwargs)

    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    for col in frame:
        bluebelt.core.graph.line(series=frame[col], ax=axes, style=style)
        
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.line.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

def scatter(_obj, **kwargs):
    """
    Make a scatter plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    style = kwargs.pop('style', bluebelt.styles.paper)
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    frame = _get_data(_obj, **kwargs)

    if frame.shape[1] >= 2:
        title = kwargs.pop('title', f'{_get_name(frame.iloc[:,:2])} scatter plot')
        index_name = frame.columns[0]
        frame = pd.DataFrame(data={frame.columns[1]: frame.iloc[:,1].values}, index=frame.iloc[:,0].values)
        frame.index.name = index_name
    else:
        title = kwargs.pop('title', f'{_get_name(_obj)} scatter plot')
    
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    bluebelt.core.graph.scatter(series=frame, ax=axes, style=style)
        
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.scatter.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

def area(series, **kwargs):
    """
    Make an area plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    
    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{_get_name(series)} area plot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    bluebelt.core.graph.area(series=series, ax=axes, style=style)
        
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.area.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

def hist(series, **kwargs):
    """
    Make a histogram plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        fit: boolean
            fit a normal distribution
            default value: False
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    
    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{_get_name(series)} histogram')
    
    path = kwargs.pop('path', None)
    fit = kwargs.pop('fit', False)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    bluebelt.core.graph.hist(series=series, ax=axes, style=style, fit=fit)
        
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.area.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

histogram = hist

def boxplot(_obj, **kwargs):
    """
    Make a boxplot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    
    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{_get_name(_obj)} boxplot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    frame = _get_data(_obj, **kwargs)

    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    bluebelt.core.graph.boxplot(series=frame.values, ax=axes, style=style)
        
    # format things
    axes.set_xticklabels(frame.columns)
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
            
    # title
    axes.set_title(title, **style.graphs.boxplot.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig
    