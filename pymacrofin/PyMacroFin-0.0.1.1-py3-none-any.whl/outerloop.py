import numpy as np
import pandas as pd
import scipy 
import PyMacroFin.utilities as util
from PyMacroFin.innerloop import innerloop
from PyMacroFin.stencil_decomposition import stencil_decomposition
import scipy.sparse as sparse
import scipy.sparse.linalg as sparse_linalg
import warnings
from dask.distributed import Client
import cloudpickle
import os
from copy import deepcopy
import findiff

def outerloop(m,df):
    """
    Function for the outer loop
    """
    # initialize an error
    hjb_loop_error = 10
    # initialize active dampening factors
    m.options._active_damp1 = m.options.damp1
    m.options._active_damp2 = m.options.damp2
    # start a dask client if running the inner loop in parallel
    if m.options.parallel:
        client = Client(processes=False)
    # save down model for inner static loop to pull
    cloudpickle.dump(m,open('modeltmp_{}.pkl'.format(m.name),'wb'))
    # start outer hjb loop
    for i_hjb in range(m.options.max_hjb):
        if not m.options.quiet and i_hjb==0 and m.options.ignore_HJB_loop == False:
            print("HJB loop {0} iteration {1} with dt = {2}".format(m.options._loop,i_hjb+1,m.options.dt))
        # run the inner loop
        if m.options.suppress_warnings:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                df = innerloop(m,df)
        else:
            df = innerloop(m,df)
        
        # if ignoring the HJB loop, break here and return
        if m.options.ignore_HJB_loop:
            break
        
        # apply hjb loop dampening
        if m.options._loop == 1:
            m.options._active_damp1 = m.options._active_damp1*m.options.damp1_adjustment
            m.options._active_damp1 = np.max([m.options._active_damp1,m.options.min_damp1])
        elif m.options._loop == 2:
            m.options._active_damp2 = m.options._active_damp2*m.options.damp2_adjustment
            m.options._active_damp2 = np.max([m.options._active_damp2,m.options.min_damp2])
        
        # run HJB map for each value
        for i in range(len(m.value)):
            df['_{}_old'.format(m.value[i])] = df[m.value[i]].copy()
            if m.one_dimension:
                df[m.value[i]] = hjb1d_map(m,df,i)
            else:
                df[m.value[i]] = hjb2d_map(m,df,i)
            # warn if values are unusually high or low
            if any(df[m.value[i]]>m.options.value_upper) or any(df[m.value[i]]<m.options.value_lower):
                warnings.warn("Value {0} has an unusual value: {1}".format(m.value[i],np.abs(df[m.value[i]]).max()))
        # run finite difference (pull the differences from HJB map as an option, but also maintain current 
        #                        implemementation as an option)
        df = util.finite_difference(m,df)
        # compute error
        hjb_loop_error = (np.abs((df[m.value[0]]-df['_{}_old'.format(m.value[0])])/df['_{}_old'.format(m.value[0])])).max()  
        if not m.options.quiet:
            print("HJB loop {0} iteration {1} completed with error {2:.3g} and dt = {3}".format(m.options._loop,i_hjb+1,hjb_loop_error,m.options.dt))
        # swap loop stage if appropriate
        if m.options.loop:
            if m.options._loop == 1:
                if hjb_loop_error<m.options.tol_hjb and i_hjb>m.options.min_hjb1:
                    m._loop = 2
                    hjb_loop_error = 1
        
        if m.options.outer_plot:
            if m.use_dash:
                df[m.secondaryplot+m.endog+m.value].to_csv('./tmp{}/dash_data.csv'.format(m.name),index=False)
            else:
                util.plot(m,df)
                    
        # break if break conditions met
        if m.options._loop == 1:
            if i_hjb>m.options.min_hjb1 and hjb_loop_error<m.options.tol_hjb:
                break
        elif m.options._loop == 2:
            if i_hjb>m.options.min_hjb2 and hjb_loop_error<m.options.tol_hjb:
                break
    # close dask client
    if m.options.parallel:
        client.close()
    # remove temporary file
    try:
        os.remove('modeltmp_{}.pkl'.format(m.name))
    except:
        warnings.warn("Unable to clean up serialized temporary model file")
    return df
            
        
