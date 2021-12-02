# -*- coding: utf-8 -*-

import SeriesDeTiempo.serie
import numpy as np
import copy

class Naive(SeriesDeTiempo.serie.Modelo):
    """docstring for Naive."""

    def __init__(self, data):
        self.modelo = "NAÏVE"
        self.data = data
        self.data["ft"] = self.data["yt"].shift()
        self.comprobado = True
        self.calcularErrores()

    def __repr__(self):
        return (
        "MODELO " + self.modelo +"\n"+
        str(self.data)
        )

    def pronosticarMetodo(self, n, t):
        
        nuevo = copy.deepcopy(self)
        
        
        if t!=None:
            ti=t
        else:
            long = len(nuevo.data)
            ti=long
            t=long
        
        if (nuevo.data.index != ti).all():
            nuevo.data.loc[ti]=np.nan
        
        nuevo.data["ft"][ti] = nuevo.data["yt"][ti-1]
        
        ti = ti + 1
        while ti < t + n:

            if (nuevo.data.index != ti).all():
                nuevo.data.loc[ti]=np.nan
                
                
            nuevo.data["ft"][ti] = nuevo.data["ft"][ti-1]
            ti = ti + 1
        
        nuevo.calcularErrores()
        return nuevo
    
    
    
    
    