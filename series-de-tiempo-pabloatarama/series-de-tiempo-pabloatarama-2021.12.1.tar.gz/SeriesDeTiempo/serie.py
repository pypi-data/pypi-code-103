import matplotlib.pyplot as plt
import pandas as pd
import numpy as np



class Serie():
    """data: es el DataFrame donde se encuentran los datos\n
       columna: Es la columna del DataFrame que se utilizará como datos"""

    def __init__(self, data, columna=""):
        pd.set_option('mode.chained_assignment', None)
        # super(SeriesDeTiempo, self).__init__()

        # self.data = data[columna: "yt"]


        # self.data.shift()
        # print(data)

        if columna in data.columns:
            self.data = data.rename(columns={columna:"yt"})
        else:
            raise ErrorDeSerie(columna)

        self.data["t"]=np.arange(0,len(self.data))
        self.data["t"] = self.data["t"].astype(int)
        self.data.set_index("t",inplace=True)
        self.data.loc[len(self.data)]=np.nan
        self.data = self.data.shift()
        # self.data.index = self.data["t"]

    def __repr__(self):
        return (
        "SERIE DE TIEMPO\n"+
        str(self.data)
        )

    # def __getitem__(self, key):
    #     return self.data[key];

    def naive(self):
        import SeriesDeTiempo.naive
        return SeriesDeTiempo.naive.Naive(self.data[:])

    def mediaMovilSimple(self, longitud=3, desfasada=False):
        """longitud: longitud de la media movil simple, por defecto es 3\n
        desfasada: Si es desfasada o no (True o False), por defecto es False"""
        import SeriesDeTiempo.mediaMovilSimple
        return SeriesDeTiempo.mediaMovilSimple.MediaMovilSimple(self.data[:],longitud,desfasada)

    def mediaMovilDoble(self, longitud=3, desfasada=False):
        """longitud: longitud de ambas medias moviles, por defecto es 3\n
        desfasada: Si es desfasada o no (True o False)"""
        import SeriesDeTiempo.mediaMovilDoble
        return SeriesDeTiempo.mediaMovilDoble.MediaMovilDoble(self.data[:],longitud,desfasada)

    def mediaMovilPonderada(self,ponderaciones):
        """ponderaciones: lista con alfas a ponderar ej: [alfa1,alfa2,alfa3] donde alfa1 > alfa2 > alfa3, etc"""
        import SeriesDeTiempo.mediaMovilPonderada
        return SeriesDeTiempo.mediaMovilPonderada.MediaMovilPonderada(self.data[:],ponderaciones)

    def suavizacionExponencialSimple(self,alfa=0.5):
        """alfa: parámetro alfa del modelo, por defecto es 0.5"""
        import SeriesDeTiempo.suavizacionExponencialSimple
        return SeriesDeTiempo.suavizacionExponencialSimple.SuavizacionExponencialSimple(self.data[:],alfa)

    def mediaMovilDobleConTendencia(self,longitud=3):
        """longitud: longitud de ambas medias moviles, por defecto es 3"""
        import SeriesDeTiempo.mediaMovilDobleConTendencia
        return SeriesDeTiempo.mediaMovilDobleConTendencia.MediaMovilDobleConTendencia(self.data[:],longitud)

    def brown(self, alfa=0.5, M1=None, M2=None):
        """alfa: parámetro alfa del modelo, por defecto es 0.5\n
        M1: Valor inicial de Mat, por defecto es yt para t = 1\n
        M2: Valor inicial de Maat, por defecto es yt para t = 1"""
        import SeriesDeTiempo.brown
        return SeriesDeTiempo.brown.Brown(self.data[:], alfa, M1, M2)

    def holt(self, alfa=0.5, beta=0.5, M=None, T=0):
        """alfa: parámetro alfa del modelo, por defecto es 0.5\n
        beta: parámetro beta del modelo, por defecto es 0.5\n
        M: Valor inicial de Mt, por defecto es yt para t = 1\n
        T: Valor inicial de Tt, por defecto es 0"""
        import SeriesDeTiempo.holt
        return SeriesDeTiempo.holt.Holt(self.data[:], alfa, beta, M, T)

    def holtYWinters(self, metodo, alfa=0.5, beta=0.5, gamma=0.5, L=4):
        """metodo: El método a utilizar "aditivo" para el método aditivo y "multiplicativo" para el método multiplicativo\n
        alfa: parámetro alfa del modelo, por defecto es 0.5\n
        beta: parámetro beta del modelo, por defecto es 0.5\n
        gamma: parámetro gamma del modelo, por defecto es 0.5\n
        L: Longitud de la estacionalidad, por defecto es 4"""
        import SeriesDeTiempo.holtYWinters
        return SeriesDeTiempo.holtYWinters.HoltYWinters(self.data[:], metodo, alfa, beta, gamma, L)

    def descomposicion(self, metodo, L=12):
        """metodo: El método a utilizar "aditivo" para el método aditivo y "multiplicativo" para el método multiplicativo\n
        L: Longitud de la estacionalidad, por defecto es 12"""
        import SeriesDeTiempo.descomposicion
        return SeriesDeTiempo.descomposicion.Descomposicion(self.data[:], metodo, L)

    def graficar(self,titulo="", xlabel="", ylabel=""):
        """Grafíca la serie de tiempo\n
        titulo: Título de la gráfica\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))
        # self.data[["yt","ft"]].plot()

        ax.plot(self.data["yt"],label="yt")
        if titulo!="":
            ax.set_title(titulo)
        if xlabel != "":
            ax.set_xlabel(xlabel)

        if ylabel != "":
            ax.set_ylabel(ylabel)

        ax.grid(linestyle=":")
        ax.legend()
        plt.show()


    def cajasEstacionalidad(self, ciclo=4,comienzo=1,titulo="",xlabel="",ylabel="",grilla=True):
        """Muestra un gráfico de cajas de la serie en ciclos\n
        ciclo: Ciclos en que se agrupará los datos, por defecto es 4\n
        titulo: Título de la gráfica\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y\n
        grilla: Grilla de gráfica (True o False), por defecto True"""

        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))

        t=comienzo
        data = []
        while t<ciclo+comienzo:
            data.append(self.data["yt"][t::ciclo])
            t = t+1
        ax.boxplot(data)

        if titulo!="":
            ax.set_title(titulo)
        if xlabel != "":
            ax.set_xlabel(xlabel)

        if ylabel != "":
            ax.set_ylabel(ylabel)

        if grilla:
            ax.grid(linestyle=":")

        plt.show()


    def cajas(self, L=4,comienzo=1,titulo="",xlabel="",ylabel="",grilla=True):
        """Muestra un gráfico de cajas de la serie en ciclos\n
        ciclo: Ciclos en que se agrupará los datos\n
        titulo: Título de la gráfica\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y\n
        grilla: Grilla de gráfica (True o False), por defecto True"""


        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))


        t=comienzo
        data = []
        while t<len(self.data):
            data.append(self.data["yt"][t:t+L])
            t = t + L
        ax.boxplot(data)

        if titulo!="":
            ax.set_title(titulo)
        if xlabel != "":
            ax.set_xlabel(xlabel)

        if ylabel != "":
            ax.set_ylabel(ylabel)

        if grilla:
            ax.grid(linestyle=":")

        plt.show()

class ErrorDeMetodo(Exception):
    def __init__(self, valor, modelo):
        self.valor = valor
        self.modelo = modelo

    def __str__(self):
        return "PABLEX: Error de método, '" + str(self.valor) + "' no es un método válido para el MODELO " + self.modelo + "."

class ErrorDeSerie(Exception):
    def __init__(self, columna):
        self.columna = columna

    def __str__(self):
        return "PABLEX: La columna '" + str(self.columna) + "' no existe en el DataFrame."


class Modelo:

    def __init__(self):
        self.prop = "asd"

    def graficar(self,titulo="", xlabel="", ylabel=""):
        """Grafíca la serie de tiempo con el modelo\n
        titulo: Título de la gráfica, por defecto es el nombre del modelo\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))

        ax.plot(self.data["yt"],label="yt")
        ax.plot(self.data["ft"],label="ft")
        if titulo=="":
            ax.set_title("MODELO "+self.modelo)
        else:
            ax.set_title(titulo)
        if xlabel != "":
            ax.set_xlabel(xlabel)

        if ylabel != "":
            ax.set_ylabel(ylabel)

        ax.grid(linestyle=":")
        ax.legend()
        plt.show()

    def calcularErrores(self):
        self.data["residual"] = self.data["yt"] - self.data["ft"]
        self.data["e"] = abs(self.data["residual"])
        self.data["mse"] = self.data["e"]**2
        self.errores = Errores(self.data, self.modelo)
        self.residual = Residual(self.data["residual"],self.modelo)

    def pronosticar(self, p=1, t=None):
        """Pronostica la serie de tiempo p periodos por delante\n
        p: cantidad de periodos a pronosticar, por defecto es 1.\n
        t: valor de t desde donde comenzará el pronóstico, por defecto comienza luego del último dato"""
        return self.pronosticarMetodo(p,t)





