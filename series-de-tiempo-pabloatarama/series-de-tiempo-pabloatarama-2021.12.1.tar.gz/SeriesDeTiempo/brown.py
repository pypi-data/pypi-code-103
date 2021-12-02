# -*- coding: utf-8 -*-

import numpy as np
import SeriesDeTiempo.serie
import copy

class Brown(SeriesDeTiempo.serie.Modelo):
    """docstring for brown."""

    def __init__(self, data,alfa,M1,M2):
        self.modelo = "DE BROWN O SUAVIZACIÓN EXPONENCIAL DOBLE"
        self.data = data
        self.comprobado = False
        self.alfa = alfa

        self.data["Mat"] = np.nan
        self.data["Maat"] = np.nan       
        self.data["at"] = np.nan
        self.data["bt"] = np.nan
        self.data["ft"] = np.nan
        
        if M1 == None:
            self.data["Mat"][0] = self.data["yt"][1]
        else:
            self.data["Mat"][0] = M1
            
        if M2 == None:
            self.data["Maat"][0] = self.data["yt"][1]
        else:
            self.data["Maat"][0] = M2

        
        t = 1
        while (t < len(self.data)):
            
            self.data["Mat"][t] = ( alfa*self.data["yt"][t] ) + ( (1-alfa)*self.data["Mat"][t-1] )
            self.data["Maat"][t] = ( alfa*self.data["Mat"][t] ) + ( (1-alfa)*self.data["Maat"][t-1] )
            self.data["at"][t] = 2 * self.data["Mat"][t] - self.data["Maat"][t]
            self.data["bt"][t] = ( alfa/(1-alfa) ) * ( self.data["Mat"][t] - self.data["Maat"][t] )
            
            if t > 1:
                self.data["ft"][t] = self.data["at"][t-1] + self.data["bt"][t-1]
            
            t = t+1
            
        self.calcularErrores()

    def __repr__(self):
        return (
        "MODELO "+self.modelo+"\n"+
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
        
        while ti < t + n:

            if (nuevo.data.index != ti).all():
                nuevo.data.loc[ti]=np.nan
                
            nuevo.data["ft"][ti]= nuevo.data["at"][t-1] + nuevo.data["bt"][t-1] * ( ti - t + 1 )
            
            ti = ti + 1
        
        nuevo.calcularErrores()
        return nuevo
        
        
        