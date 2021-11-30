# -*- coding: utf-8 -*-
"""
Created on Tue Sept 14 2021

@author: jru
"""

from numba import jit
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.colors as col
from matplotlib.patches import Path
from matplotlib.patches import PathPatch
from matplotlib.patches import Polygon
import napari
#%gui qt

def getNiceColormap(whiteback):
    r=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]
    g=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,251,247,243,239,235,231,227,223,219,215,211,207,203,199,195,191,187,183,179,175,171,167,163,159,155,151,147,143,139,135,131,127,123,119,115,111,107,103,99,95,91,87,83,79,75,71,67,63,59,55,51,47,43,39,35,31,27,23,19,15,11,7,3,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,255]
    b=[0,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,251,247,243,239,235,231,227,223,219,215,211,207,203,199,195,191,187,183,179,175,171,167,163,159,155,151,147,143,139,135,131,127,123,119,115,111,107,103,99,95,91,87,83,79,75,71,67,63,59,55,51,47,43,39,35,31,27,23,19,15,11,7,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,255]
    if(whiteback):
        r[0]=255
        r[255]=255
        g[0]=255
        g[255]=120
        b[0]=255
        b[255]=120
    tcolors=[]
    for i in range(256):
        tcolors.append([r[i]/256.0,g[i]/256.0,b[i]/256.0])
    return col.ListedColormap(tcolors)

def get2DHistBins(binSize,limits,logs,logxmin=1.0,logymin=1.0):
    #need to generate the histogram bins
    histSize=256
    newhistsize=int(histSize/binSize)
    xMin=limits[0]
    xMax=limits[1]
    yMin=limits[2]
    yMax=limits[3]
    logx=logs[0]
    logy=logs[1]
    #not sure if this is the right kind of 2D array
    histbins=[]
    tempxbins=[]
    tempybins=[]
    if not logx and not logy:
        tbinsizex=(binSize/float(histSize))*(xMax-xMin)
        tbinsizey=(binSize/float(histSize))*(yMax-yMin)
        for i in range(0,newhistsize):
            tempxbins.append(xMin+tbinsizex*float(i))
        for i in range(0,newhistsize):
            tempybins.append(yMin+tbinsizey*float(i))
    else:
        #find the x bin edges
        if logx:
            if xMin>0.0:
                logxmin=math.log(xMin)
            #else: 
            #    xMin=findmingt0(xValues,xMax)
            #    logxmin=math.log(xMin)
            logxmax=math.log(xMax)
            tbinsizex=(binSize/float(histSize))*(logxmax-logxmin)
            for i in range(0,newhistsize):
                val=math.exp(logxmin+tbinsizex*float(i))
                tempxbins.append(val)
        else:
            tbinsizex=(binSize/float(histSize))*(xMax-xMin)
            for i in range(0,newhistsize):
                tempxbins.append(xMin+tbinsizex*float(i))
        #find the y bin edges
        if logy:
            if yMin>0.0:
                logymin=math.log(yMin)
            #else: 
            #    yMin=findmingt0(yValues,yMax)
            #    logymin=math.log(yMin)
            logymax=math.log(yMax)
            tbinsizey=(binSize/float(histSize))*(logymax-logymin)
            for i in range(0,newhistsize):
                val=math.exp(logymin+tbinsizey*float(i))
                tempybins.append(val)
        else:
            tbinsizey=(binSize/float(histSize))*(yMax-yMin)
            for i in range(0,newhistsize):
                tempybins.append(yMin+tbinsizey*float(i))
    #combine them
    histbins.append(tempxbins)
    histbins.append(tempybins)
    return histbins
    
def drawHist(df,xcol,ycol,limits,logs,binSize=4,figsize=(4,4),multiplier=1.0):
    fig=Figure(figsize=figsize,dpi=300)
    #canvas=FigureCanvasAgg(fig)
    histbins=get2DHistBins(binSize,limits,logs)
    counts,_,_=np.histogram2d(df[xcol],df[ycol],histbins)
    cmap=getNiceColormap(True)
    marg=0.15
    width=1.0-2.0*marg
    height=1.0-2.0*marg
    #ax=fig.gca()
    ax=fig.add_axes([marg,marg,width,height])
    maxcounts=counts.max().max()
    ax.pcolormesh(histbins[0],histbins[1],counts.T,cmap=cmap,vmin=0.0,vmax=maxcounts/multiplier)
    ax.set_xlabel(xcol)
    ax.set_ylabel(ycol,labelpad=-5)
    ax.axis([limits[0],limits[1],limits[2],limits[3]])
    if logs[0]: ax.set_xscale('log')
    if logs[1]: ax.set_yscale('log')
    #ax.margins(x=0.05,y=0.05,tight=True)
    #plt.subplots_adjust(left=marg,right=(1.0-marg),top=(1.0-marg),bottom=marg)
    #ax.yaxis.label_pad=-10
    canvas=FigureCanvasAgg(fig)
    canvas.draw()
    figimg=np.asarray(canvas.buffer_rgba())
    return fig,figimg
    
