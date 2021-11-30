import pandas as pd
import numpy as np


# In[1960]:


# Esqueleto de la función. Llama a las otras funciones para cada tarea
def approve(data, cond):
    col_name = []
    col_name_total = []

    # Chequeamos columnas y examenes
    status = check(list(data), cond)
    print(status)
    if status == 'error':
        print('Tests and columns do not match')
        return
    
    # Iteramos por el dict de configuración
    for key, value1 in cond.items():
    
        #Si entre los elementos encontramos un dict (que seria los grupos de examenes)
        # Analizamos sus valores
        if type(value1) is dict:
            group_keys = list(value1.keys())
            group_items = [value1[x] for x in group_keys]
            # Se le agrega el _ porque si no hay recuperatorio, queda con el mismo nombre de la col original
            col_name = ' '.join(group_keys) + '_' 
            col_name_total.append(col_name)
            data[col_name] = data.apply(lambda x: calc(x[group_keys], group_items, group_keys), axis =1)

    data['final_mark'] = data.apply(lambda x: final_mark(x[col_name_total]), axis = 1)
    data.drop(col_name_total, inplace=True, axis=1)

    
# Controla que los campos de la configuración estén en la base cargada
def check(columns, cond):
    # Creamos una lista con todas las lleves de último nivel del dict
    keys = set([ name for groups
            in cond.values() for name in groups.keys() ])
    col = set(columns)  
    check =  all(item in col for item in keys)

    if check is True:
        print("The list {} contains all elements of the list {}".format(keys, col))    
        return 'ok'
    else:
        return 'error'
    
# Calcula las notas mas alta para cada instancia, o si está desaprobado, devuelve NULL    
def calc(value, passed, keys):
    value = value.tolist()
    for value,passed,keys in zip(value,passed, keys):
        if value < passed:
            pass
        elif value >= passed:
            return value

# Calcula la situación final del alumno
def final_mark(dataset):
    if (dataset.isna()).any():
        return 'Failed'
    else:
        return dataset.mean()

