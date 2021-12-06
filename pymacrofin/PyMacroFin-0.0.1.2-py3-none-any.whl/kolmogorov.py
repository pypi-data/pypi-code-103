import numpy as np
import pandas as pd
from PyMacroFin.outerloop import hjb1d_map, hjb2d_map
from PyMacroFin.parameters import options
from scipy.linalg import null_space
import matplotlib.pyplot as plt
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import PyMacroFin.utilities as util


pd.options.mode.chained_assignment = None
plt.rcParams.update({'font.size': 16})

def stationary_distribution_model(m,df,plot=True,t=[],init=[],return_mesh=False):
    """
    Estimate stationary distribution given a PyMacroFin model object and solution DataFrame.
    This function uses the basis of the adjoint of the Kolmogorov Forward / Fokker-Planck operator
    as described in Chapter 3 of Markus Brunnermeier and Yuily Sannikov's ECON 529 Notes (see 
    `here <https://scholar.princeton.edu/markus/classes/eco529-financial-and-monetary-economics>`_).
    
    Parameters
    -------------
    m: PyMacroFin.model.macro_model 
        Model object to which the solution belongs
    df: pd.core.frame.DataFrame
        DataFrame returned by :code:`df = m.run()` with the option :code:`m.options.return_solution = True`.
    t: iterable
        Vector of times.
    init: pd.core.series.Series
        Vector the same size first dimension as :code:`df` being the initial distribution (starting point) for 
        iterating forward in time if :code:`t` is nonempty.
    return_mesh: bool
        Whether or not to return a mesh object for use with the :code:`stationary_plot_2d` function. If generating 
        the :code:`pdfs` return object, returning the mesh is useful to plot the distribution from any given time 
        point. If the problem is one-dimensional, this argument has no effect.
    
    Returns
    -----------
    pdf: np.array
        Estimated stationary distribution
    pdfs: np.array
        This object is only returned when :code:`t` is nonempty. If the problem is one-dimensional, this returns
        a two-dimensional array with the second dimension corresponding to the entries in :code:`t`. Hence, :code:`pdfs`
        will contain the distribution vector for each time in :code:`t`.
        
    Notes
    --------------
    
    1. If the function fails, you may try running wtih a :code:`t` vector to see how the distribution evolves from an initial known distribution. It may be the case that your stationary distribution is degenerate.
    2. Note that this function will fail in most instances if the volatility at grid boundaries is nonzero and if drifts point toward outside the grid at or near boundaries. 
    """
    # add a necessary starter column 
    df['stationary'] = 0.5
    # get the matrix from outerloop
    if m.one_dimension:
        f,a = hjb1d_map(m,df,0,var_type='stationary',stationary_distribution=True,method='monotone')
    else:
        f,a = hjb2d_map(m,df,0,var_type='stationary',stationary_distribution=True)
    null = null_space(a.T)
    if null.shape[1]==0:
        try: 
            a[0,:] = 0.0
            a[0,0] = 1
            null = null_space(a.T)
            assert null.shape[1] > 0, "failure"
        except:
            raise ValueError("The Fokker-Planck operator has no nontrivial solutions to the homogenous system")
    null = null[:,0]
    if m.one_dimension:
        cdf = null.cumsum()/null.sum()
        state = df[m.state[0]].to_numpy()
        dp = df['_dp{}'.format(m.state[0])].to_numpy()
        pdf = np.concatenate([np.array([0]),(cdf[1:]-cdf[:-1])/dp[:-1]])
    else:
        null = np.reshape(null,[m.options.n0,m.options.n1],order='F')
        cdf = null.cumsum(axis=0).cumsum(axis=1)/null.sum(axis=1).sum(axis=0)
        pdf = (null[2:,2:] - null[2:,1:-1] - null[1:-1,2:] + 2*null[1:-1,1:-1] - null[:-2,1:-1] - null[1:-1,:-2] \
                + null[:-2,:-2])/(m.grid.dm[0][1:-1,1:-1]*m.grid.dm[1][1:-1,1:-1]+m.grid.dp[0][1:-1,1:-1]*m.grid.dp[1][1:-1,1:-1])
    if plot:
        if m.one_dimension:
            stationary_plot_1d(pdf,state,m.state[0])
        else:
            mesh = (m.grid.x[0],m.grid.x[1],m.state[0],m.state[1])
            stationary_plot_2d(pdf,(mesh[0][1:-1,1:-1],mesh[1][1:-1,1:-1],mesh[2],mesh[3]))
    if len(t)>0 and len(init)>0:
        pdfs = forward_iteration(m,a,t,init)
        if return_mesh and (not m.one_dimension):
            retval = (pdf,pdfs,mesh)
        else:
            retval = (pdf,pdfs)
    else:
        if return_mesh and (not m.one_dimension):
            retval = (pdf,mesh)
        else:
            retval = pdf
    return retval 
    