def addNapariHist(df,xcol,ycol,limits,logs,viewer=None,binSize=4,multiplier=1.0):
    fig,figimg=drawHist(df,xcol,ycol,limits,logs,binSize,multiplier=multiplier)
    figname=ycol+' vs '+xcol
    if(viewer is None):
        viewer=napari.Viewer()
        viewer.theme='light'
    viewer.add_image(figimg,blending='opaque',interpolation='bilinear',name=figname)
    return fig,figimg,viewer
    
def overlayImageGate(figimg,gate):
    fig=Figure(dpi=300)
    ax=fig.gca()
    ax.axis('off')
    ax.imshow(figimg)
    #swap the gate axes and add the closing line
    #gate2=np.array([list(gate[1,:])+[gate[1,0]],list(gate[0,:])+[gate[0,0]]]).T
    gate2=gate.copy()
    gate2[:,0]=gate[:,1]
    gate2[:,1]=gate[:,0]
    #patch=PathPatch(Path(gate2),facecolor=None,fill=False,lw=2)
    patch=Polygon(gate2,fill=False,edgecolor='black')
    ax.add_patch(patch)
    canvas=FigureCanvasAgg(fig)
    canvas.draw()
    return fig,np.asarray(canvas.buffer_rgba())
    
def drawHistGate(df,xcol,ycol,limits,logs,gate,binSize=4,multiplier=1.0):
    fig,figimg=drawHist(df,xcol,ycol,limits,logs,binSize,multiplier=muliplier)
    return overlayImageGate(figimg,gate)

def getPlotCoords(xpts,ypts,limits,logs,margins=[180,180],psizes=[840,840]):
    """
    This gets the plot image coordinates.
    Default margins and plot sizes are for 4 x 4 plot with 15% margins at 300 dpi.
    """
    if(not logs[0]):
        xcoords=(xpts-limits[0])*psizes[0]/(limits[1]-limits[0])
    else:
        logxmin=np.log(limits[0])
        logxmax=np.log(limits[1])
        logxpts=np.log(xpts)
        xcoords=(logxpts-logxmin)*psizes[0]/(logxmax-logxmin)
        xcoords[xpts<=0.0]=-1.0
    xcoords+=float(margins[0])
    if(not logs[1]):
        ycoords=(ypts-limits[2])*psizes[1]/(limits[3]-limits[2])
    else:
        logymin=np.log(limits[2])
        logymax=np.log(limits[3])
        logypts=np.log(ypts)
        ycoords=(logypts-logymin)*psizes[1]/(logymax-logymin)
        ycoords[ypts<=0.0]=-1.0
    ycoords+=float(margins[1])
    return xcoords,ycoords

def plotGateContains(xpts,ypts,gatecoords,limits,logs,margins=[180,180],psizes=[840,840]):
    """
    This function takes a set of data points and gate coordinates and plot size details and returns a boolean list if points are in the gate.
    Default margins and plot sizes are for 4 x 4 plot with 15% margins at 300 dpi.
    Gate coordinates are organized as ordered in Napari.
    """
    #start by converting x and y pts into plot coordinates
    xcoords,ycoords=getPlotCoords(xpts,ypts,limits,logs,margins,psizes)
    #now test to see if the transformed coordinates are in the gate and in the plot margins
    ymax=psizes[1]+margins[1]+margins[1]
    inmargins=(xcoords>=margins[0]) & (xcoords<(psizes[0]+margins[0])) & (ycoords>=margins[1]) & (ycoords<(psizes[1]+margins[1]))
    ingate=[polyContains(gatecoords,np.array([xcoords[i],ymax-ycoords[i]])) if(inmargins[i]) else False for i in range(len(xcoords))]
    return ingate,xcoords,ycoords

#copy of the contains code from ImageJ FloatPolygon: https://imagej.nih.gov/ij/developer/source/ij/process/FloatPolygon.java.html
@jit(nopython=True)
def polyContains(polygon,point):
    inside=False
    y=point[1]
    x=point[0]
    for i in range(polygon.shape[0]):
        if(i>0): j=i-1
        else: j=polygon.shape[0]-1
        if(((polygon[i,0]>=y)!=(polygon[j,0]>=y)) and (x>(polygon[j,1]-polygon[i,1])*(y-polygon[i,0])/(polygon[j,0]-polygon[i,0])+polygon[i,1])):
            inside=(not inside)
    return inside