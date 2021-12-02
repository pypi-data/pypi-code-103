# -*- coding: utf-8 -*-

import numpy as np
import scipy.stats as sct
import matplotlib.pyplot as plt

class QQPlot():
    def __init__(self, data):
        self.data = data.to_frame()
        self.data = self.data[self.data["residual"].notna()]
        self.data = self.data.sort_values(["residual"])
        self.data["i"] = np.arange(1, len(self.data)+1).astype(int)
        self.data.set_index("i",inplace=True)
        
        self.data["Q"] = np.nan
        if len(self.data)<=10:
            i=1
            while i<=len(self.data):
                self.data["Q"][i] = ( i - (3/8) ) / ( len(self.data) + (1/4) )
                i = i + 1
        else:
            i=1
            while i<=len(self.data):
                self.data["Q"][i] = ( i - (1/2) ) / len(self.data)
                i = i + 1
                
        self.data["Z"] = self.data["Q"].apply(sct.norm.ppf)   
        
    def __repr__(self):
        return (
        # "QQ Plot " + self.modelo+"\n"+
        str(self.data)
        )
    
    def graficar(self,titulo="", xlabel="", ylabel=""):
        """Grafíca el QQ-Plot\n
        titulo: Título de la gráfica\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))
        
        # Puntos 
        ax.plot(self.data["Z"],self.data["residual"],"o")
        
        a, b = np.polyfit(self.data["Z"], self.data["residual"], deg=1)
        y_est = a * self.data["Z"] + b
        
        
        
        y_err = sct.t.ppf(0.05, len(self.data)-2) * ( ((1/len(self.data["Z"])) + ( self.data["Z"]**2/((self.data["Z"]**2).sum()) ) )**0.5 )     
        
        self.data["a"] = y_est - y_err
        self.data["est"] = y_est
        self.data["b"] = y_est + y_err
        
        # Área de intervalo
        ax.fill_between(self.data["Z"], y_est - y_err, y_est + y_err, alpha=0.2)
        
        
        
        ax.plot(self.data["Z"], self.data["a"], '-')
        ax.plot(self.data["Z"], self.data["b"], '-')
        
        
        # Linea de regresión
        ax.plot(self.data["Z"], y_est, '-')
        
        
        
               
        
        
        if titulo!="":
            ax.set_title(titulo)
        else:
            ax.set_title("QQ-Plot")
        if xlabel != "":
            ax.set_xlabel(xlabel)
        else:
            ax.set_xlabel("Z")
        if ylabel != "":
            ax.set_ylabel(ylabel)
        else:
            ax.set_ylabel("residuales")

        ax.grid(linestyle=":")
        # ax.legend()
        plt.show()