class Errores():
    """Muestra los errores de un modelo de pronóstico"""

    def __init__(self, data, modelo):
        self.mse = data["mse"].mean()
        self.rmse = pow(self.mse,0.5)
        yt = pow((data["yt"]**2).mean(),0.5)
        ft = pow((data["ft"]**2).mean(),0.5)
        self.u_theil = self.rmse / ( yt + ft )

        self.modelo = modelo


    def __repr__(self):
        return (
        "ERRORES MODELO "+self.modelo+"\n"
        "MSE:\t\t" + str(self.mse) + "\n"
        "RMSE:\t\t" + str(pow(self.mse,0.5)) + "\n"
        "U-THEIL:\t" + str(self.u_theil)
        )

class Residual():
    def __init__(self, data, modelo):
        self.data = data;
        self.modelo = modelo

    def __repr__(self):
        return (
        "RESIDUAL DEL "+self.modelo+"\n"+
        str(self.data)
        )

    def graficar(self,titulo="", xlabel="", ylabel=""):
        """Grafíca el residual del modelo\n
        titulo: Título de la gráfica, por defecto es el nombre del modelo\n
        xlabel: Título del eje x\n
        ylabel: Título del eje y"""
        fig, ax = plt.subplots(dpi=300, figsize=(9.6,5.4))
        # self.data[["yt","ft"]].plot()

        ax.plot(self.data,label="residual")
        # plt.axhline(y=0, linestyle="dashed")

        if titulo == "":
            ax.set_title("RESIDUAL DEL MODELO DE "+self.modelo)
        else:
            ax.set_title(titulo)

        if xlabel != "":
            ax.set_xlabel(xlabel)

        if ylabel != "":
            ax.set_ylabel(ylabel)

        ax.grid()

        ax.legend()
        plt.show()

    def qqPlot(self):
        import SeriesDeTiempo.pruebas
        return SeriesDeTiempo.pruebas.QQPlot(self.data[:])

