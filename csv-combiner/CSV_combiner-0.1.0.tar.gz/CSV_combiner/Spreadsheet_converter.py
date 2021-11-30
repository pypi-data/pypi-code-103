from pandas import read_excel
class sheet_converter :
    def __init__(self) :
        """okay"""
        pass
    def converter(source) :
        df = read_excel(source, sheet_name=None)
        df[list(df.keys())[0]].to_csv(source +".csv" ,index = False)
           