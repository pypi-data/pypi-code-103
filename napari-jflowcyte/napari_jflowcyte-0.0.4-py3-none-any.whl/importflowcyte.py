# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 13:42:36 2020

@author: jru
"""

import numpy as npy
import struct
import math
import array
import sys

def getFCSFile(path):
    #this loads and parses a .FCS file and returns column name, column array, and metadata
    f=open(path,"rb")
    try:
        label=readstring(f,6)
        print(label)
        readbytearray(f,4)
        toff=readstring(f,8)
        textoff=parseNumber(toff.strip())
        teoff=readstring(f,8)
        texteoff=parseNumber(teoff.strip())
        doff=readstring(f,8)
        dataoff=parseNumber(doff.strip())
        deoff=readstring(f,8)
        dataeoff=parseNumber(deoff.strip())
        aoff=readstring(f,8)
        analoff=parseNumber(aoff.strip())
        aeoff=readstring(f,8)
        analeoff=parseNumber(aeoff.strip())
        print([textoff,texteoff,dataoff,dataeoff,analoff,analeoff])
        f.close()
        f=open(path,"rb")
        readbytearray(f,textoff)
        textlength=texteoff-textoff
        text=readstring(f,textlength)
        readbytearray(f,1)
        text=text.replace('\\','/')
        text=text.replace('|','/')
        text=text.replace('\u000C','/')
        text=text.replace('\u001E','/')
        text=text.replace('*','/')
        #params=text.split('/\\u0024') #this is the $ character
        params=text.split('/$')
        #print(params)
        templen=len(params)-1
        labels=[]
        values=[]
        flags=[False]*templen
        numextra=0
        for i in range(1,len(params)):
            temp=params[i].split('/')
            labels.append(temp[0])
            values.append(temp[1])
            #if temp is longer than 2 values, need to add those values
            if(len(temp)>2):
                flags[i-1]=True
                numextra+=(len(temp)-2)/2
        
        #tack on the extra values if they exist
        if(numextra>0):
            counter=len(flags)
            for i in range(len(flags)):
                if(flags[i]):
                    temp=params[i+1].split('/')
                    temp1=int((len(temp)-2)/2)
                    for j in range(temp1):
                        labels.append(temp[2*j+2])
                        values.append(temp[2*j+3])
                        counter+=1
        
        meta=[labels,values]
        #now get the number of data points and number of channels
        npts=get_label_number(labels,values,'TOT')                        
        nch=get_label_number(labels,values,'PAR')
        byteord=get_label_value(labels,values,'BYTEORD')
        motorola=True
        if(byteord.startswith('1,')): motorola=False
        dtype=get_label_value(labels,values,'DATATYPE')
        isints=dtype.startswith('I')
        chnames=[]
        chbits=[]
        ranges=[]
        for i in range(nch):
            tempname='P'+str(i+1)+'N'
            chnames.append(get_label_value(labels,values,tempname))
            if(chnames[i]==None): chnames[i]=tempname
            tempname='P'+str(i+1)+'B'
            chbits.append(get_label_number(labels,values,tempname))
            if(chbits[i]<0): chbits[i]=32
            tempname='P'+str(i+1)+'R'
            ranges.append(get_label_number(labels,values,tempname))
            
        f.close()
        if(npts<=0): return [chnames,None,meta]
        temp=npy.zeros((npts,nch))
        f=open(path,"rb")
        readbytearray(f,dataoff)
        #now we need to read the data
        #check if all bit depths are the same
        if(allElementsSame(chbits)):
            bigarray=readArray(f,chbits[0],isints,motorola,nch*npts)
            columns=npy.reshape(bigarray,(npts,nch))
            columns=columns.T
        else:
            columns=npy.zeros((nch,npts))
            for i in range(npts):
                for j in range(nch):
                    temp=readArray(f,chbits[j],isints,motorola,1)
                    columns[j,i]=temp[0]
    finally:
        f.close()
    return chnames,columns,meta

def readArray(f,bits,isints,motorola,tlen):
    if(bits==16):
        if(not motorola): 
            bigarray=readintelshort(f,tlen)
        else: 
            bigarray=readmotorolashort(f,tlen)
    else:
        if(bits==32):
            if(isints):
                if(not motorola): 
                    bigarray=readintelint(f,tlen)
                else: 
                    bigarray=readmotorolaint(f,tlen)
            else:
                if(not motorola): 
                    bigarray=readintelfloat(f,tlen)
                else: 
                    bigarray=readmotorolafloat(f,tlen)
        else:
            if(bits==8):
                bigarray=readbytearray(f,tlen)
    return bigarray
        
def allElementsSame(mylist):
    first=mylist[0]
    for item in mylist:
        if(item!=first): return False
    return True

def readstring(f,tlen):
    barr=readbytearray(f,tlen)
    return str(barr.tobytes(),'utf-8')

def readbytearray(f,tlen):
    a=array.array('b')
    a.fromfile(f,tlen)
    return a

def readintelfloat(f,tlen):
    return npy.fromfile(f, dtype='<f',count=tlen)

def readmotorolafloat(f,tlen):
    return npy.fromfile(f, dtype='>f',count=tlen)

def readintelshort(f,tlen):
    return npy.fromfile(f, dtype='<h',count=tlen)

def readmotorolashort(f,tlen):
    return npy.fromfile(f, dtype='>h',count=tlen)

def readintelint(f,tlen):
    return npy.fromfile(f, dtype='<i',count=tlen)

def readmotorolaint(f,tlen):
    return npy.fromfile(f, dtype='>i',count=tlen)

def parseNumber(strval):
    return int(strval)

def get_label_value(labels,values,match):
    try:
        pos=labels.index(match)
    except:
        return None
    if(pos>=0): return values[pos]
    else: return None

def get_label_number(labels,values,match):
    val=get_label_value(labels,values,match)
    if(val!=None):
        return int(val.strip())
    return -1

if __name__ == "__main__":
    fname=sys.argv[1]
    chnames,fcsdata,meta=getFCSFile(fname)
    fcsdata=npy.array(fcsdata).T
    myhead=chnames[0]
    for i in range(1,len(chnames)):
        myhead+=','+chnames[i]
    npy.savetxt(sys.argv[2],fcsdata,delimiter=',',header=myhead)