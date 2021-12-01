from itertools import combinations, permutations
from collections import Counter

def calcular_shapley(data):
    '''
    El input es una lista con una lista de recorridos a la conversion.
    El output es la cantidad de conversiones atribuidas a cada canal en los recorridos.
    '''
    
    print("Proceso de calcular Shapley")

    # CONVERSIONES TOTALES
    conversiones_totales = sum(list(map(lambda x: x[1], data)))

    # CANALES UNICOS
    canales_unicos = sorted(set(canal for recorrido in data for canal in recorrido[0] if recorrido[1]==1))

    # COMBINACION EXHAUSTIVA DE CANALES UNICOS (ORDENADOS)
    canales_combinados = combinar(canales_unicos)
    sub_coaliciones = {camino:0 for camino in canales_combinados}

    # GRAN COALICION Y SUS PERMUTACIONES
    gran_coalicion = list(permutations(canales_unicos))

    # TODOS LOS CAMINOS CON CANALES UNICOS ORDENADOS
    recorridos = [tuple(sorted(recorrido[0])) for recorrido in data]

    # ACTUALIZAR VALORES DE LAS SUBCOALICIONES
    sub_coaliciones.update(Counter(recorridos))

    # CALCULAR SHAPLEY
    shapley = valor_shapley(gran_coalicion, sub_coaliciones)

    #  Y APLICAR A CONVERSIONES
    atribucion = {k:round(v*conversiones_totales,2) for k,v in shapley.items()}

    return atribucion

def formatear_shapley(data, parametros):

    for k,v in parametros.items():
        print("Parametros: ",k,v)
    
    print("Proceso de formatear Markov")
    
    return data

def combinar(lista):
    '''
    Pasando una lista de elementos, devuelve una lista con la combinatoria de los elementos, ordenados y no repetidos
    '''    
    # calcular el numero de elementos en la lista
    numero_de_elementos = len(lista)
    
    # crear un rango de 1 al numero de elementos
    rango = range(1,numero_de_elementos+1)
    
    # hacer la combinatoria de los elementos para cada valor del rango
    combinacion = [list(combinations(lista,i)) for i in rango]
    
    # desanidar las listas
    resultado = [tupla for sublist in combinacion for tupla in sublist]
    
    return resultado

def valor_shapley(gran_coalicion, sub_coaliciones):
    conversiones = {}
    for permutacion in gran_coalicion:
        suma = 0
    
        for orden,canal in enumerate(permutacion):
            valor = max(sub_coaliciones[tuple(sorted(permutacion[0:orden+1]))] - suma,0)
            if valor > 0:
                conversiones[canal] = conversiones.get(canal, 0) + valor
                suma += valor

    proporcion = {k:v/sum(conversiones.values()) for k,v in conversiones.items()}

    return proporcion
