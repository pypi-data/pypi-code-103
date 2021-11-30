# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 2021

@author: jru
"""

import struct
import numpy as np
from pathlib import Path
from datetime import date

labeldelim='|\u0024'
delim2='|'
textheadlength=20048

def write_data(path,chnames,data,meta=None):
    fname=Path(path).name
    nch=len(chnames)
    npts=len(data)
    f=open(path,'wb')
    offset=0
    header=getFCSHeader(nch,npts)
    f.write(bytes(header,'utf-8'))
    offset=offset+len(header)
    texthead=getTEXTHeader(nch,npts,fname,meta)
    f.write(bytes(texthead,'utf-8'))
    offset=offset+len(texthead)
    ranges=getRanges(data,nch)
    parambuf=getPARAMBuffer(chnames,ranges)
    f.write(bytes(parambuf,'utf-8'))
    offset=offset+len(parambuf)
    for i in range(offset,textheadlength):
        f.write((32).to_bytes(1,'little'))
    f.write(np.asfarray(data.flatten(),dtype='float32').tobytes())
    f.close()
    return
    
def getRanges(data,nch):
    ranges=data.max(axis=0).astype(int)
    ranges+=1
    return ranges
    
def getFCSHeader(nch,npts):
    header='FCS3.0    '
    header=header+padInteger(58)+padInteger(textheadlength-1)+padInteger(textheadlength)
    totpts=nch*npts*4
    header=header+padInteger(textheadlength+totpts-1)+padInteger(0)+padInteger(0)
    return header
    
def getTEXTHeader(nch,npts,filename,meta=None):
    texthead=labeldelim+"TOT"+delim2+str(npts)
    texthead=texthead+labeldelim+"PAR"+delim2+str(nch)
    texthead=texthead+labeldelim+"BYTEORD"+delim2+"1,2,3,4"
    texthead=texthead+labeldelim+"DATATYPE"+delim2+"F"
    texthead=texthead+labeldelim+"MODE"+delim2+"L"
    texthead=texthead+labeldelim+"BEGINDATA"+delim2+str(textheadlength)
    dataend=nch*npts*8+textheadlength
    texthead=texthead+labeldelim+"ENDDATA"+delim2+str(dataend)
    texthead=texthead+labeldelim+"BEGINANALYSIS"+delim2+"0"
    texthead=texthead+labeldelim+"ENDANALYSIS"+delim2+"0"
    texthead=texthead+labeldelim+"BEGINSTEXT"+delim2+"58"
    texthead=texthead+labeldelim+"ENDSTEXT"+delim2+"20048"
    texthead=texthead+labeldelim+"COM"+delim2+"Jay Unruh Plugins"
    texthead=texthead+labeldelim+"FIL"+delim2+filename
    texthead=texthead+labeldelim+"NEXTDATA"+delim2+"0"
    texthead=texthead+labeldelim+"DATE"+delim2+date.today().strftime("%m-%d-%Y")
    texthead=texthead+labeldelim+"CYT"+delim2+"ImageJ_Table"
    if(meta is not None):
        for i in range(len(meta)):
            texthead=texthead+labeldelim+meta[0][i]+delim2+meta[1][i]
    return texthead
    
def getPARAMBuffer(labels,ranges):
    parambuf=''
    for i in range(len(labels)):
        parambuf=parambuf+labeldelim+"P"+str(i+1)+"S"+delim2+labels[i]
        parambuf=parambuf+labeldelim+"P"+str(i+1)+"N"+delim2+labels[i]
        parambuf=parambuf+labeldelim+"P"+str(i+1)+"E"+delim2+"0,0"
        parambuf=parambuf+labeldelim+"P"+str(i+1)+"G"+delim2+"1"
        parambuf=parambuf+labeldelim+"P"+str(i+1)+"R"+delim2+str(ranges[i])
        parambuf=parambuf+labeldelim+"P"+str(i+1)+"B"+delim2+"32"
    return parambuf
    
def padInteger(val,nchar=8):
    zeros=''.join(['0']*nchar)
    temp=zeros+str(val)
    return temp[-nchar:]