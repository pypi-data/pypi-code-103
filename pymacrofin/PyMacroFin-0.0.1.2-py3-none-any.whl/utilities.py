import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import cloudpickle
import os
import time
import subprocess
import scipy.stats as stats
import multiprocessing as mp
from threading import Timer
import webbrowser
from copy import deepcopy


pio.renderers.default = 'browser'

def boundary_assignment(n0,n1):
    """
    Create a vector of boundtags to assign boundaries
    """
    #"b0{0}_b1{1}".format(bounds[0],bounds[1])
    # bounds = 'min','','max'
    myarray = pd.DataFrame(np.ones((n1,n0))*np.nan)
    myarray.iloc[:,:] = 'b0_b1'
    myarray.iloc[0,:] = 'b0_b1min'
    myarray.iloc[:,0] = 'b0min_b1'
    myarray.iloc[-1,:] = 'b0_b1max'
    myarray.iloc[:,-1] = 'b0max_b1'
    myarray.iloc[0,0] = 'b0min_b1min'
    myarray.iloc[-1,-1] = 'b0max_b1max'
    myarray.iloc[-1,0] = 'b0min_b1max'
    myarray.iloc[0,-1] = 'b0max_b1min'
    result = myarray.to_numpy().flatten(order='F')
    return result
    
def get_shifted(vector,dimension,direction,n0,n1,distance=1):
    """
    From a flattened array get shifted data in the dimension given (0 or 1) and 
    direction specified (m or p)
    """
    assert dimension in [0,1], "invalid dimension"
    switch = {0:1,1:0}
    dimension = switch[dimension]
    assert direction in ['p','m'], "invalid direction"
    #myarray = pd.DataFrame(vector.to_numpy().reshape([n0,n1],order='F'))
    myarray = pd.DataFrame(vector.to_numpy().reshape([n1,n0],order='F'))
    if direction == 'p':
        result = myarray.shift(-1*distance,axis=dimension)
    elif direction == 'm':
        result = myarray.shift(distance,axis=dimension)
    result = np.reshape(result.to_numpy(),n0*n1,order='F')
    return result    

def shift_prices(m,df):
    """
    Shift prices before calculating price derivatives
    """
    for var in m.prices:
        for direc in ['m','p']:
            for i in range(len(m.state)):
                df['_{0}{1}{2}'.format(var,direc,m.state[i])] = get_shifted(df[var],i,direc,m.options.n0,m.options.n1)
    return df
    
def shift_derivatives(m,df):
    """
    Add shifted derivatives to dataframe
    """
    for var in m.prices+m.value:
        for direc in ['m','p']:
            df['_{0}{1}{2}{3}{1}'.format(var,m.state[0],m.state[1],direc)] = get_shifted(df['_{0}{1}{2}'.format(var,m.state[0],m.state[1])],0,direc,m.options.n0,m.options.n1)
            df['_{0}{1}{2}{3}{2}'.format(var,m.state[0],m.state[1],direc)] = get_shifted(df['_{0}{1}{2}'.format(var,m.state[0],m.state[1])],1,direc,m.options.n0,m.options.n1)
            if m.options._legacy_price_deriv:
                df['_{0}{1}{2}{1}{3}{1}'.format(var,m.state[0],m.state[1],direc)] = get_shifted(df['_{0}{1}{2}{1}'.format(var,m.state[0],m.state[1])],0,direc,m.options.n0,m.options.n1)
                df['_{0}{1}{2}{2}{3}{2}'.format(var,m.state[0],m.state[1],direc)] = get_shifted(df['_{0}{1}{2}{2}'.format(var,m.state[0],m.state[1])],1,direc,m.options.n0,m.options.n1)
                df['_{0}{1}{2}{1}{3}{2}'.format(var,m.state[0],m.state[1],direc)] = get_shifted(df['_{0}{1}{2}{1}'.format(var,m.state[0],m.state[1])],1,direc,m.options.n0,m.options.n1)
                df['_{0}{1}{2}{2}{3}{1}'.format(var,m.state[0],m.state[1],direc)] = get_shifted(df['_{0}{1}{2}{2}'.format(var,m.state[0],m.state[1])],0,direc,m.options.n0,m.options.n1)
        for i in range(len(m.state)):
            if i == 1:
                j = 0
            elif i == 0:
                j = 1
            for direc in ['m','p']:
                df['_{0}{2}{1}'.format(var,m.state[i],direc)] = get_shifted(df[var],i,direc,m.options.n0,m.options.n1)
                df['_{0}{1}{2}{1}'.format(var,m.state[i],direc)] = get_shifted(df['_{0}{1}'.format(var,m.state[i])],i,direc,m.options.n0,m.options.n1)
                df['_{0}{1}{2}{3}'.format(var,m.state[j],direc,m.state[i])] = get_shifted(df['_{0}{1}'.format(var,m.state[j])],i,direc,m.options.n0,m.options.n1)
                if m.options._legacy_price_deriv:
                    df['_{0}{1}{1}{2}{1}'.format(var,m.state[i],direc)] = get_shifted(df['_{0}{1}{1}'.format(var,m.state[i])],i,direc,m.options.n0,m.options.n1)
                    df['_{0}{1}{1}{1}{2}{1}'.format(var,m.state[i],direc)] = get_shifted(df['_{0}{1}{1}'.format(var,m.state[i])],i,direc,m.options.n0,m.options.n1)
    return df
    