def hjb2d_map(m,df_,_idx_,var_type='value',stationary_distribution=False):
    """
    HJB 2D map function
    
    Accepts model object, dataframe with model data, 
    an index (_idx_) and var_type that together point to 
    the variable to apply the map to. If :code:`'stationary'` is
    selected then the stationary distribution is calculated
    """
    df = util.transposal(df_,m.state,m.value,m.options)
    if var_type == 'value':
        var = m.value[_idx_]
    elif var_type == 'stationary':
        var = 'stationary'
    else:
        raise ValueError("Invalid input for var_type. Must be either 'value' or 'state'")
    # determine active time difference 
    if m.options._loop == 1:
        active_dt = m.options.dt 
    elif m.options._loop == 2:
        active_dt = m.options.dt2
    # calculate distance for each point from the boundary
    df['distance'] = util.distance(m.options)    
    # create dictionaries
    eta = {}
    sig = {}
    seta = np.empty(m.options.N)
    xi = {}
    testd = {}
    for ik in range(m.options.N):
        sig[ik] = np.empty((len(m.state),len(m.state)))
        for i in range(len(m.state)):
            for j in range(len(m.state)):
                if i == j:
                    sig[ik][i,j] = df.loc[ik,"_sig_{}".format(m.state[i])]
                else:
                    sig[ik][i,j] = df.loc[ik,"_sig_cross"]
    mdim = np.array([1,m.options.n0])
    if len(m.state)>1:
        for ik in range(m.options.N):
            eta[ik],xi[ik],testd[ik] = stencil_decomposition(sig[ik],df.loc[ik,'distance'],m.options)
            for ix in range(len(eta[ik])):
                xdim = mdim @ xi[ik]
                try:
                    xdim = xdim[:,ix].sum()
                except:
                    xdim = xdim[ix].sum()
                if ik+1-xdim<1 or ik+1-xdim>m.options.N:
                    eta[ik][:] = 0
                if ik+1+xdim<1 or ik+1+xdim>m.options.N:
                    eta[ik][:] = 0
            seta[ik] = eta[ik].sum()
    else:
        for ik in range(m.options.N):
            eta[ik] = sig[ik]
            xi[ik] = 1
            seta[ik] = sig[ik]
    dk = np.empty((2,m.options.N))
    uk = np.empty((2,m.options.N))
    df['zero'] = 0
    for i in range(len(m.state)):
        if stationary_distribution:
            dk[i,:] = -1.0*df[['_mu_{0}'.format(m.state[i]),'zero']].min(axis=1)/df['_dm{0}'.format(m.state[i])]
            uk[i,:] = df[['_mu_{0}'.format(m.state[i]),'zero']].max(axis=1)/df['_dp{0}'.format(m.state[i])]
        else:
            dk[i,:] = df[['_mu_{0}'.format(m.state[i]),'zero']].min(axis=1)/df['_dm{0}'.format(m.state[i])]
            uk[i,:] = -1.0*df[['_mu_{0}'.format(m.state[i]),'zero']].max(axis=1)/df['_dp{0}'.format(m.state[i])]
    dk = np.reshape(dk,[len(m.state),m.options.n0,m.options.n1],order='F')
    uk = np.reshape(uk,[len(m.state),m.options.n0,m.options.n1],order='F')
    # warn about drifts directing mass out of the grid 
    drifts_out = []
    if m.options.warn_drift_out:
        if any(dk[0,0,:]!=0):
            drifts_out.append(np.abs(dk[0,0,:]).max())
            #warnings.warn("There are drifts of state {0} in a negative direction out of the grid. Maximum absolute value: {1}".format(m.value[0],np.abs(dk[0,0,:]).max()))
        if any(dk[1,:,0]!=0):
            drifts_out.append(np.abs(dk[1,:,0]).max())
            #warnings.warn("There are drifts of state {0} in a negative direction out of the grid. Maximum absolute value: {1}".format(m.value[1],np.abs(dk[1,:,0]).max()))
        if any(uk[0,-1,:]!=0):
            drifts_out.append(np.abs(uk[0,-1,:]).max())
            #warnings.warn("There are drifts of state {0} in a positive direction out of the grid. Maximum absolute value: {1}".format(m.value[0],np.abs(uk[0,-1,:]).max()))
        if any(uk[1,:,-1]!=0):
            drifts_out.append(np.abs(uk[1,:,-1]).max())
            #warnings.warn("There are drifts of state {0} in a positive direction out of the grid. Maximum absolute value: {1}".format(m.value[1],np.abs(uk[1,:,-1]).max()))
    if len(drifts_out)>0:   
        if max(drifts_out)>0:
            warnings.warn("There are drifts directing out of the grid. Maximum absolute value: {}".format(max(drifts_out)))
    # ensure there are not drifts directing mass out of the grid 
    dk[0,0,:] = 0
    dk[1,:,0] = 0
    uk[0,-1,:] = 0
    uk[1,:,-1] = 0
    dk = np.reshape(dk,[len(m.state),m.options.N],order='F')
    uk = np.reshape(uk,[len(m.state),m.options.N],order='F')
    if stationary_distribution:
        mk = -1.0*dk.sum(axis=0) - uk.sum(axis=0) - 2*seta
    else:
        mk = df['_r_{0}'.format(var)] + 1/active_dt - dk.sum(axis=0) - uk.sum(axis=0) + 2*seta
    a = np.zeros((m.options.N,m.options.N))
    for ik in range(m.options.N):
        ik_check = ik + 1
        a[ik,ik] = a[ik,ik] + mk[ik]
        for i_d in range(len(m.state)):
            flag1 = 0
            flag2 = 0 
            if i_d == 0:
                if ik_check % mdim[1] == 0:
                    flag1 = 1
                if (ik_check-1) % mdim[1] == 0:
                    flag2 = 1
            if ik_check-mdim[i_d]>=1 and flag2 == 0:
                a[ik,ik-mdim[i_d]] = a[ik,ik-mdim[i_d]]+dk[i_d,ik]
            if ik_check+mdim[i_d]<=m.options.N and flag1 == 0:
                a[ik,ik+mdim[i_d]] = a[ik,ik+mdim[i_d]]+uk[i_d,ik]
        for ix in range(len(eta[ik])):
            xdim =  mdim @ xi[ik]
            try:
                xdim = xdim[:,ix].sum()
            except:
                xdim = xdim[ix].sum()
            xdim = int(xdim)
            flag1 = 0
            flag2 = 0
            if xdim == 1:
                if ik_check % mdim[1] == 0:
                    flag1 = 1
                if (ik_check-1) % mdim[1] == 0:
                    flag2 = 1
            x1 = np.ceil(ik_check/mdim[1])+1
            y1 = ik_check % mdim[1]
            if y1 == 0:
                y1 = mdim[1]
            x2 = np.ceil(np.max([ik_check-xdim,0])/mdim[1])+1
            y2 = np.max([0,ik_check-xdim]) % mdim[1]
            if y2 == 0:
                y2 = mdim[1]
            x3 = np.ceil((ik_check+xdim)/mdim[1])+1
            y3 = (ik_check+xdim) % mdim[1]
            if y3 == 0:
                y3 = mdim[1]
            dist2 = np.power(np.power(x2-x1,2)+np.power(y2-y1,2),0.5)
            dist3 = np.power(np.power(x3-x1,2)+np.power(y3-y1,2),0.5)
            if dist2>mdim[1]/2:
                flag2 = 1
            if dist3>mdim[1]/2:
                flag1 = 1
            if ik_check-xdim>=1 and ik_check-xdim<=m.options.N and flag2==0:
                if stationary_distribution:
                    a[ik,ik-xdim] = a[ik,ik-xdim]+eta[ik][ix]
                else:
                    a[ik,ik-xdim] = a[ik,ik-xdim]-eta[ik][ix]
            if ik_check+xdim>=1 and ik_check+xdim<=m.options.N and flag1==0:
                if stationary_distribution:
                    a[ik,ik+xdim] = a[ik,ik+xdim]+eta[ik][ix]
                else:
                    a[ik,ik+xdim] = a[ik,ik+xdim]-eta[ik][ix]
    #a = sparse.csr_matrix(a)
    #f = sparse_linalg.inv(a).toarray() @ (df["_u_{}".format(var)].to_numpy() + 1.0/active_dt*
    #    df["{}".format(m.value[_idx_])].to_numpy())
    if stationary_distribution:
        # forward in time 
        f_ = a @ (df[var].to_numpy()*active_dt)
        for i in range(len(f_)):
            if f_[i]<0:
                f_[i]=0
                
    else:
        # backward in time 
        f_ = np.linalg.inv(a) @ (df["_u_{}".format(var)].to_numpy() + 1.0/active_dt*df[var].to_numpy())
    f = util.reverse_transposal(f_,m.options)
    if stationary_distribution:
        retval = (f,a)
    else:
        retval = f
    return retval
    

