# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import SeriesDeTiempo.serie

class Descomposicion(SeriesDeTiempo.serie.Modelo):
    """docstring for Descomposicion."""

    def __init__(self, data, metodo, L):
        self.modelo = "DE DESCOMPOSICIÓN"
        self.data = data
        self.comprobado = True

        # self.data["Mt"] = np.nan
        
        if int(L) % 2 == 0:
            l2 = int(-(L/2))
            self.data["M1t"] = self.data["yt"].rolling(window=L).mean().shift(l2)
            self.data["Tt"] = self.data["M1t"].rolling(window=2).mean()
            
        else:
            l2 = round(-(L/2))
            self.data["Tt"] = self.data["yt"].rolling(window=L).mean().shift(l2)
        
        
        if metodo=="aditivo":
            
            self.modelo = self.modelo + " ADITIVO"
            
            self.data["yt-Tt"] = self.data["yt"]-self.data["Tt"]
            
            self.data["St"] = np.nan
            
            t=1
            while (t<=L):
                self.data["St"][t] = self.data["yt-Tt"][t::L].mean()
                t = t + 1
                
            t=1 
            prom = self.data["St"][1:(L+1)].mean()
            while (t<=L):
                self.data["St"][t::L] = self.data["St"][t]-prom
                t = t + 1

            self.data["yt-St"] = self.data["yt"]-self.data["St"]
            
            self.data["ft"] = self.data["St"]+self.data["Tt"]

            
            
        elif metodo=="multiplicativo":
            
            self.modelo = self.modelo + " MULTIPLICATIVO"
            
            self.data["yt/Tt"] = self.data["yt"]/self.data["Tt"]
            
            self.data["St"] = np.nan
            
            t=1
            while (t<=L):
                self.data["St"][t] = self.data["yt/Tt"][t::L].mean()
                t = t + 1
                
            t=1 
            prom = self.data["St"][1:(L+1)].mean()
            while (t<=L):
                self.data["St"][t::L] = self.data["St"][t]/prom
                t = t + 1

            self.data["yt/St"] = self.data["yt"]/self.data["St"]
            
            self.data["ft"] = self.data["St"]*self.data["Tt"]
            
            
        else:
            raise SeriesDeTiempo.serie.ErrorDeMetodo(metodo,self.modelo)
        

        self.tendencia = Tendencia(self.data["Tt"], self.modelo)
        self.estacionalidad = Estacionalidad(self.data["St"][1:L+1], self.modelo)
        self.calcularErrores()
        
    def __repr__(self):
        return (
        "MODELO "+self.modelo+"\n"+
        str(self.data)
        )

    def graficar(self,titulo=""):
        """Grafíca la serie de tiempo"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))
        # self.data[["yt","ft"]].plot()

        ax.plot(self.data["yt"],label="yt")
        ax.plot(self.data["Tt"],label="Tt")
        if titulo=="":
            ax.set_title("MODELO "+self.modelo)
        else:
            ax.set_title(titulo)
        ax.legend()
        ax.grid(linestyle=":")
        plt.show()

    def pronosticar(self, n):
        """Pronostica la serie de tiempo n periodos por delante"""
        print("Acá se supone corre un pronóstico para "+str(n)+"periodos por delante xd") 
            
            
            
class Tendencia:
    def __init__(self, data, modelo):
        self.data = data;
        self.modelo = modelo
    
    def __repr__(self):
        return (
        "TENDENCIA DEL "+self.modelo+"\n"+
        str(self.data)
        )
    
    def graficar(self, titulo="", xlabel="", ylabel=""):
        """Grafica la tendencia descompuesta de la serie de tiempo\n
        titulo: Título de la gráfica, por defecto es el nombre del modelo\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))
        # self.data[["yt","ft"]].plot()

        ax.plot(self.data,label="Tt")
        if titulo == "":
            ax.set_title("TENDENCIA DEL MODELO DE "+self.modelo)
        else:
            ax.set_title(titulo)
            
        if xlabel != "":
            ax.set_xlabel(xlabel)
          
        if ylabel != "":
            ax.set_ylabel(ylabel)
            
        ax.legend()
        ax.grid(linestyle=":")
        plt.show()

class Estacionalidad:
    def __init__(self, data, modelo):
        self.data = data;
        self.modelo = modelo
    
    def __repr__(self):
        return (
        "ESTACIONALIDAD DEL "+self.modelo+"\n"+
        str(self.data)
        )
    
    def graficar(self, titulo="", xlabel="", ylabel=""):
        """Grafica la estacionalidad descompuesta de la serie de tiempo\n
        titulo: Título de la gráfica, por defecto es el nombre del modelo\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))
        # self.data[["yt","ft"]].plot()

        ax.plot(self.data,label="St")
        
        if titulo == "":
            ax.set_title("ESTACIONALIDAD DEL MODELO DE "+self.modelo)
        else:
            ax.set_title(titulo)
            
        if xlabel != "":
            ax.set_xlabel(xlabel)
          
        if ylabel != "":
            ax.set_ylabel(ylabel)
            
        ax.legend()
        ax.grid(linestyle=":")
        plt.show()
