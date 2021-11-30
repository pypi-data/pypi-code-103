import numpy.ma as ma
from . import wolfpy
from .wolf_array import WolfArray

class OneWolfResult:
    waterdepth : WolfArray 
    qx : WolfArray
    qy : WolfArray

    def __init__(self,fname = None,mold = None):
        self.waterdepth = WolfArray()
        self.qx = WolfArray()
        self.qy = WolfArray()

class Wolfresults_2D(object):
    
    filename=""
    nb_blocks = 0
    myblocks:dict

    def __init__(self,fname = None,mold = None):

        if fname is not None:
            self.filename = fname.ljust(255)
            wolfpy.r2d_init(self.filename)
            self.nb_blocks = wolfpy.r2d_nbblocks()
            self.myblocks={}
            for i in range(self.nb_blocks):
                curblock = OneWolfResult()
                self.myblocks['block'+str(i+1)] = curblock
                nbx,nby,dx,dy,ox,oy,tx,ty = wolfpy.r2d_hblock(i+1)
                
                self.myblocks['block'+str(i+1)].waterdepth.dx = dx
                self.myblocks['block'+str(i+1)].waterdepth.dy = dy
                self.myblocks['block'+str(i+1)].waterdepth.nbx = nbx
                self.myblocks['block'+str(i+1)].waterdepth.nby = nby
                self.myblocks['block'+str(i+1)].waterdepth.origx = ox
                self.myblocks['block'+str(i+1)].waterdepth.origy = oy
                self.myblocks['block'+str(i+1)].waterdepth.translx = tx
                self.myblocks['block'+str(i+1)].waterdepth.transly = ty
                
                self.myblocks['block'+str(i+1)].qx.dx = dx
                self.myblocks['block'+str(i+1)].qx.dy = dy
                self.myblocks['block'+str(i+1)].qx.nbx = nbx
                self.myblocks['block'+str(i+1)].qx.nby = nby
                self.myblocks['block'+str(i+1)].qx.origx = ox
                self.myblocks['block'+str(i+1)].qx.origy = oy
                self.myblocks['block'+str(i+1)].qx.translx = tx
                self.myblocks['block'+str(i+1)].qx.transly = ty

                self.myblocks['block'+str(i+1)].qx.dx = dx
                self.myblocks['block'+str(i+1)].qx.dy = dy
                self.myblocks['block'+str(i+1)].qx.nbx = nbx
                self.myblocks['block'+str(i+1)].qx.nby = nby
                self.myblocks['block'+str(i+1)].qx.origx = ox
                self.myblocks['block'+str(i+1)].qx.origy = oy
                self.myblocks['block'+str(i+1)].qx.translx = tx
                self.myblocks['block'+str(i+1)].qx.transly = ty

            self.allocate_ressources()
            return

    def allocate_ressources(self):
        for i in range(self.nb_blocks):
            self.myblocks['block'+str(i+1)].waterdepth.allocate_ressources()
            self.myblocks['block'+str(i+1)].qx.allocate_ressources()
            self.myblocks['block'+str(i+1)].qy.allocate_ressources()

    def read_oneresult(self,which=-1):
        for i in range(self.nb_blocks):
            nbx = self.myblocks['block'+str(i+1)].waterdepth.nbx
            nby = self.myblocks['block'+str(i+1)].waterdepth.nby
            self.myblocks['block'+str(i+1)].waterdepth.array, self.myblocks['block'+str(i+1)].qx.array, self.myblocks['block'+str(i+1)].qy.array = wolfpy.r2d_getresults(which,nbx,nby,i+1)
            self.myblocks['block'+str(i+1)].waterdepth.array=ma.masked_equal(self.myblocks['block'+str(i+1)].waterdepth.array,0.)
            self.myblocks['block'+str(i+1)].qx.array=ma.masked_where(self.myblocks['block'+str(i+1)].waterdepth.array==0.,self.myblocks['block'+str(i+1)].qx.array)
            self.myblocks['block'+str(i+1)].qy.array=ma.masked_where(self.myblocks['block'+str(i+1)].waterdepth.array==0.,self.myblocks['block'+str(i+1)].qy.array)

    def get_values_as_wolf(self,i,j,which_block=1):
        h=-1
        qx=-1
        qy=-1
        vx=-1
        vy=-1
        vabs=-1
        fr=-1
        
        nbx = self.myblocks['block'+str(which_block)].waterdepth.nbx
        nby = self.myblocks['block'+str(which_block)].waterdepth.nby

        if(i>0 and i<=nbx and j>0 and j<=nby):
            h = self.myblocks['block'+str(which_block)].waterdepth.array[i-1,j-1]
            qx = self.myblocks['block'+str(which_block)].qx.array[i-1,j-1]
            qy = self.myblocks['block'+str(which_block)].qy.array[i-1,j-1]
            if(h>0.):
                vx = qx/h
                vy = qy/h
                vabs=(vx**2.+vy**2.)**.5
                fr = vabs/(9.81*h)**.5
        
        return h,qx,qy,vx,vy,vabs,fr

    def get_values_from_xy(self,x,y):
        h=-1
        qx=-1
        qy=-1
        vx=-1
        vy=-1
        vabs=-1
        fr=-1
        
        exists=False
        for which_block in range(1,7):
            nbx = self.myblocks['block'+str(which_block)].waterdepth.nbx
            nby = self.myblocks['block'+str(which_block)].waterdepth.nby
            i,j=self.get_ij_from_xy(x,y,which_block=which_block)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                h = self.myblocks['block'+str(which_block)].waterdepth.array[i-1,j-1]
                qx = self.myblocks['block'+str(which_block)].qx.array[i-1,j-1]
                qy = self.myblocks['block'+str(which_block)].qy.array[i-1,j-1]
                if(h>0.):
                    vx = qx/h
                    vy = qy/h
                    vabs=(vx**2.+vy**2.)**.5
                    fr = vabs/(9.81*h)**.5
                    exists=True
                    break
        if exists:
            return (h,qx,qy,vx,vy,vabs,fr),(i,j,which_block)
        else:
            return (-1,-1,-1,-1,-1,-1,-1),('-','-','-')

    def get_xy_from_ij(self,i,j,which_block):
        x,y = self.myblocks['block'+str(which_block)].waterdepth.get_xy_from_ij(i,j)
        return x,y

    def get_ij_from_xy(self,x,y,which_block):
        i,j = self.myblocks['block'+str(which_block)].waterdepth.get_ij_from_xy(x,y)
        return i+1,j+1 # En indices WOLF

