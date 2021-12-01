from .markov import formatear_markov, calcular_markov
from .shapley import formatear_shapley, calcular_shapley
from .heuristicos import calcular_heuristicos

class Modelo():
    def __init__(self, data, formateada=False) -> None:
        self.data = data
        self.formateada = formateada
        
        print("Data: ", data)
        print("Formateada: ", formateada)

        pass

    def markov(self, orden=1, ventana=30, touchpoints=8, conversion=True):

        if self.formateada == False:
            parametros = {
                'orden' : orden,
                'ventana' : ventana,
                'touchpoints' : touchpoints,
                'conversion' : conversion
            }
            print("Validados los parametros")
            data = formatear_markov(self.data, parametros)
        
        else:
            data = self.data

        resultado = calcular_markov(data)

        return resultado

    def shapley(self, ventana=30, touchpoints=8):

        if self.formateada == False:
            parametros = {
                'ventana' : ventana,
                'touchpoints' : touchpoints,
            }
            print("Validados los parametros")
            data = formatear_shapley(self.data, parametros)
        
        else:
            data = self.data

        resultado = calcular_shapley(data)

        return resultado

    def heuristicos(self, ventana=30, touchpoints=8):

        if self.formateada == False:
            parametros = {
                'ventana' : ventana,
                'touchpoints' : touchpoints,
            }
            print("Validados los parametros")
            data = formatear_shapley(self.data, parametros)
        
        else:
            data = self.data

        resultado = calcular_heuristicos(data)

        return resultado

    def comparacion(self):
        pass