def initialization(m):
    """
    Initialize data from initial values for endogenous variables
    """
    df = pd.DataFrame(np.ones((m.options.N,len(m.endog))),columns=m.endog)
    for i,x in enumerate(m.endog):
        df[x] = m.endog_init[i]
    for i,x in enumerate(m.value):
        df[x] = m.value_init[i]
    for i,p in enumerate(m.params.names):
        df[p] = m.params.values[i]
    for i,s in enumerate(m.state):
        df[s] = np.reshape(m.grid.x[i],[m.options.N,1],order='F')
    for var in m.prices+m.value:
        for i in range(len(m.state)):
            df["_{0}{1}".format(var,m.state[i])] = 0
            df["_{0}{1}{1}".format(var,m.state[i])] = 0
            if m.options._legacy_price_deriv:
                df["_{0}{1}{1}{1}".format(var,m.state[i])] = 0
        df["_{0}{1}{2}".format(var,m.state[0],m.state[1])] = 0
        if m.options._legacy_price_deriv:
            df["_{0}{1}{2}{1}".format(var,m.state[0],m.state[1])] = 0
            df["_{0}{1}{2}{2}".format(var,m.state[0],m.state[1])] = 0
    df = shift_derivatives(m,df)
    # initialize spatial differences
    for i in range(len(m.state)):
        df["_dm{}".format(m.state[i])] = np.reshape(m.grid.dm[i],[m.options.N,1],order='F')
        df["_dp{}".format(m.state[i])] = np.reshape(m.grid.dp[i],[m.options.N,1],order='F')
    df['boundtag'] = boundary_assignment(m.options.n0,m.options.n1)
    for i,eq in enumerate(m.equations):
        for boundtag in df.boundtag.unique():
            args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,eq.name))
            df.loc[df['boundtag']==boundtag,eq.name] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,eq.name,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(a) for a in args])))
    for tup in m.hjb_equations.keys():
        for boundtag in df.boundtag.unique():
            name = "_{0}_{1}".format(tup[0],tup[1])
            args = eval("m.engine.{0}_{1}{2}hjbfcn_args".format(boundtag,tup[0],tup[1]))
            df.loc[df['boundtag']==boundtag,name] = eval("m.engine.{0}_{1}{2}hjbfcn({3})".format(boundtag,tup[0],tup[1],','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
    df['_sidx'] = np.nan # system index 
    return df
    
def initialize_from_guess(m):
    """
    Initialize from data in a guess file. 
    The guess file should have all value, state, and endogenous variables
    """
    # considerations... ordering (will the user provide the correct order)
    # ... does the user's state input match the grid input provided by the user
    df = pd.read_csv(m.options.import_guess_location)
    for i,p in enumerate(m.params.names):
        df[p] = m.params.values[i]
    df['boundtag'] = boundary_assignment(m.options.n0,m.options.n1)
    # initialize spatial differences
    for i in range(len(m.state)):
        df["_dm{}".format(m.state[i])] = np.reshape(m.grid.dm[i],[m.options.N,1],order='F')
        df["_dp{}".format(m.state[i])] = np.reshape(m.grid.dp[i],[m.options.N,1],order='F')
    df = shift_prices(m,df)
    # don't use drifts (monotonicity scheme) to initialize since it's a circular problem initially if drifts depend on derivatives (also set cross derivative to zero initially)
    df = finite_difference(m,df,target='value',use_drifts=False) # value derivatives
    df = finite_difference(m,df,target='prices',use_drifts=False) # some price derivatives
    df = shift_derivatives(m,df)
    df = calculate_price_derivatives(m,df) # now recalculate the price derivatives better
    for i,eq in enumerate(m.equations):
        for boundtag in df.boundtag.unique():
            args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,eq.name))
            df.loc[df['boundtag']==boundtag,eq.name] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,eq.name,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(a) for a in args])))
    for tup in m.hjb_equations.keys():
        for boundtag in df.boundtag.unique():
            name = "_{0}_{1}".format(tup[0],tup[1])
            args = eval("m.engine.{0}_{1}{2}hjbfcn_args".format(boundtag,tup[0],tup[1]))
            df.loc[df['boundtag']==boundtag,name] = eval("m.engine.{0}_{1}{2}hjbfcn({3})".format(boundtag,tup[0],tup[1],','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
    df['_sidx'] = np.nan # system index 
    return df
    
def initialize_from_function(m):
    """
    Initialize from a guess function 
    """
    df = pd.DataFrame(np.ones((m.options.N,len(m.endog))),columns=m.endog)
    for i,p in enumerate(m.params.names):
        df[p] = m.params.values[i]
    for i,s in enumerate(m.state):
        df[s] = np.reshape(m.grid.x[i],[m.options.N,1],order='F')
    for n in range(m.options.N):
        df.loc[n,m.endog+m.value] = m.options.guess_function(df.loc[n,m.state[0]],df.loc[n,m.state[1]])
    df['boundtag'] = boundary_assignment(m.options.n0,m.options.n1)
    # initialize spatial differences
    for i in range(len(m.state)):
        df["_dm{}".format(m.state[i])] = np.reshape(m.grid.dm[i],[m.options.N,1],order='F')
        df["_dp{}".format(m.state[i])] = np.reshape(m.grid.dp[i],[m.options.N,1],order='F')
    df = shift_prices(m,df)
    # don't use drifts (monotonicity scheme) to initialize since it's a circular problem initially if drifts depend on derivatives (also set cross derivative to zero initially)
    df = finite_difference(m,df,target='value',use_drifts=False) # value derivatives
    df = finite_difference(m,df,target='prices',use_drifts=False) # some price derivatives
    df = shift_derivatives(m,df)
    df = calculate_price_derivatives(m,df) # now recalculate the price derivatives better
    for i,eq in enumerate(m.equations):
        for boundtag in df.boundtag.unique():
            args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,eq.name))
            df.loc[df['boundtag']==boundtag,eq.name] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,eq.name,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(a) for a in args])))
    for tup in m.hjb_equations.keys():
        for boundtag in df.boundtag.unique():
            name = "_{0}_{1}".format(tup[0],tup[1])
            args = eval("m.engine.{0}_{1}{2}hjbfcn_args".format(boundtag,tup[0],tup[1]))
            df.loc[df['boundtag']==boundtag,name] = eval("m.engine.{0}_{1}{2}hjbfcn({3})".format(boundtag,tup[0],tup[1],','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
    df['_sidx'] = np.nan # system index 
    return df

def calculate_price_derivatives(m,df):
    """
    Recalculate price derivatives after an iteration of the inner loop
    """
    for var in m.prices:
        for boundtag in list(df.boundtag.unique()):
            for i in range(len(m.state)):
                element = "_{0}{1}".format(var,m.state[i])
                args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,element))
                df.loc[df['boundtag']==boundtag,element] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,element,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
                element = "_{0}{1}{1}".format(var,m.state[i])
                args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,element))
                df.loc[df['boundtag']==boundtag,element] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,element,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
            element = "_{0}{1}{2}".format(var,m.state[0],m.state[1])
            args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,element))
            df.loc[df['boundtag']==boundtag,element] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,element,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
    return df
    