def hjb1d_map(m,df_,_idx_,var_type='value',method='monotone',stationary_distribution=False):
    """
    Legacy HJB 1D map function
    
    Accepts model object, dataframe with model data, 
    an index (_idx_) and var_type that together point to 
    the variable to apply the map to. If :code:`'state'` is
    selected then the stationary distribution is calculated
    
    Ignores the second state variable in the model
    """
    if stationary_distribution:
        # ensure correct method 
        assert method in ['monotone'], "invalid method for stationary distribution in this release"
    mu = '_mu_{}'.format(m.state[0])
    sig = '_sig_{}'.format(m.state[0])
    dm = '_dm{}'.format(m.state[0])
    dp = '_dp{}'.format(m.state[0])
    if not stationary_distribution:
        df = util.transposal(deepcopy(df_),m.state,m.value,m.options)
        df = util.extract_1d(df,m.options)
    else:
        df = deepcopy(df_)
    df['zero'] = 0
    if var_type == 'value':
        var = m.value[_idx_]
    elif var_type == 'stationary':
        var = 'stationary'
    else:
        raise ValueError("Invalid input for var_type. Must be either 'value' or 'stationary'")
    r = '_r_{}'.format(var)
    # determine active time difference 
    if m.options._loop == 1:
        active_dt = m.options.dt 
    elif m.options._loop == 2:
        active_dt = m.options.dt2
    a = np.zeros((m.options.n0,m.options.n0))
    mu_plus = df[[mu,'zero']].max(axis=1)
    mu_minus = df[[mu,'zero']].min(axis=1)
    if method=='monotone':
        mksig = np.power(df[sig]/df[dm],2)
        if stationary_distribution:
            uk = mu_plus/df[dp]
            dk = -1.0*mu_minus/df[dm]
            mk = -1.0*uk - dk
            uk = uk + np.power(df[sig],2)/((df[dp] + df[dm])*df[dp])
            dk = dk + np.power(df[sig],2)/((df[dp] + df[dm])*df[dm])
            mk = mk - np.power(df[sig],2)/((df[dp] + df[dm])*df[dm]) - np.power(df[sig],2)/((df[dp] + df[dm])*df[dp])
        else:
            mk = df[r] + 1/active_dt + (mu_plus-mu_minus)/df[dm] + mksig 
            uk = -1.0*df[[mu,'zero']].max(axis=1)/df[dp] - np.power(df[sig]/df[dp],2)/2
            dk = df[[mu,'zero']].min(axis=1)/df[dm] - np.power(df[sig]/df[dm],2)/2
        d2k = df['zero']
        u2k = df['zero']
    elif method=='backward':
        mksig = -1.*np.power(df[sig]/df[dm],2)/2
        mk = df[r] + 1/active_dt - df[mu]/df[dm] + mksig + df[r]
        uk = df['zero']
        u2k = df['zero']
        dk = df[mu]/df[dm] + np.power(df[sig]/df[dm],2)
        d2k = -1.*np.power(df[sig]/df[dm],2)/2
    elif method=='forward':
        mksig = -1.*np.power(df[sig]/df[dm],2)/2
        mk = df[r] + 1/active_dt + df[mu]/df[dm] + mksig + df[r]
        dk = df['zero']
        d2k = df['zero']
        uk = -1.*df[mu]/df[dm] + np.power(df[sig]/df[dm],2)
        u2k = -1.*np.power(df[sig]/df[dm],2)/2
    elif method=='central':
        mksig = np.power(df[sig]/df[dm],2)
        mk = df[r] + 1/active_dt + mksig + df[r]
        u2k = df['zero']
        d2k = df['zero']
        uk = -1.*df[mu]/(2*df[dm]) - np.power(df[sig]/df[dp],2)/2
        dk = df[mu]/(2*df[dm]) - np.power(df[sig]/df[dm],2)/2
    elif method=='proper-high-order-central':
        # requires an equispaced grid
        # still need to check all this algebra again
        mksig = df['zero'].copy()
        mk = df['zero'].copy()
        uk = df['zero'].copy()
        u2k = df['zero'].copy()
        dk = df['zero'].copy()
        d2k = df['zero'].copy()
        for idx in range(m.options.n0):
            if idx == 0:  
                # simple forward for first derivative 
                # second order forward for second derivative  
                mk.loc[idx] = df.loc[idx,mu]/df.loc[idx,dp] + 1/active_dt + df.loc[idx,r]
                mksig.loc[idx] = -1.*np.power(df.loc[idx,sig]/df.loc[idx,dp],2)/2
                dk.loc[idx] = 0
                d2k.loc[idx] = 0
                uk.loc[idx] = -1.*df.loc[idx,mu]/df.loc[idx,dp] + np.power(df.loc[idx,sig]/df.loc[idx,dp],2)
                u2k.loc[idx] = -1.*np.power(df.loc[idx,sig]/df.loc[idx,dp],2)/2
            elif idx==1:
                # simple central for first derivative
                # second order central for second derivative
                mk.loc[idx] = 1/active_dt + df.loc[idx,r]
                mksig.loc[idx] = np.power(df.loc[idx,sig]/df.loc[idx,dp],2)
                dk.loc[idx] = df.loc[idx,mu]/df.loc[idx,dm] - np.power(df.loc[idx,sig]/df.loc[idx,dm],2)/2
                d2k.loc[idx] = 0
                uk.loc[idx] = -1.*df.loc[idx,mu]/df.loc[idx,dp] - np.power(df.loc[idx,sig]/df.loc[idx,dp],2)/2
                u2k.loc[idx] = 0
            elif idx>0 and idx<m.options.n0-2:
                # fourth order central for both first and second derivatives 
                mk.loc[idx] = 1/active_dt + df.loc[idx,r]
                mksig.loc[idx] = 15.*np.power(df.loc[idx,sig]/df.loc[idx,dp],2)
                dk.loc[idx] = (8.*df.loc[idx,mu])/(12.*df.loc[idx,dm]) - 16/12*np.power(df.loc[idx,sig]/df.loc[idx,dm],2)
                d2k.loc[idx] = df.loc[idx,mu]/(12.*df.loc[idx,dm]) + 1/12*np.power(df.loc[idx,sig]/df.loc[idx,dm],2)
                uk.loc[idx] = (-8.*df.loc[idx,mu])/(12.*df.loc[idx,dp]) - 16/12*np.power(df.loc[idx,sig]/df.loc[idx,dp],2)
                u2k.loc[idx] = df.loc[idx,mu]/(12.*df.loc[idx,dm]) + 1/12*np.power(df.loc[idx,sig]/df.loc[idx,dm],2)
            elif idx==m.options.n0-2:
                # simple central  for first derivative 
                # second order central for second derivative 
                # second order central for second derivative
                mk.loc[idx] = 1/active_dt + df.loc[idx,r]
                mksig.loc[idx] = np.power(df.loc[idx,sig]/df.loc[idx,dm],2)
                dk.loc[idx] = df.loc[idx,mu]/df.loc[idx,dm] - np.power(df.loc[idx,sig]/df.loc[idx,dm],2)/2
                d2k.loc[idx] = 0
                uk.loc[idx] = -1.*df.loc[idx,mu]/df.loc[idx,dm] - np.power(df.loc[idx,sig]/df.loc[idx,dm],2)/2
                u2k.loc[idx] = 0
            elif idx==m.options.n0-1:
                # simple backward for first derivative 
                # second order backward for second derivative
                mk.loc[idx] = -1.*df.loc[idx,mu]/df.loc[idx,dp] + 1/active_dt + df.loc[idx,r]
                mksig.loc[idx] = -1.*np.power(df.loc[idx,sig]/df.loc[idx,dp],2)/2
                dk.loc[idx] = df.loc[idx,mu]/df.loc[idx,dp] + np.power(df.loc[idx,sig]/df.loc[idx,dp],2)
                d2k.loc[idx] = -1.*np.power(df.loc[idx,sig]/df.loc[idx,dp],2)/2
                uk.loc[idx] = 0
                u2k.loc[idx] = 0
    for idx in range(m.options.n0):
        # boundary methods for volatility leaving the grid (important for iterating forward 
        # with kolmogorov forward equations) left in case they might be useful in the future, 
        # but the code should not run for now
        boundary_method = None
        a[idx,idx] = a[idx,idx] + mk.loc[idx]
        if idx-1>=0:
            a[idx,idx-1] = a[idx,idx-1] + dk.loc[idx]
        else:
            if boundary_method == 'shadow':
                # add dk from shadow point to the left 
                a[idx,idx] = a[idx,idx] + dk.loc[idx]
            elif boundary_method == 'interior':
                # only volatility goint into the interior from the boundary point 
                a[idx,idx] = a[idx,idx] - mksig.loc[idx]/2
        if idx-2>=0:
            a[idx,idx-2] = a[idx,idx-2] + d2k.loc[idx]
        else:
            if boundary_method == 'shadow':
                # shadow point two points to the left
                a[idx,idx] = a[idx,idx] + d2k.loc[idx] 
        if idx+1<=m.options.n0-1:
            a[idx,idx+1] = a[idx,idx+1] + uk.loc[idx]
        else:
            if boundary_method == 'shadow':
                # shadow point to the right
                a[idx,idx] = a[idx,idx] + uk.loc[idx]
            elif boundary_method == 'interior':
                # only volatility goint into the interior from the boundary point 
                a[idx,idx] = a[idx,idx] - mksig.loc[idx]/2
        if idx+2<=m.options.n0-1:
            a[idx,idx+2] = a[idx,idx+2] + u2k.loc[idx]
        else:
            if boundary_method == 'shadow':
                # shadow point two points to the right 
                a[idx,idx] = a[idx,idx] + u2k.loc[idx]
    if stationary_distribution:
        # forward in time 
        f = a @ (df[var].to_numpy()*active_dt)
        for i in range(len(f)):
            if f[i]<0:
                f[i]=0
    else:
        # backward in time 
        f_ = np.linalg.inv(a) @ (df["_u_{}".format(var)].to_numpy() + 1.0/active_dt*df[var].to_numpy())
        f = util.dummy_2d(f_,m.options)
    if stationary_distribution:
        retval = (f,a)
    else:
        retval = f
    return retval


