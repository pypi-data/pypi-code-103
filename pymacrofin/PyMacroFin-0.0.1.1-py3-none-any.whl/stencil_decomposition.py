import numpy as np
import pandas as pd
import warnings
import PyMacroFin.utilities as util

def stencil_decomposition(sig,distance,options):
    """
    Stencil decomposition function
    """
    maxp_specific = np.min([options.max_p,distance])
    n = sig.shape[0]
    if np.array_equal(np.tril(sig,-1),np.triu(sig,1)):
        warnings.warn("The matrix passed to the stencil decomposition algorithm is not a triangular diffusion matrix")
    neta = int(n + 2*(n**2-n)/2)
    eta = np.empty(neta)
    eta[:] = np.nan
    xi = np.zeros((n,neta))
    i_ = sorted(range(len(np.diag(sig))),reverse=True,key=np.diag(sig).__getitem__)
    ah = sig.copy()
    for i in range(2):
        for j in range(2):
            ah[i,j] = sig[int(i_[i]),int(i_[j])]
    ncorr = 0
    if ah[1,0]<0:
        ah = np.abs(ah)
        ncorr = 1
    
    e = -1
    for i in range(n):
        e += 1
        a_ = ah.copy()
        a_[i,i] = 0
        eta[e] = ah[i,i] - np.abs(a_[i,:]).sum()
        xi[i,e] = 1
    
    for l in range(n):
        for i in range(l):
            e += 1
            eta[e] = ah[i,l]*(ah[i,l]>=0)
            xi[i,e] = 1
            xi[l,e] = 1
    
    for l in range(n):
        for i in range(l):
            e += 1
            eta[e] = -1*ah[i,l]*(ah[i,l]<0)
            xi[i,e] = 1
            xi[l,e] = -1
    
    if (not util.isdiagdom(ah)) and n<=2:
        q = 0
        p = 1
        qp = 1
        pp = 1
        v_ah = util.vecfun(ah)
        
        stop = 0
        while stop == 0:
            xxi = np.array([p,q])
            xxip = np.array([pp,qp])
            x_ = np.reshape(xxi,[2,1])@np.reshape(xxi,[1,2])
            xp = np.reshape(xxip,[2,1])@np.reshape(xxip,[1,2])
            v_x = util.vecfun(x_)
            v_xp = util.vecfun(xp)
            v_n = np.cross(v_x.flatten(),v_xp.flatten())
            v_ap = util.pfun(v_n,np.zeros((3,1)),v_ah.flatten())
            if p+pp>maxp_specific or np.linalg.norm(v_ah-v_ap)<=options.tol_d*np.linalg.norm(v_ah):
                eta = np.linalg.lstsq(np.hstack([v_x,v_xp]),v_ap,rcond=None)[0]
                xi = np.hstack([np.reshape(xxi,[2,1]),np.reshape(xxip,[2,1])])
                stop = 1
            else:
                qpp = q + qp
                ppp = p + pp
                xxipp = np.array([ppp,qpp])
                xpp = np.reshape(xxipp,[2,1])@np.reshape(xxipp,[1,2])
                v_xpp = util.vecfun(xpp)
                eta_ = np.linalg.lstsq(np.hstack([v_x,v_xp,v_xpp]),v_ah.flatten(),rcond=None)[0]
                v_np = np.cross(v_x.flatten(),v_xpp.flatten())
                s = np.sign(np.dot(v_np,np.array([.5,0,.5])))
                if all(eta_>=0):
                    eta = eta_
                    xi = np.vstack([xxi,xxip,xxipp]).T
                    stop = 1
                elif s*np.dot(v_np,v_ah.flatten())<=0:
                    qp = qpp
                    pp = ppp
                else:
                    q = qpp
                    p = ppp
    xi = xi[i_,:]
    if ncorr:
        xi[1,0] = xi[1,0]*-1
        xi[1,1] = xi[1,1]*-1
        if len(eta)==3:
            xi[1,2] = xi[1,2]*-1
    testd,null,null_,b_ = util.decfun(eta,sig,xi)
    if testd>1:
        warnings.warn("high stencil decomposition function error: {}".format(testd))
    return [eta,xi,testd]
    