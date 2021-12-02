# -*- coding: utf-8 -*-

import numpy as np
import SeriesDeTiempo.serie
import copy

class HoltYWinters(SeriesDeTiempo.serie.Modelo):
    """docstring for HoltYWinters."""

    def __init__(self, data, metodo, alfa, beta, gamma, L):
        self.modelo = "DE HOLT Y WINTERS"
        self.data = data
        self.metodo = metodo
        self.L = L
        self.alfa = alfa
        self.beta = beta
        self.gamma = gamma
        self.comprobado = True
        
        longitudAntigua = len(self.data)
        t = longitudAntigua 
        while t<longitudAntigua+L-1:
            self.data.loc[t]=np.nan
            t = t + 1
        
        self.data = self.data.shift(L-1)
        self.data.index = self.data.index - L + 1

        self.data["Mt"] = np.nan
        self.data["Tt"] = np.nan
        self.data["St"] = np.nan
        self.data["ft"] = np.nan
        
        # M0 (Es igual en aditivio que multiplicativo)
        t=1
        M0suma = 0
        while t<=L:
            M0suma = M0suma + self.data["yt"][t]/L
            t = t+1
        self.data["Mt"][0] = M0suma
        
        # T0 (Es igual en aditivio que multiplicativo)
        self.data["Tt"][0] = 0
        
        if metodo=="aditivo":
            
            self.modelo = self.modelo + " ADITIVO"
            
            #S0
            t=1
            while t<=L:
                self.data["St"][t-L] = self.data["yt"][t] - self.data["Mt"][0]
                t = t+1
            
            t=1
            while t<=(len(self.data)-L):
                self.data["Mt"][t] = alfa * ( self.data["yt"][t] - self.data["St"][t-L] ) + (1- alfa) * ( self.data["Mt"][t-1] + self.data["Tt"][t-1] )
                
                self.data["Tt"][t] = beta * ( self.data["Mt"][t] - self.data["Mt"][t-1] ) + ( 1 - beta ) * self.data["Tt"][t-1] 
                
                self.data["St"][t] = gamma * ( self.data["yt"][t] - self.data["Mt"][t] ) + (1- gamma)*self.data["St"][t-L]
                
                if t>L:
                    self.data["ft"][t] = self.data["Mt"][t-1] + self.data["Tt"][t-1] + self.data["St"][t-L]
                t = t+1
            
            
        
        elif metodo=="multiplicativo":
            
            self.modelo = self.modelo + " MULTIPLICATIVO"
            
            #S0
            t=1
            while t<=L:
                self.data["St"][t-L] = self.data["yt"][t] / self.data["Mt"][0]
                t = t+1
            
            # Mt
            t=1
            while t<=(len(self.data)-L):
                self.data["Mt"][t] = alfa * ( self.data["yt"][t] / self.data["St"][t-L] ) + (1- alfa) * ( self.data["Mt"][t-1] + self.data["Tt"][t-1] )
                
                self.data["Tt"][t] = beta * ( self.data["Mt"][t] - self.data["Mt"][t-1] ) + ( 1 - beta ) * self.data["Tt"][t-1]
                
                self.data["St"][t] = gamma * ( self.data["yt"][t] / self.data["Mt"][t] ) + (1- gamma)*self.data["St"][t-L]
                
                if t>L:
                    self.data["ft"][t] = ( self.data["Mt"][t-1] + self.data["Tt"][t-1] ) * self.data["St"][t-L]
                t = t+1
        else:
            raise SeriesDeTiempo.serie.ErrorDeMetodo(metodo,self.modelo)
        
            
        self.calcularErrores()

    def __repr__(self):
        return (
        "MODELO " + self.modelo+"\n"+
        str(self.data)
        )


    def pronosticarMetodo(self, n, t):
        
        nuevo = copy.deepcopy(self)
        
        if n > self.L:
            raise ErrorDeEstacionalidad(n,self.L)
        
        if t!=None:
            ti=t
        else:
            long = len(nuevo.data)-self.L
            ti=long+1
            t=long+1
        
        if self.metodo == "aditivo":
            
            while ti < t + n:

                if (nuevo.data.index != ti).all():
                    nuevo.data.loc[ti]=np.nan
                    
                # nuevo.data["Mt"][ti] = self.alfa * ( nuevo.data["ft"][ti] - nuevo.data["St"][ti-self.L] ) + (1- self.alfa) * ( nuevo.data["Mt"][ti-1] + nuevo.data["Tt"][ti-1] )
                
                # nuevo.data["Tt"][ti] = self.beta * ( nuevo.data["Mt"][ti] - nuevo.data["Mt"][ti-1] ) + ( 1 - self.beta ) * nuevo.data["Tt"][ti-1] 
                
                # nuevo.data["St"][ti] = self.gamma * ( nuevo.data["ft"][ti] - nuevo.data["Mt"][ti] ) + (1 - self.gamma)*nuevo.data["St"][ti-self.L]
                
                
                    
                nuevo.data["ft"][ti]= ( nuevo.data["Mt"][t-1] + ( ti - t + 1 ) * nuevo.data["Tt"][t-1] ) + nuevo.data["St"][ti - self.L]
                
                ti = ti + 1
        
        elif self.metodo == "multiplicativo":
                    
            while ti < t + n:

                if (nuevo.data.index != ti).all():
                    nuevo.data.loc[ti]=np.nan
                    
                nuevo.data["ft"][ti]= ( nuevo.data["Mt"][t-1] + ( ti - t + 1 ) * nuevo.data["Tt"][t-1] ) * nuevo.data["St"][ti - self.L]
                
                ti = ti + 1
        
        nuevo.calcularErrores()
        return nuevo
    
class ErrorDeEstacionalidad(Exception):
    def __init__(self, p, L):
        self.p = p
        self.L = L
    def __str__(self):
        return "PABLEX: No se puede realizar predicciones para un p > L (" + str(self.p) +" > "+ str(self.L) + ")."
    
    
    
    
    
    
    
    