from IPython.display import display_html
import plotly.graph_objs as go
import matplotlib.pyplot as plt

# ~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<
# BASIC Visualization FUNCTIONS <~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~
# ~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<


def display_side_by_side(*args):
    '''Pleasing display of the given tables side by side ~ display_side_by_side(df1, df2)'''
    html_str=''
    for df in args:
        if type(df) == list:
            for t in df: 
                html_str+=t.to_html()
        else:
            html_str+=df.to_html()
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)


def draw_scatter_plot(X,
                      Y,
                      graph_name='Title', 
                      color='Green',
                      labels=[],
                      msize=10,
                      mode='markers'):
    '''Add a scatter plot to the data going into a figure
    '''
    if len(labels)==0:
        labels=list(X.index)
    
    scatter=go.Scatter(
        name=graph_name,
        x = X,
        y = Y,
        mode='markers',
        marker=dict(
            color=color,
            size=msize),
        text=labels
        )
    
    return scatter 


