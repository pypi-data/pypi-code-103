import pandas as pd
def datasets(name):
    '''this medoul is dessigned to allow you to download datasets that where created from the islander community'''
    datasets = {}
    datasets["titanic"] = "https://raw.githubusercontent.com/Islanderrobotics/titanic/master/titanic.csv"
    datasets["titanic.csv"] = datasets["titanic"]
    datasets["amazon electronics"] = "https://raw.githubusercontent.com/Islanderrobotics/islander-datasets/master/amazon%20electronics.csv"
    datasets["amazon electronics.csv"] = datasets["amazon electronics"]
    return pd.read_csv(datasets[name.lower()], index_col=0)