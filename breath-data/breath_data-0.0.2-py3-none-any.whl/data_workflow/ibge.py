import pandas as pd

URL = "https://raw.githubusercontent.com/BReATH-Brazilian-Research/breath_data/89047539c6b83ca9791a3cbb4e52106bc0eefa41/module/resources/IBGE_Municipios.csv"

def load_csv():
    return pd.read_csv(URL)