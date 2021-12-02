# -*- coding: utf-8 -*-

import SeriesDeTiempo.serie
import copy
import numpy as np

class MediaMovilSimple(SeriesDeTiempo.serie.Modelo):
    """docstring for MediaMovilSimple."""

    def __init__(self, data,longitud,desfasada):
        self.modelo = "MEDIA MÓVIL SIMPLE"
        self.data = data
        self.long = longitud
        self.desfasada = desfasada
        self.comprobado = True
        
        if (desfasada):
            self.data["ft"] = self.data["yt"].shift().rolling(window=longitud).mean() 
        else:
            self.data["ft"] = self.data["yt"].rolling(window=longitud).mean()       
        
        self.calcularErrores()

    def __repr__(self):
        return (
        "MODELO "+self.modelo+"\n"+
        str(self.data)
        )

    def pronosticarMetodo(self, n, t0):
        
        nuevo = copy.deepcopy(self)
        
        
        if t0!=None:
            t=t0
        else:
            long = len(nuevo.data)
            t=long
            t0=long
        
        if self.desfasada:
        
            t = t0
            while t < t0 + n:

                if (nuevo.data.index != t).all():
                    nuevo.data.loc[t]=np.nan

                suma = 0
                ti=1
                while ti<=self.long:

                    if t-ti<t0:
                        suma = suma + nuevo.data["yt"][t-ti]/self.long
                    else:
                        suma = suma + nuevo.data["ft"][t-ti]/self.long

                    ti = ti + 1

                nuevo.data["ft"][t] = suma
                t = t + 1

        else:
            t = t0
            while t < t0 + n:

                
                if (nuevo.data.index != t).all():
                    nuevo.data.loc[t]=np.nan

                suma = 0
                ti=0
                while ti<self.long:
                    
                    if t-ti<t0:
                        suma = suma + nuevo.data["yt"][t-ti]/self.long
                    else:
                        suma = suma + nuevo.data["ft"][t-ti-1]/self.long
                    
                    ti = ti + 1

                nuevo.data["ft"][t] = suma
                t = t + 1
        
        nuevo.calcularErrores()
        return nuevo
