from dash import html
from rats.callbackfunctions.interscanappcallbacks import createcontent

def create_layout(children):
    layout = html.Div([
        html.Br(),
        html.Div(
            [html.Div(
                [html.Div(
                    [html.Button(id='pulldatainterscan', children='Pull the data into Interscan app',
                                 className='btn btn-secondary', type='button')
                     ], id='interscanpullcontainer', className='col-12 text-center')
                 ], className='row')
             ], className='container text-center'),

        html.Br(),

        html.Div(id='interscanappplots', children=children,
                 className='container-fluid text-center'),
        ########################################
    ], className='container-fluid')
    return layout


children = createcontent(3)
layout = html.Div([
        html.Br(),
        html.Div(
            [html.Div(
                [html.Div(
                    [html.Button(id='pulldatainterscan', children='Pull the data into Interscan app',
                                 className='btn btn-secondary', type='button')
                     ], id='interscanpullcontainer', className='col-12 text-center')
                 ], className='row')
             ], className='container text-center'),

        html.Br(),

        html.Div(id='interscanappplots', children=children,
                 className='container-fluid text-center'),
        ########################################
    ], className='container-fluid')