def stationary_distribution(state,mu,sig,plot=True,t=[],init=[],return_mesh=False):
    """
    Estimate stationary distribution given a state grid with drift and volatility.
    This function uses the basis of the adjoint of the Kolmogorov Forward / Fokker-Planck operator
    as described in Chapter 3 of Markus Brunnermeier and Yuily Sannikov's ECON 529 Notes (see 
    `here <https://scholar.princeton.edu/markus/classes/eco529-financial-and-monetary-economics>`_).
    
    Parameters
    ------------
    state: pd.core.series.Series or pd.core.frame.DataFrame
        Vector or matrix of state variable values. If the problem is one-dimensional, :code:`state` 
        should be a named series with the name being the name of the state variable. If the problem 
        is two-dimensional, :code:`state` should be a DataFrame with two columns, named for the two state
        variables. The DataFrame should contain a row for each combination of values to be used in the 
        discretization of the state space.
    mu: pd.core.series.Series of pd.core.frame.DataFrame
        Vector or matrix of drifts corresponding to the brownian motion of the state variable(s)  
        at the discrete points of :code:`state`. If the problem is one-dimensional, this should be a 
        single vector (series). If the problem is two-dimensional, this should be a DataFrame with columns
        names matching the column names in :code:`state`. The column corresponding to a state variable 
        should contain the drifts in that state variable direction. There should not be drifts leading 
        outside the grid (i.e. :code:`mu.iloc[0]>=0` and :code:`mu.iloc[-1]<=0` in the 1D case).
    sig: pd.core.series.Series of pd.core.frame.DataFrame
        Vector or matrix of volatilities corresponding to the brownian motion of state variable(s) 
        at the discrete points of :code:`state`. If the problem is one-dimensional, this should be a 
        single vector (series). If the problem is two-dimensional, this should be a DataFrame with columns
        names matching the column names in :code:`state`, as well as a column named :code:`'cross'`. The column 
        corresponding to a state variable should contain the volatility (standard deviation) of that state 
        variable direction, and the :code:`'cross'` column should contain the cross volatility term (again in 
        standard deviation form). The first and last volatilities should be zero in the grid (i.e. 
        :code:`sig.iloc[0]=0` and `sig.iloc[-1]=0` in the 1D case).
    plot: bool
        Whether or not to plot the distribution. Defaults to :code:`True`
    return_mesh: bool
        Whether or not to return a mesh object for use with the :code:`stationary_plot_2d` function. If generating 
        the :code:`pdfs` return object, returning the mesh is useful to plot the distribution from any given time 
        point. If the problem is one-dimensional, this argument has no effect.
    
    Returns
    ---------
    pdf: pd.core.frame.DataFrame
        Estimated stationary distribution
        
    Notes
    -----------
    
    1. There should be no NaN or inf in the input vectors / matrices. NaNs or infs will cause undesired behavior.
    2. If the function fails, you may try running wtih a :code:`t` vector to see how the distribution evolves from an initial known distribution. It may be the case that your stationary distribution is degenerate.
    3. Note that this function will fail in most instances if the volatility at grid boundaries is nonzero and if drifts point toward outside the grid at or near boundaries. 
    """
    assertions(state,mu,sig,plot)
    # create mini model object to pass into hjb map functions
    m = mini_model(state)
    if m.one_dimension:
        # convert from pandas to numpy if necessary 
        mu,state,sig = to_numpy(mu,state,sig)
    # construct the dataframe input
    dm,dp,df,mesh = construct_df(m,mu,state,sig)
    # get the matrix from outerloop
    if m.one_dimension:
        f,a = hjb1d_map(m,df,0,var_type='stationary',stationary_distribution=True,method='monotone')
    else:
        f,a = hjb2d_map(m,df,0,var_type='stationary',stationary_distribution=True)
    null = null_space(a.T)
    if null.shape[1]==0:
        try: 
            a[0,:] = 0.0
            a[0,0] = 1
            null = null_space(a.T)
            assert null.shape[1] > 0, "failure"
        except:
            raise ValueError("The Fokker-Planck operator has no nontrivial solutions to the homogenous system")
    null = null[:,0]
    if m.one_dimension:
        cdf = null.cumsum()/null.sum()
        pdf = np.concatenate([np.array([0]),(cdf[1:]-cdf[:-1])/dp[:-1]])
    else:
        null = np.reshape(null,[m.options.n0,m.options.n1],order='F')
        cdf = null.cumsum(axis=0).cumsum(axis=1)/null.sum(axis=1).sum(axis=0)
        pdf = (null[2:,2:] - null[2:,1:-1] - null[1:-1,2:] + 2*null[1:-1,1:-1] - null[:-2,1:-1] - null[1:-1,:-2] \
                + null[:-2,:-2])/(dm[0][1:-1,1:-1]*dm[1][1:-1,1:-1]+dp[0][1:-1,1:-1]*dp[1][1:-1,1:-1])
    if plot:
        if m.one_dimension:
            stationary_plot_1d(pdf,state,m.state[0])
        else:
            stationary_plot_2d(pdf,(mesh[0][1:-1,1:-1],mesh[1][1:-1,1:-1],mesh[2],mesh[3]))
    if len(t)>0 and len(init)>0:
        pdfs = forward_iteration(m,a,t,init)
        if return_mesh and (not m.one_dimension):
            retval = (pdf,pdfs,mesh)
        else:
            retval = (pdf,pdfs)
    else:
        if return_mesh and (not m.one_dimension):
            retval = (pdf,mesh)
        else:
            retval = pdf
    return retval 
        
