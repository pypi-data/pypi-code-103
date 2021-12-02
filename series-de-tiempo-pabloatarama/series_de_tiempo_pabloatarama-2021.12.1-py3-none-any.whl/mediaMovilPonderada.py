# -*- coding: utf-8 -*-

import numpy as np
import SeriesDeTiempo.serie
import copy

class MediaMovilPonderada(SeriesDeTiempo.serie.Modelo):
    """docstring for MediaMovilDoble."""

    def __init__(self, data, ponderaciones):
        self.modelo = "MEDIA MÓVIL PONDERADA"
        self.data = data
        self.comprobado = True
        self.data["ft"] = np.nan
        self.ponderaciones = ponderaciones
        
        cantDeciMax=0
        i=0
        while i<len(ponderaciones):
            cantDeci = len(str(ponderaciones[i]).split(".")[1])
            if cantDeciMax < cantDeci: 
                cantDeciMax = cantDeci
            i = i + 1 

        if round(sum(ponderaciones),cantDeciMax) != 1:
            raise ErrorDePonderaciones(sum(ponderaciones))
        
        t = len(ponderaciones)+1
        while (t < len(self.data)):
            
            i = t - len(ponderaciones)
            promedio = 0
            while (i<t):
                promedio = promedio + self.data["yt"][i] * ponderaciones[t-i-1]
                i = i+1
            
            self.data["ft"][t] = promedio
            
            t = t + 1

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
        
        t = t0
        while t < t0 + n:
            print("t = " + str(t))
            if (nuevo.data.index != t).all():
                nuevo.data.loc[t]=np.nan

            suma = 0
            ti=1
            while ti<=len(self.ponderaciones):

                if t-ti<t0:
                    suma = suma + nuevo.data["yt"][t-ti] * self.ponderaciones[ti-1]
                else:
                    suma = suma + nuevo.data["ft"][t-ti] * self.ponderaciones[ti-1]
                print("ti = " + str(ti))
                ti = ti + 1

            nuevo.data["ft"][t] = suma
            t = t + 1
        
        nuevo.calcularErrores()
        return nuevo
            
class ErrorDePonderaciones(Exception):
    def __init__(self, suma):
        self.suma = suma
    
    def __str__(self):
        return "PABLEX: La suma de las ponderaciones es " + str(self.suma) + " y debe ser de 1."