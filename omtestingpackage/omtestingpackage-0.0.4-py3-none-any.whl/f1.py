import pandas as pd

def add(x,y):
    return x + y

def subtract(x,y):
    return x - y
    
def dep_test():
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    return df