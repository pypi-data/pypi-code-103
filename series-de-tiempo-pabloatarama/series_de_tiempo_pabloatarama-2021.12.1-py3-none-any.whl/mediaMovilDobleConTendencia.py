# -*- coding: utf-8 -*-

import numpy as np
import SeriesDeTiempo.serie
import copy

class MediaMovilDobleConTendencia(SeriesDeTiempo.serie.Modelo):
    """docstring for MediaMovilDobleConTendencia."""

    def __init__(self, data,longitud):
        self.modelo = "MEDIA MÓVIL DOBLE CON TENDENCIA"
        self.data = data
        self.comprobado = False

        self.data["Mst"] = self.data["yt"].rolling(window=longitud).mean()
        self.data["Msst"] = self.data["Mst"].rolling(window=longitud).mean()       
        
        
        self.data["at"] = np.nan
        self.data["bt"] = np.nan
        self.data["ft"] = np.nan
        
        t = ( longitud * 2 ) - 1
        while ( t<len(self.data) ):
            self.data["at"][t] = 2 * self.data["Mst"][t] - self.data["Msst"][t]
            self.data["bt"][t] = ( 2/(longitud-1) ) * ( self.data["Mst"][t] - self.data["Msst"][t] )
            
            if t > (longitud*2)-1:
                self.data["ft"][t] = self.data["at"][t-1] + self.data["bt"][t-1]
            
            t = t + 1
            
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
            print(ti)
            if (nuevo.data.index != ti).all():
                nuevo.data.loc[ti]=np.nan
                
            nuevo.data["ft"][ti]= nuevo.data["at"][t-1] + nuevo.data["bt"][t-1] * ( ti - t + 1 )
            
            ti = ti + 1
        
        nuevo.calcularErrores()
        return nuevo