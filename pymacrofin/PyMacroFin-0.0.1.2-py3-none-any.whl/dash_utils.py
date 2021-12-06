import dash
from dash import dcc
from dash import html
from dash.dependencies import Input,Output
import argparse
import webbrowser
from threading import Timer
import pickle
import pandas as pd
import dash_daq as daq
try:
    from PyMacroFin.grid import grid
    import PyMacroFin.utilities as util
except:
    from grid import grid
    import utilities as util
from flask import request


app = dash.Dash(__name__,external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'])
title_text = "PyMacroFin Model Visualization"
app.layout = html.Div([ html.H1(id='header',
                                className='banner',
                                children=title_text),
                        dcc.Interval(id='header-update',interval=10000,n_intervals=0),
                        html.Div([
                            html.Div([
                                dcc.Graph(id='fig1',figure={}),
                                dcc.Interval(id='fig1_update',interval=100000,n_intervals=0)
                                ]),
                            html.Div([dcc.Graph(id='fig2',figure={}),
                                      dcc.Interval(id='fig2_update',interval=100000,n_intervals=0)])
                            ])#,
                        #daq.StopButton(id='stop-button',
                        #               label='Shutdown Visualization',
                        #               buttonText='Shut Down',
                        #               n_clicks=0)
                        ])
                        
        
@app.callback(Output('fig1','figure'),Input('fig1_update','n_intervals'))
def update_dash1(interval):
    """
    Utility pipe function for updating dash application from the utilities module
    """
    df = pd.read_csv('./tmp{}/dash_data.csv'.format(name))
    figs = util.plot(m,df)
    return figs[0]
    
@app.callback(Output('fig2','figure'),Input('fig2_update','n_intervals'))
def update_dash2(interval):
    """
    Utility pipe function for updating dash application from the utilities module
    """
    df = pd.read_csv('./tmp{}/dash_data.csv'.format(name))
    figs = util.plot(m,df)
    return figs[1]
    
@app.callback(Output('header','children'),Input('header-update','n_intervals'))
def update_dash3(interval):
    """
    Utility pipe function for updating dash application from the utilities module
    """
    return title_text+': {}'.format(name)
    
#def shutdown_server():
#    func = request.environ.get('werkzeug.server.shutdown')
#    if func is None:
#        raise RuntimeError('Not running with the Werkzeug Server')
#    func()
    
#@app.callback(Output('header','children'),Input('stop-button','n_clicks'))
#def shutdown(n):
#    if n>1:
#        shutdown_server()
#        return 'Visualization shutting down...'
#    else:
#        return 
    
    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--name',help='set name of model')
    parser.add_argument('-d','--dash_debug')
    parser.add_argument('-p','--port',help='set port')
    args = parser.parse_args()
    
    if args.name:
        name = args.name
    else:
        name = ''
    if args.dash_debug:
        dash_debug = args.dash_debug
    else:
        dash_debug = True
    if args.port:
        myport = args.port
    else:
        myport = 8050

    m = pickle.load(open('./tmp{}/init.pkl'.format(name),'rb')) 
    m.grid = grid(m.options)
 
    app.run_server(debug=dash_debug,port=myport)
