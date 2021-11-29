# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 21:16:04 2021

@author: HEDI
"""



__CEND__='\x1b[0m'

class __color__:
    def __init__(self):
        for i,c in enumerate(["BLACK","RED","GREEN","RED2","BLUE","PURPLE","SKYBLUE","GREY","GREY2","RED3","GREEN2","YELLOW","BLUE2","PURPLE2","BLUE3","WHITE"]):
            setattr(self,c,''.join(('\x1b[$;5;',str(i),'m')))

            
COLOR=__color__()        

def __fgc__(c):
    return c.replace("$",'38')
def __bgc__(c):
    return c.replace("$",'48')



def paint(txt, **kwargs):
    c=""
    bg=""
    cend=""
    for k,v in kwargs.items():
        if k in ['color','c','fg','fgc']:
            c=v
        if k in ['bg','bgcolor','bgc']:
            bg=v
    if c:
        c=__fgc__(c)
        cend=__CEND__
    if bg:
        bg=__bgc__(bg)
        cend=__CEND__

    return bg+c+txt+cend

def formatting(val,**kwargs):
    d=0
    paint__=None
    for k,v in kwargs.items():
        if k in ['d','decimals']:
            d=v
        if k in ['between',"paint"]:
            paint__ = v
    val = ('{:.'+str(d)+'f}').format(val)
    if paint__:
        val = val.join(tuple(map(lambda x: x,paint__)))
    return paint(val,**kwargs)

def FORMAT_MW(val,paint=None):
    return formatting(val,d=2,paint=paint,c=COLOR.WHITE,bg=COLOR.BLUE)
def FORMAT_C(val,paint=None):
    return formatting(val,paint=paint,c=COLOR.GREEN2,bg=COLOR.BLACK)
def FORMAT_MC(val,paint=None):
    return formatting(val,d=2,paint=paint,c=COLOR.YELLOW,bg=COLOR.BLACK)
        
def line_tag(label='',n=20,marker='-',c=COLOR.GREY,bg=COLOR.BLACK):
    if label:
        label=label.join([' ']*2)
    for i in range(n):
        print(marker, end='', flush=True)
    print(__bgc__(bg)+__fgc__(c)+label+__CEND__, end='', flush=True)
    for i in range(n):
        print(marker, end='', flush=True)
    print()
def tag(txt,c=COLOR.GREY,bg=COLOR.BLACK):
    return __bgc__(bg)+__fgc__(c)+txt+__CEND__
    

# def hlabel(txt,c="#D7DBDD",bg="#17202A"):
#     return "<font color="+c+" bgcolor="+bg+">"+txt+"</font>"

# def hnlabel(val,d=0,c="#FDFEFE",bg="#17202A",paint=None):
#     if paint:
#         val= formatting(val,d=d).join(tuple(map(lambda x: x,paint)))
#     else:
#         val= formatting(val,d=d)
#     return "<font color="+c+" bgcolor="+bg+">"+val+"</font>"