def forward_iteration(m,a,t,init):
    """
    Iterate forward through a time vector from an initial distribution 
    """
    t = np.array(t)
    dt = t[1:]-t[:-1]
    dt = np.append([t[0]-0],dt)
    if m.one_dimension:
        pdfs = np.empty((a.shape[0],len(t)))
        f = init
    else:
        pdfs = np.empty((m.options.n0,m.options.n1,len(t)))
        init = np.array(init)
        if len(init.shape)==1:
            f = init
        elif len(init.shape)==2:
            f = np.reshape(init,m.options.N,order='F')
        else:
            raise ValueError("invalid shape of init argument")
    for idx,t_ in enumerate(list(t)):
        operator = (np.eye(a.shape[0],a.shape[0]) - dt[idx]*a.T)
        if m.one_dimension:
            f = np.linalg.inv(operator) @ f
            pdfs[:,idx] = f
        else:
            f = np.linalg.inv(operator) @ f
            pdfs[:,:,idx] = np.reshape(f,[m.options.n0,m.options.n1],order='F')
    return pdfs
    
def assertions(state,mu,sig,plot):
    """
    Run some error checking 
    """
    assert isinstance(plot,bool), "invalid input for plot argument"
    if isinstance(state,pd.core.frame.DataFrame):
        assert isinstance(mu,pd.core.frame.DataFrame), "invalid type for mu argument"
        assert isinstance(sig,pd.core.frame.DataFrame), "invalid type for sig argument"
        assert 'cross' in sig.columns, "'cross' must be a column in sig"
        for x in state.columns:
            assert x in sig.columns, "state variables must have columns in sig"
            assert x in mu.columns, "state variables must have columns in mu"
    else:
        assert isinstance(state,pd.core.series.Series), "invalid type for state argument"
        assert isinstance(mu,pd.core.series.Series), "invalid type for state argument"
        assert isinstance(sig,pd.core.series.Series), "invalid type for state argument"
    assert mu.shape[0]==sig.shape[0], "first dimension size must match between mu and sig"
    assert mu.shape[0]==state.shape[0], "first dimension size must match between state and mu"
    
    