def calculate_secondary(m,df):
    """
    Recalculate secondary variables from new endogenous variable values found in the inner loop
    """
    for i,eq in enumerate(m.equations):
        for boundtag in df.boundtag.unique():
            args = eval("m.engine.{0}_{1}fcn_args".format(boundtag,eq.name))
            df.loc[df['boundtag']==boundtag,eq.name] = eval("m.engine.{0}_{1}fcn({2})".format(boundtag,eq.name,','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
            for sidx in range(len(m.systems)):
                args = eval("m.engine.{0}_system{1}_{2}fcn_args".format(boundtag,sidx,eq.name))
                df.loc[(df['boundtag']==boundtag)&(df['_sidx']==sidx),eq.name] = eval("m.engine.{0}_system{1}_{2}fcn({3})".format(boundtag,sidx,eq.name,','.join(["df.loc[(df['boundtag']==boundtag)&(df['_sidx']==sidx),'{}']".format(var) for var in args])))
    for tup in m.hjb_equations.keys():
        for boundtag in df.boundtag.unique():
            name = "_{0}_{1}".format(tup[0],tup[1])
            args = eval("m.engine.{0}_{1}{2}hjbfcn_args".format(boundtag,tup[0],tup[1]))
            df.loc[df['boundtag']==boundtag,name] = eval("m.engine.{1}_{2}{3}hjbfcn({4})".format(name,boundtag,tup[0],tup[1],','.join(["df.loc[df['boundtag']==boundtag,'{}']".format(var) for var in args])))
            for sidx in range(len(m.systems)):
                args = eval("m.engine.{0}_system{1}_{2}{3}hjbfcn_args".format(boundtag,sidx,tup[0],tup[1]))
                df.loc[(df['boundtag']==boundtag)&(df['_sidx']==sidx),name] = eval("m.engine.{1}_system{0}_{2}{3}hjbfcn({4})".format(sidx,boundtag,tup[0],tup[1],','.join(["df.loc[(df['boundtag']==boundtag)&(df['_sidx']==sidx),'{}']".format(var) for var in args])))
    return df
    
def get_secondary_plot(m):
    secondaryplot = []
    for eq in m.equations:
        if eq.plot:
            secondaryplot.append(eq.name)
    for element in m.options.derivative_plotting:
        secondaryplot.append('_{0}{1}'.format(element[0],''.join(element[1:])))
    return secondaryplot


def plot(m,df,use_dash=True):
    """
    Plot based on plotting options specified in the options class
    """
    firstplot = m.endog+m.value
    firstlatex = m.endog_latex+m.value_latex
    nrow = int(np.floor(np.sqrt(len(firstplot))))
    ncol = int(np.ceil(len(firstplot)/nrow))
    nplots = int(nrow*ncol)
    one_dimension = m.one_dimension
    if one_dimension:
        fig = make_subplots(rows=nrow,cols=ncol,subplot_titles=firstlatex)
    else:
        fig = make_subplots(rows=nrow,cols=ncol,specs=[[{'type':'surface'} for i in range(ncol)] for j in range(nrow)],subplot_titles=firstlatex)
    row = 1
    col = 1
    traces = []
    for i,var in enumerate(firstplot):
        if one_dimension:
            myx = np.linspace(m.options.start0,m.options.end0,m.options.n0)
            myy = np.reshape(df[var].to_numpy(),[m.options.n1,m.options.n0],order='F')[0,:]
            t = go.Scatter(x=myx,y=myy,name=firstlatex[i],mode='lines')
        else:
            t = go.Surface(x=m.grid.x[0],y=m.grid.x[1],z=df[var].to_numpy().reshape([m.options.n1,m.options.n0],order='F'),colorscale='Viridis',name=firstlatex[i])
        traces.append(t)
        fig.add_trace(t,row=row,col=col)
        fig.update_xaxes(title_text=m.state_latex[0], row=row, col=col)
        if not one_dimension:
            fig.update_yaxes(title_text=m.state_latex[1], row=row, col=col)
        else:
            fig.update_yaxes(title_text=var, row=row, col=col)
        if col == ncol:
            col = 1
            row += 1
        else:
            col += 1
    fig.update_layout(height=500*nrow, width=500*ncol, title_text="Endogenous Variables",title_x=0.5,title_font_size=24,showlegend=False)
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=22)
    if not one_dimension:
        fig.update_traces(showscale=False)
    if not use_dash:
        fig.show()
    
    fig2 = {}
    if len(m.secondaryplot)>0:
        nrow = int(np.floor(np.sqrt(len(m.secondaryplot))))
        ncol = int(np.ceil(len(m.secondaryplot)/nrow))
        nplots = int(nrow*ncol)
        if one_dimension:
            fig2 = make_subplots(rows=nrow,cols=ncol,subplot_titles=m.secondarylatex)
        else:
            fig2 = make_subplots(rows=nrow,cols=ncol,specs=[[{'type':'surface'} for i in range(ncol)] for j in range(nrow)],subplot_titles=m.secondarylatex)
        row = 1
        col = 1
        traces2 = []
        for i,var in enumerate(m.secondaryplot):
            if one_dimension:
                myx = np.linspace(m.options.start0,m.options.end0,m.options.n0)
                myy = np.reshape(df[var].to_numpy(),[m.options.n1,m.options.n0],order='F')[0,:]
                t = go.Scatter(x=myx,y=myy,name=m.secondarylatex[i],mode='lines')
            else:
                t = go.Surface(x=m.grid.x[0],y=m.grid.x[1],z=df[var].to_numpy().reshape([m.options.n1,m.options.n0],order='F'),colorscale='Viridis',name=m.secondarylatex[i])
            fig2.add_trace(t,row=row,col=col)
            fig.update_xaxes(title_text=m.state_latex[0], row=row, col=col)
            if not one_dimension:
                fig.update_yaxes(title_text=m.state_latex[1], row=row, col=col)
            else:
                fig.update_yaxes(title_text=var, row=row, col=col)
            if col == ncol:
                col = 1
                row += 1
            else:
                col += 1
        fig2.update_layout(height=500*nrow, width=500*ncol, title_text="Secondary Variables",title_x=0.5,title_font_size=24,showlegend=False)
        for i in fig2['layout']['annotations']:
            i['font'] = dict(size=22)
        if not one_dimension:
            fig2.update_traces(showscale=False)
        if not use_dash:
            fig2.show()
    if use_dash:
        return [fig,fig2]
        
        
def get_secondary_latex(m):   
    """
    Get latex values for secondary plot 
    """
    secondarylatex = []
    for i,x in enumerate(m.secondaryplot):
        found = False
        for eq in m.equations:
            if x==eq.name:
                secondarylatex.append(eq.latex)
                found = True
        if not found:
            for entry in m.secondaryplot:
                if entry==x:
                    first = x[1:-1]
                    if first in m.endog:
                        idx = m.endog.index(first)
                        first = m.endog_latex[idx].replace('$','')
                        first = ' '+first
                        second = x[-1]
                    elif first in m.value:
                        idx = m.value.index(first)
                        first = m.value_latex[idx].replace('$','')
                        first = ' '+first
                        second = x[-1]
                    else:
                        if x in ['_{0}{1}{1}'.format(var,s) for var in m.prices for s in m.state]+['_{0}{1}{2}'.format(var,m.state[0],m.state[1]) for var in m.prices]:
                            first = r'^2 '+x[1]
                            second = x[2]+r' \partial '+x[3]
                        else:
                            pass
                    #mylatex = r'$\frac{\partial'+first+r'}{\partial '+second+r'}$'
                    mylatex = r'$\partial'+first+r'/ \partial '+second+r'$'
                    secondarylatex.append(mylatex)
    return secondarylatex
        
def start_dash(m,stationary_distribution=False):
    """
    Start dash application for live plotting updates
    """
    # create temporary directory for sharing updates (maybe use subprocess later)
    stationary_str = ''
    if stationary_distribution:
        stationary_str = '_stationary'
    if not os.path.isdir('./tmp{0}{1}'.format(m.name,stationary_str)):
        os.mkdir('./tmp{0}{1}'.format(m.name,stationary_str))
    # save down objects needed for the dash application 
    dash_data = dash_init_data(m)
    with open('./tmp{0}{1}/init.pkl'.format(m.name,stationary_str),'wb') as myfile:
        pickle.dump(dash_data,myfile)
    #def open_browser():
    #    webbrowser.open_new("http://localhost:{}".format(m.options.dash_port))
    #Timer(1,open_browser).start()
    #p = mp.Process(target=deploy_dash)
    #p.start()
    
def open_browser(port):
    # open browser to dash port location 
    webbrowser.open_new("http://localhost:{}".format(port))
        
def deploy_dash(m,stationary_distribution=False):
    # user facing function
    Timer(1,_deploy_dash,args=[m,stationary_distribution]).start()
    if stationary_distribution:
        Timer(1,open_browser,args=[m.options.dash_port_stationary]).start()
    else:
        Timer(1,open_browser,args=[m.options.dash_port]).start()
    
def _deploy_dash(m,stationary_distribution):
    # start the dash application (internal function)
    if stationary_distribution:
        retcode = subprocess.call("python dash_utils_stationary.py -n {0} -d {1} -p {2}".format(m.name,m.options.dash_debug,m.options.dash_port_stationary),shell=True)
    else:
        retcode = subprocess.call("python dash_utils.py -n {0} -d {1} -p {2}".format(m.name,m.options.dash_debug,m.options.dash_port),shell=True)
    
class dash_init_data:
    """
    Simple utility class to hold data for dash initialization 
    """
    def __init__(self,m):
        self.endog = m.endog 
        self.options = deepcopy(m.options)
        if self.options.guess_function != False:
            del self.options.guess_function
        self.state = m.state 
        self.secondaryplot = m.secondaryplot
        self.value = m.value
        self.value_latex = m.value_latex 
        self.endog_latex = m.endog_latex 
        self.secondarylatex = m.secondarylatex
        self.name = m.name
        self.state_latex = m.state_latex
        self.one_dimension = m.one_dimension
    
def distance(options):
    """
    Calculate distance from grid boundary
    """
    distance = np.ones(options.N)*options.max_p
    distance = np.reshape(distance,(options.n0,options.n1),order='F')
    for i in range(options.n0):
        for j in range(options.n1):
            if i<options.n0/2 and i<distance[i,j]:
                distance[i,j]=i
            if j<options.n1/2 and j<distance[i,j]:
                distance[i,j]=j
            if i>options.n0/2 and (options.n0-i)<distance[i,j]:
                distance[i,j] = options.n0-i+1
            if j>options.n1/2 and (options.n1-j)<distance[i,j]:
                distance[i,j]=options.n1-j+1
    distance = np.reshape(distance,options.N,order='F')    
    return distance
    
def isdiagdom(a):
    """
    Check if a is a diagonal dominant matrix
    """
    isdom = True
    for r in range(a.shape[0]):
        rowdom = 2*np.abs(a[r,r])>abs(a[r,:]).sum()
        isdom = isdom and rowdom 
    return isdom 
    
def vecfun(a):
    """
    Simple utility function for the stencil decomposition algorithm
    """
    return np.array([[a[0,0]],[np.sqrt(2)*a[0,1]],[a[1,1]]])
    
def pfun(n,p,h):
    """
    Simple utility function for the stencil decomposition algorithm
    """
    # n is normal
    # p is point on plane
    # h is point to project
    # k is projection 
    
    a = n[0]
    b = n[1]
    c = n[2]
    
    d = p[0]
    e = p[1]
    f = p[2]
    
    x = h[0]
    y = h[1]
    z = h[2]
    
    t = (a*d - a*x + b*e - b*y + c*f - c*z)/(a**2+b**2+c**2)
    k = np.array([x+t*a,y+t*b,z+t*c])
    
    return k
    
def decfun(eta,a,xi):
    """
    Simple utility function for the stencil decomposition algorithm
    """
    n = xi.shape[0]
    neta = len(eta)
    eb = np.empty((n,n,neta))
    b = np.empty((n,n,neta))
    for e in range(neta):
        eb[:,:,e] = eta[e] * np.reshape(xi[:,e],[xi.shape[0],1])@np.reshape(xi[:,e],[1,xi.shape[0]])
        b[:,:,e] = np.reshape(xi[:,e],[xi.shape[0],1])@np.reshape(xi[:,e],[1,xi.shape[0]])
    b_ = eb.sum(axis=2)
    f_ = (a-b_).max().max()/np.sqrt(np.power(a[0,0],2)+np.power(a[1,1],2))
    df = np.empty(neta)
    for e in range(neta):
        df[e] = -1*np.multiply((a-b_),b[:,:,e]).sum().sum()
    h_ = np.empty([neta,neta])
    for e1 in range(neta):
        for e2 in range(neta):
            h_[e1,e2] = np.multiply(b[:,:,e1],b[:,:,e2]).sum().sum()
    return [f_,df,h_,b_]
    
def finite_difference(m,df,target='value',use_drifts=True,zero_cross=False):
    """
    Compute value (or select price) derivatives via finite difference using a monotonicity scheme
    """
    dm = {}
    dp = {}
    mu = {}
    if target=='value':
        target = m.value
    elif target=='prices':
        target = m.prices
    for s in range(len(m.state)):
        dm[s] = np.reshape(df['_dm{}'.format(m.state[s])].to_numpy(),[m.options.n1,m.options.n0],order='F')
        dp[s] = np.reshape(df['_dp{}'.format(m.state[s])].to_numpy(),[m.options.n1,m.options.n0],order='F')
        if use_drifts:
            mu[s] = np.reshape(df['_mu_{}'.format(m.state[s])].to_numpy(),[m.options.n1,m.options.n0],order='F')
        else:
            mu[s] = np.zeros((m.options.n1,m.options.n0))
    for i in range(len(target)):
        # first order derivatives
        v = np.reshape(df[target[i]].to_numpy(),[m.options.n1,m.options.n0],order='F')
        diff = finite_difference_utility(m.options.n0,m.options.n1,v,mu,dp,dm)
        df['_{0}{1}'.format(target[i],m.state[0])] = np.reshape(diff[0],m.options.N,order='F')
        df['_{0}{1}'.format(target[i],m.state[1])] = np.reshape(diff[1],m.options.N,order='F')
        # second order derivatives
        v = np.reshape(df['_{0}{1}'.format(target[i],m.state[0])].to_numpy(),[m.options.n1,m.options.n0],order='F')
        diff = finite_difference_utility(m.options.n0,m.options.n1,v,mu,dp,dm)
        df['_{0}{1}{1}'.format(target[i],m.state[0])] = np.reshape(diff[0],m.options.N,order='F')
        df['_{0}{1}{2}a'.format(target[i],m.state[0],m.state[1])] = np.reshape(diff[1],m.options.N,order='F')
        v = np.reshape(df['_{0}{1}'.format(target[i],m.state[1])].to_numpy(),[m.options.n1,m.options.n0],order='F')
        diff = finite_difference_utility(m.options.n0,m.options.n1,v,mu,dp,dm)
        df['_{0}{1}{2}b'.format(target[i],m.state[0],m.state[1])] = np.reshape(diff[0],m.options.N,order='F')
        df['_{0}{1}{1}'.format(target[i],m.state[1])] = np.reshape(diff[1],m.options.N,order='F')
        # cross derivative
        df['_{0}{1}{2}'.format(target[i],m.state[0],m.state[1])] = 0.5*df['_{0}{1}{2}a'.format(target[i],m.state[0],m.state[1])] + 0.5*df['_{0}{1}{2}b'.format(target[i],m.state[0],m.state[1])]
        
    return df

def finite_difference_utility(n0,n1,v,mu,dp,dm):
    """
    Utility function for finite difference function (uses monotonicity scheme)
    """
    diff = {}
    if n0==n1:
        # difference for first state
        diff[0] = np.empty(v.shape)
        diff[0][1:-1,:] = (mu[0][1:-1,:]>=0)*(v[2:,:]-v[1:-1,:])/dp[0][1:-1,:] \
            + (mu[0][1:-1,:]<0)*(v[1:-1,:]-v[0:-2,:])/dm[0][1:-1,:]
        diff[0][0,:] = (v[1,:]-v[0,:])/dp[0][0,:]
        diff[0][-1,:] = (v[-1,:]-v[-2,:])/dm[0][-1,:]
        # difference for second state 
        diff[1] = np.empty(v.shape)
        diff[1][:,1:-1] = (mu[1][:,1:-1]>=0)*(v[:,2:]-v[:,1:-1])/dp[1][:,1:-1] \
            + (mu[1][:,1:-1]<0)*(v[:,1:-1]-v[:,0:-2])/dm[1][:,1:-1]
        diff[1][:,0] = (v[:,1]-v[:,0])/dp[1][:,0]
        diff[1][:,-1] = (v[:,-1]-v[:,-2])/dm[1][:,-1]
    else:
        # difference for first state
        diff[0] = np.empty(v.shape)
        diff[0][:,1:-1] = (mu[0][:,1:-1]>=0)*(v[:,2:]-v[:,1:-1])/dp[0][:,1:-1] \
            + (mu[0][:,1:-1]<0)*(v[:,1:-1]-v[:,0:-2])/dm[0][:,1:-1]
        diff[0][:,0] = (v[:,1]-v[:,0])/dp[0][:,0]
        diff[0][:,-1] = (v[:,-1]-v[:,-2])/dm[0][:,-1]
        # difference for second state 
        diff[1] = np.empty(v.shape)
        diff[1][1:-1,:] = (mu[1][1:-1,:]>=0)*(v[2:,:]-v[1:-1,:])/dp[1][1:-1,:] \
            + (mu[1][1:-1,:]<0)*(v[1:-1,:]-v[0:-2,:])/dm[1][1:-1,:]
        diff[1][0,:] = (v[1,:]-v[0,:])/dp[1][0,:]
        diff[1][-1,:] = (v[-1,:]-v[-2,:])/dm[1][-1,:]
    return diff
    
def scipy_solver_feed(endog,*packed):
    """
    Translates from typical arguments for the engine functions to a function scipy's solver can use
    Accepts boundtag, the engine object, a dictionary translating the order of elements in the endog 
    (what can be changed by the solver) and other (variables treated as constant by the solver)
    """
    # unpack arguments
    other,order,boundtag,engine,sidx = packed
    # provide correct order of arguments to the engine function 
    engine_feed = np.empty(len(endog)+len(other)-np.isnan(order['endog']).sum())
    for i,x in enumerate(list(endog)):
        try:
            engine_feed[int(order['endog'][i])] = x 
        except:
            pass # cannot convert to integer, meaning the entry is a nan, and the endogenous variable is not used
    for i,x in enumerate(list(other)):
        engine_feed[int(order['other'][i])] = x 
    # call the engine function 
    if sidx==None:
        retval =  eval("engine.{0}_Ffcn({1})".format(boundtag,','.join(["engine_feed[{}]".format(i) for i in range(len(engine_feed))])))
    else:
        retval =  eval("engine.{0}_system{1}_Ffcn({2})".format(boundtag,sidx,','.join(["engine_feed[{}]".format(i) for i in range(len(engine_feed))])))
    return np.reshape(retval,len(endog))

def scipy_jacobian_feed(endog,*packed):
    """
    Translates from typical arguments for the engine functions to a function scipy's solver can use
    Accepts boundtag, the engine object, a dictionary translating the order of elements in the endog 
    (what can be changed by the solver) and other (variables treated as constant by the solver)
    """
    # unpack arguments
    other,order,boundtag,engine,sidx = packed
    # provide correct order of arguments to the engine function 
    engine_feed = np.empty(len(endog)+len(other)-np.isnan(order['endog']).sum())
    for i,x in enumerate(list(endog)):
        try:
            engine_feed[int(order['endog'][i])] = x 
        except:
            pass # cannot convert to integer, meaning the entry is a nan, and the endogenous variable is not used
    for i,x in enumerate(list(other)):
        engine_feed[int(order['other'][i])] = x 
    # call the engine function 
    if sidx==None:
        retval =  eval("engine.{0}_jacobian({1})".format(boundtag,','.join(["engine_feed[{}]".format(i) for i in range(len(engine_feed))])))
    else:
        retval =  eval("engine.{0}_system{1}_jacobian({2})".format(boundtag,sidx,','.join(["engine_feed[{}]".format(i) for i in range(len(engine_feed))])))
    return retval

    
def system_ordering(systems):
    """
    Order systems such that more complex (more constraints) are checked first. 
    This way if a set of constraints X is attached to system A and a set of 
    constraints Y is attached to system B such that Y is a subset of X, the 
    constraints X are checked first. Otherwise, system B could be triggered when 
    system A should actually triggered.
    """
    new_systems = []
    max_num_constraints = max([len(s.constraint_trigger) for s in systems])
    for i in range(max_num_constraints):
        j = max_num_constraints-i # j iterates backward from max_num_constraints to 1 
        for s in systems:
            if len(s.constraint_trigger)==j:
                new_systems.append(s)
    return new_systems
    
def triggered(result_,c,endog):
    """
    Determine if a constraint (c) is binding based on the result from scipy.optimize.least_squares (result_)
    """
    idx = endog.index(c.endog_var)
    if c.constraint_type in ['>','>=']:
        binding = result_.active_mask[idx]==-1
    elif c.constraint_type in ['<','<=']:
        binding = result_.active_mask[idx]==1
    return binding 

def transposal(df_,state,value,options):
    """
    Transpose the grid space for inputs to the HJB 2D map (2D map accepts a transposed 
    grid compared to the rest of the code base due to an issue with the port from MatLab.
    This should be fixed in a future release).
    """
    # t is a list of lists... [item for sublist in t for item in sublist]
    inputs = ['distance','_sig_','_dm','_dp','_mu_','_r_','_u_','boundtag','stationary']+value+state
    input_cols = [[col for col in df_.columns if theinput in col] for theinput in inputs]
    input_cols = [item for sublist in input_cols for item in sublist]
    input_cols = list(set(input_cols))
    df = pd.DataFrame(columns=input_cols,index=df_.index)
    for x in list(df.columns):
        old = np.reshape(df_[x].to_numpy(),[options.n1,options.n0],order='F')
        new = np.reshape(old.T,options.N,order='F')
        df[x] = new 
    return df

def reverse_transposal(f,options):
    """
    Reverse the transposal to return an f vector from the HJB 2D map that is compatible with the 
    rest of the code (This should be fixed in a future release by making the grid compatible 
    throughout the code).
    """
    old = np.reshape(f,[options.n1,options.n0],order='F')
    new = np.reshape(old.T,options.N,order='F')
    return new
    
def check_boundary_condition(boundaries,boundtag,endog,row,params,state):
    """
    Check if you are on a boundary with a defined boundary condition and calculate 
    endogenous values based on boundary condition specified
    """
    on_boundary = False
    results = None
    dict_input = {}
    for i,p in enumerate(params.names):
        dict_input[p] = params.values[i]
    for s in state:
        dict_input[s] = row.loc[s]
    for b in boundaries:
        if boundtag in b.boundary:
            on_boundary = True
            results = b.condition(dict_input)
            break
    return on_boundary, results
    
def clean_boundaries(boundaries):
    """
    If there are only edges defined (such as say s=0 for a state s) then let the 
    edges define the corners. However, if there are edges and corners defined, then 
    let the edges not define the corners.
    """
    # define the corners
    corners = ['b0min_b1min','b0max_b1max','b0min_b1max','b0max_b1min']
    # find which corners have dedicated definitions
    dedicated_corners = []
    for corner in corners:
        for b in boundaries:
            if len(b.boundary)==1 and b.boundary[0]==corner:
                dedicated_corners.append(corner)
    # remove the dedicated corners from any edge boundaries that also contain corners
    for b in boundaries:
        if len(b.boundary)>1:
            for corner in dedicated_corners:
                if corner in b.boundary:
                    b.boundary.remove(corner)
    return boundaries
    
def initial_stationary_2d(m):
    """
    Initial distribution to start from for stationary distribution numerical calculation (2D problems)
    """
    midpoint0 = (m.options.end0-m.options.start0)/2 + m.options.start0
    midpoint1 = (m.options.end1-m.options.start1)/2 + m.options.start0
    dist0 = m.options.end0-m.options.start0 
    dist1 = m.options.end1-m.options.start1
    initial = stats.multivariate_normal([midpoint0,midpoint1],[[dist0/7,0],[0,dist1/7]],allow_singular=True)
    return initial
    
def initial_stationary_1d(m,state,scaler=2):
    """
    Initial distribution to start from for stationary distributio numerical calculation (1D problems)
    """
    midpoint0 = (m.options.end0-m.options.start0)/2 + m.options.start0
    dist0 = m.options.end0-m.options.start0 
    initial = stats.norm.pdf(state,loc=midpoint0,scale=dist0/scaler)
    return initial
    
def extract_1d(df,options):
    """
    Extract 1-dimensional data from a 2-dimensional grid 
    """
    df_ = pd.DataFrame(index=range(options.n0),columns=df.columns)
    for var in df.columns:
        df_[var] = np.reshape(df[var].to_numpy(),[options.n0,options.n1],order='F')[:,0]
    return df_
    
def dummy_2d(f,options):
    """
    Re-apply second dummy state variable to 1D problem result vector
    """
    try:
        f = f.to_numpy()
    except:
        pass
    f = np.reshape(np.vstack([np.reshape(f,[1,options.n0]),\
            np.reshape(f,[1,options.n0])]),options.N,order='F')
    return f
    
def remove_boundary_conditions(df,m):
    """
    Remove grid edges associated with boundary conditions for the stationary distribution
    """
    if m.state[-1] == 'o':
        # one dimensional
        if any([any(['b0min' in x for x in b.boundary]) for b in m.boundaries]):
            df = df.loc[~df.boundtag.str.contains('b0min')]
            original_vector = np.linspace(m.options.start0,m.options.end0,m.options.n0)
            m.options.n0 = m.options.n0 - 1
            m.options.start0 = m.options.start0 + original_vector[1]-original_vector[0]
            m.options.N = m.options.n0*m.options.n1
            m.grid.x[0] = m.grid.x[0][:,1:]
            m.grid.x[1] = m.grid.x[1][:,1:]
        if any([any(['b0max' in x for x in b.boundary]) for b in m.boundaries]):
            df = df.loc[~df.boundtag.str.contains('b0max')]
            original_vector = np.linspace(m.options.start0,m.options.end0,m.options.n0)
            m.options.n0 = m.options.n0 - 1
            m.options.end0 = m.options.end0 - original_vector[-1]-original_vector[-2]
            m.options.N = m.options.n0*m.options.n1
            m.grid.x[0] = m.grid.x[0][:,:-1]
            m.grid.x[1] = m.grid.x[1][:,:-1]
    else:
        raise ValueError("Stationary distribution calculation in 2-dimensions with boundary conditions is not supported in this release.")
    df = df.reset_index(drop=True)
    # need to restart dash to provide new grid and options to the saved file
    start_dash(m,stationary_distribution=True)
    return df,m.options,m.grid
        
