# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 2021

@author: jru
"""

import importflowcyte as ifc
import exportflowcyte as efc
import pandas as pd
import numpy as np

def getFileAsDF(chnames,data,meta):
    """
    converts fcs file data into a dataframe and metadata dictionary
    """
    df=pd.DataFrame(data.T)
    df.columns=chnames
    metadict=dict(zip(meta[0],meta[1]))
    return df,metadict
    
def getFileAsDF2(fpath):
    """
    converts fcs file data into a dataframe and metadata dictionary
    """
    chnames,data,meta=ifc.getFCSFile(fpath)
    df=pd.DataFrame(data.T)
    df.columns=chnames
    metadict=dict(zip(meta[0],meta[1]))
    return df,metadict
    
def saveDF(fpath,df,metadict):
    """
    saves a dataframe and metadata dictionary as an fcs file
    """
    chnames=df.columns
    data=df.values.T
    if(metadict is not None):
        meta=[list(metadict.keys()),list(metadict.values())]
    else:
        meta=None
    efc.write_data(fpath,chnames,data,meta)

def getCompensated(fpath):
    """
    reads an fcs file from fpath and returns a compensated dataframe and metadata dictionary
    """
    #start by getting the data and metadata
    chnames,data,meta=ifc.getFCSFile(fpath)
    #now get the dataframe and metadata dictionary
    df,metadict=getFileAsDF(chnames,data,meta)
    spillstr=metadict['SPILLOVER']
    spilldf=getSpillMat(spillstr)
    compsubset=df[spilldf.columns]
    compdf=compensateColumns(compsubset,spilldf)
    df[spilldf.columns]=compdf
    return df,metadict
    
def compensateColumns(colsdf,spilldf):
    """
    compensates selected columns by multiplying by spillover matrix inverse
    """
    spillinv=np.linalg.inv(spilldf)
    comparr=np.apply_along_axis(lambda a:np.matmul(a,spillinv),1,colsdf.values)
    compdf=pd.DataFrame(comparr)
    compdf.columns=spilldf.columns
    return compdf

def getSpillMat(spillstr):
    """
    takes the spillover string from metadata and parses it into the appropriate matrix (as dataframe)
    """
    tsplit=spillstr.split(',')
    nch=int(tsplit[0])
    print(nch)
    chnames=tsplit[1:nch+1]
    linear=tsplit[nch+1:]
    linear=np.array([float(linear[i]) for i in range(len(linear))])
    mat=linear.reshape((nch,nch))
    matdf=pd.DataFrame(mat)
    matdf.columns=chnames
    return matdf