def stationary_plot_1d(pdf,state,name,save=False):
    """
    Plot the stationary distribution for a one-dimensional problem 
    
    Parameters
    ------------
    pdf: np.array 
        The distribution vector to be plotted
    state: np.array
        The state variable vector corresponding to the values in :code:`pdf`
    name: str
        The name of the state variable.
    save: False or str
        If :code:`False` then the plot is not saved. If a string, then 
        the string passed must be a valid path to which to save the file.
        
    Returns
    ----------
    Null. The distribution is plotted (and saved if specified).
    """
    plt.figure(1,figsize=(10,10))
    plt.plot(state[1:],pdf[1:])
    plt.ylabel('stationary density')
    plt.xlabel(name)
    plt.savefig("stationary_density-{}.png".format(time.strftime("%Y%m%d-%H%M%S")))
    if save != False:
        plt.savefig(save)
    plt.show()
    
def stationary_plot_2d(pdf,mesh,save=False,engine='mpl',view=(30,-60)):
    """
    Plot the stationary distribution for a two-dimensional problem 
    
    Parameters
    ------------
    pdf: np.array 
        The two-dimensional distribution grid to be plotted.
    mesh: tuple
        This argument must be a tuple with four entries. The first two 
        entries must be the two-dimensional mesh corresponding to the 
        state-space of the distribution. For example, if the distribution is 
        over a 50x50 grid of variables x and y, where x and y are both length 
        50 vectors, then running :code:`xx, yy = numpy.meshgrid(x,y)` will 
        produce the first two entries of mesh. The second two entries of mesh 
        are the names of the two state variables.
    save: False or str
        If :code:`False` then the plot is not saved. If a string, then 
        the string passed must be a valid path to which to save the file.
    engine: str
        Whether to use :code:`matplotlib` (:code:`engine='mpl'`) or :code:`plotly`
        (:code:`engine='plotly'`). Defaults to :code:`'mpl'`. 
    angle: numeric
        Tuple of elevation and azimuth angles from which to view the plot. This 
        argument is only used for the :code:`'mpl'` engine.
        
    Returns
    ----------
    Null. The distribution is plotted (and saved if specified).
    """
    if engine=='plotly':
        fig = make_subplots(rows=1,cols=1,specs=[[{'type':'surface'}]])
        traces = []
        t = go.Surface(x=mesh[0],y=mesh[1],z=pdf,colorscale='Viridis',name='stationary')
        traces.append(t)
        fig.add_trace(t,row=1,col=1)
        fig.update_xaxes(title_text=mesh[2], row=1, col=1)
        fig.update_yaxes(title_text=mesh[3], row=1, col=1)
        fig.update_layout(height=1000*1, width=1000*1, title_text="Stationary Density",title_x=0.5,title_font_size=24)
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=22)
        fig.update_traces(showscale=False)
        if save != False:
            fig.write_image(save)
        fig.show()
    elif engine=='mpl':
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(mesh[0], mesh[1], pdf)
        ax.set_xlabel(mesh[2])
        ax.set_ylabel(mesh[3])
        ax.set_zlabel('stationary density')
        if view != (30,-60):
            ax.view_init(view[0],view[1])
        plt.tight_layout()
        if save != False:
            plt.savefig(save)
        plt.show()    
    else:
        raise ValueError("invalid input for engine argument")
    