# legacy function that uses higher order finite difference methods. Was used to iterate the kolmogorov 
# forward equations through time, but was numerically unstable. Currently unused, but could be useful 
# at some point in the future
def hjb1d_map_stationary(m,df_,method='central',accuracy=8):
    """
    requires an equispaced grid currently
    """
    assert m.options.n0 > accuracy*2+5, "Insufficient number of grid points for the desired accuracy in the 1-dimensional finite difference scheme"
    mu = '_mu_{}'.format(m.state[0])
    sig = '_sig_{}'.format(m.state[0])
    dm = '_dm{}'.format(m.state[0])
    dp = '_dp{}'.format(m.state[0])
    df = util.transposal(deepcopy(df_),m.state,m.value,m.options)
    df = util.extract_1d(df,m.options)
    df['zero'] = 0
    var = 'stationary'
    r = '_r_{}'.format(var)
    # determine active time difference 
    if m.options._loop == 1:
        active_dt = m.options.dt 
    elif m.options._loop == 2:
        active_dt = m.options.dt2
    a = np.zeros((m.options.n0,m.options.n0))
    for n in range(m.options.n0):
        if method == 'central':
            if n < accuracy/2:
                #coeff1 = findiff.coefficients(deriv=1, offsets=[x-n for x in range(0,accuracy)])
                #coeff2 = findiff.coefficients(deriv=2, offsets=[x-n for x in range(0,accuracy+1)])
                coeff1 = findiff.coefficients(deriv=1, acc=accuracy)['forward']
                coeff2 = findiff.coefficients(deriv=2, acc=accuracy)['forward']
            elif n > m.options.n0 - 1 - accuracy/2:
                # the way we want it to work, but the package doesn't appear to do it correctly
                #coeff1 = findiff.coefficients(deriv=1, offsets=[(m.options.n0-n-1)-x for x in range(accuracy-1,-1,-1)])
                #coeff2 = findiff.coefficients(deriv=1, offsets=[(m.options.n0-n-1)-x for x in range(accuracy,-1,-1)])
                # my way of reversing the correct method at the start of the grid for the end of the grid 
                #coeff1 = {}
                #coeff1['coefficients'] = -1.*np.array(list(reversed(findiff.coefficients(deriv=1, offsets=[x-(m.options.n0-1-n) for x in range(0,accuracy)])['coefficients'])))
                #coeff1['offsets'] = [(m.options.n0-n-1)-x for x in range(accuracy-1,-1,-1)]
                #coeff2 = {}
                #coeff2['coefficients'] = np.array(list(reversed(findiff.coefficients(deriv=2, offsets=[x-(m.options.n0-1-n) for x in range(0,accuracy+1)])['coefficients'])))
                #coeff2['offsets'] = [(m.options.n0-n-1)-x for x in range(accuracy,-1,-1)]
                # a way I prefer not to do it that does not properly create relationships between the points at the end of the grid
                coeff1 = findiff.coefficients(deriv=1, acc=accuracy)['backward']
                coeff2 = findiff.coefficients(deriv=2, acc=accuracy)['backward']
            else:
                coeff1 = findiff.coefficients(deriv=1, acc=accuracy)['center']
                coeff2 = findiff.coefficients(deriv=2, acc=accuracy)['center']
        elif method == 'forward':
            if n > m.options.n0 - 2 - accuracy:
                coeff1 = findiff.coefficients(deriv=1, offsets=[(m.options.n0-n-1)-x for x in range(accuracy,-1,-1)])
                coeff2 = findiff.coefficients(deriv=1, offsets=[(m.options.n0-n-1)-x for x in range(accuracy,-1,-1)])
            else:
                coeff1 = findiff.coefficients(deriv=1, acc=accuracy)['forward']
                coeff2 = findiff.coefficients(deriv=2, acc=accuracy)['forward']
        elif method == 'backward':
            if n < accuracy:
                coeff1 = findiff.coefficients(deriv=1, offsets=[x-n for x in range(0,accuracy+1)])
                coeff2 = findiff.coefficients(deriv=2, offsets=[x-n for x in range(0,accuracy+2)])
            else:
                coeff1 = findiff.coefficients(deriv=1, acc=accuracy)['backward']
                coeff2 = findiff.coefficients(deriv=2, acc=accuracy)['backward']
        for i in range(len(coeff1['offsets'])):
            j = coeff1['offsets'][i]
            a[n,n+j] = a[n,n+j] + coeff1['coefficients'][i]*df.loc[n+j,mu]/df.loc[n,dm]
        for i in range(len(coeff2['offsets'])):
            j = coeff2['offsets'][i]
            a[n,n+j] = a[n,n+j] + coeff2['coefficients'][i]*np.power(df.loc[n+j,sig]/df.loc[n,dm],2)/2
        a[n,n] = a[n,n] + 1/active_dt
    f_ = a @ (df[var].to_numpy()*active_dt)
    for i in range(len(f_)):
        if f_[i]<0:
            f_[i]=0
    f = util.dummy_2d(f_,m.options)
    return f
