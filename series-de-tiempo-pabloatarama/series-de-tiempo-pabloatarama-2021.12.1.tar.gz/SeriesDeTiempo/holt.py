# -*- coding: utf-8 -*-

import numpy as np
import SeriesDeTiempo.serie
import copy

class Holt(SeriesDeTiempo.serie.Modelo):
    """docstring for Holt."""

    def __init__(self, data, alfa, beta, M, T):
        self.modelo = "DE HOLT"
        self.data = data
        self.comprobado = False

        self.data["Mt"] = np.nan
        self.data["Tt"] = np.nan
        self.data["ft"] = np.nan
        
        if M == None:
            self.data["Mt"][0] = self.data["yt"][1]
        else:
            self.data["Mt"][0] = M
            
        self.data["Tt"][0] = T
        
        t = 1
        while (t < len(self.data)):
            
            self.data["Mt"][t] = ( alfa*self.data["yt"][t] ) + ( 1 - alfa ) * ( self.data["Mt"][t-1] + self.data["Tt"][t-1] )
            self.data["Tt"][t] = beta * ( self.data["Mt"][t] - self.data["Mt"][t-1] ) + ( 1 - beta )*self.data["Tt"][t-1]
            
            if t > 1:
                self.data["ft"][t] = self.data["Mt"][t-1] + self.data["Tt"][t-1]
            
            t = t+1
            
        self.calcularErrores()

    def __repr__(self):
        return (
        "MODELO " + self.modelo+"\n"+
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
            print(ti)
            if (nuevo.data.index != ti).all():
                nuevo.data.loc[ti]=np.nan
                
            nuevo.data["ft"][ti]= nuevo.data["Mt"][t-1] + nuevo.data["Tt"][t-1] * ( ti - t + 1 )
            
            ti = ti + 1
        
        nuevo.calcularErrores()
        return nuevo