class mini_model:
    """
    Simple utility mini-model for necessary inputs to the hjb map functions that 
    construct the fokker-planck / kolmogorov forward operator matrices
    """
    def __init__(self,state):
        if len(state.shape)==1:
            self.one_dimension=True
            self.init_1d(state)
        elif len(state.shape)==2:
            self.one_dimension=False
            self.init_2d(state)
        else:
            raise ValueError("Invalid state variable grid. Number of dimensions must be one or two.")
        
    def init_1d(self,state):
        if state.name == None:
            self.state = ['x']
        else:
            self.state = [state.name]
        self.options = options()
        self.options.n0 = state.shape[0]
        self.options.N = state.shape[0]*2
        self.value = []
        
    def init_2d(self,state):
        self.state = list(state.columns)
        self.options = options()
        self.options.n0 = int(state[self.state[0]].nunique())
        self.options.n1 = int(state.shape[0]/self.options.n0)
        self.options.N = int(state.shape[0])
        self.value = []
        
def construct_df(m,mu,state,sig):
    """
    Utility function to create the dataframe input to hjb map functions
    """
    if m.one_dimension:
        # get the dx vector
        dp = state[1:]-state[:-1]
        dp = np.append(dp,dp[-1])
        dm = state[1:]-state[:-1]
        dm = np.append(dm[0],dm)
        # construct the dataframe input required
        df = pd.DataFrame(columns=['_mu_{}'.format(m.state[0]),'_sig_{}'.format(m.state[0]),m.state[0]])
        df['_mu_{}'.format(m.state[0])] = mu 
        df['_sig_{}'.format(m.state[0])] = sig 
        df[m.state[0]] = state
        df['_dm{}'.format(m.state[0])] = dm
        df['_dp{}'.format(m.state[0])] = dp
        mesh = '_'
    else:
        mu['_mu_{}'.format(m.state[0])] = mu[m.state[0]]
        mu['_mu_{}'.format(m.state[1])] = mu[m.state[1]]
        mu = mu[['_mu_{}'.format(m.state[0]),'_mu_{}'.format(m.state[1])]]
        sig['_sig_{}'.format(m.state[0])] = sig[m.state[0]]
        sig['_sig_{}'.format(m.state[1])] = sig[m.state[1]]
        sig['_sig_cross'] = sig['cross']
        sig = sig[['_sig_{}'.format(m.state[0]),'_sig_{}'.format(m.state[1]),'_sig_cross']]
        df = pd.concat([mu,sig,state],axis=1)
        df = df.sort_values(by=[m.state[0],m.state[1]])
        v0 = pd.Series(state[m.state[0]].unique()).sort_values().to_numpy()
        v1 = pd.Series(state[m.state[1]].unique()).sort_values().to_numpy()
        xx,yy = np.meshgrid(v0,v1)
        mesh = (xx,yy,m.state[0],m.state[1])
        dp0 = v0[1:]-v0[:-1]
        dp0 = np.append(dp0,dp0[-1])
        dm0 = v0[1:]-v0[:-1]
        dm0 = np.append(dm0[0],dm0)
        dp1 = v1[1:]-v1[:-1]
        dp1 = np.append(dp1,dp1[-1])
        dm1 = v1[1:]-v1[:-1]
        dm1 = np.append(dm1[0],dm1)
        dm = {}
        dp = {}
        dm[0], dm[1] = np.meshgrid(dm0,dm1)
        dp[0], dp[1] = np.meshgrid(dp0,dp1)
        for i in range(2):
            df['_dp{}'.format(m.state[i])] = np.reshape(dm[i],[m.options.N,1],order='F')
            df['_dm{}'.format(m.state[i])] = np.reshape(dp[i],[m.options.N,1],order='F')
            #dp[i] = df['_dp{}'.format(m.state[i])]
            #dm[i] = df['_dm{}'.format(m.state[i])]
    
    df['_r_stationary'] = 0
    df['_u_stationary'] = 0
    df['stationary'] = 1

    return dm,dp,df,mesh

        
def to_numpy(mu,state,sig):
    """
    Simple utility function to convert from pandas series to numpy array 
    if not already converted
    """
    try:
        mu = mu.to_numpy()
    except:
        pass
    try: 
        state = state.to_numpy()
    except:
        pass
    try: 
        sig = sig.to_numpy()
    except:
        pass
    return mu,state,sig