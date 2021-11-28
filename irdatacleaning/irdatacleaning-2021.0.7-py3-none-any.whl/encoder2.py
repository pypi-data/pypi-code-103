import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from .stringtodatetime import StringToDateTime
from .inconsistent_data import InconsistentData
class Encoder:
    def __init__(self,df,type = "", columns = []):
        ''' this class is dessigned to help you make encoding your data simple
        the input variables for this class are
        df: a pandas dataframe
        type: by defalult this variable will br set to ONEHOTENCODER if you with to use
        OrdinalEncoder you would set type to ordinalencoder
        then you can call the check method to make the corretions
        this method will return a pandas data frame
        if you wish to compare the returned value to the original dataset you may
        call copy'''
        self.df = df
        self.copy = df.copy()
        self.type = type
        self.columns = columns
        datetime = StringToDateTime(self.df)
        self.df = datetime.check()
        correcting = InconsistentData(self.df)
        correcting.column_names_white_space()
        self.df = correcting.data_white_space()

    def check(self):
        if (len(self.columns)==0):
            self.object_column = []
            for i in self.df.columns:
                if (self.df[i].dtype == "object"):
                    self.object_column.append(i)
        else:
            self.object_column = [i for i in self.columns]
        self.Correct()
        return self.df
    def Correct(self):
        if (self.type == "" or self.type.upper() == "ONEHOTENCODER"):
            self.OneHotEncoder()
        elif (self.type.upper() == "ORDINALENCODER"):
            self.OrdinalEncoder()
    def OrdinalEncoder(self):
        for i in self.object_column:
            translate = OrdinalEncoder()
            final = translate.fit_transform(self.df[i].array.reshape(-1, 1))
            self.df.drop(columns=i, inplace=True)
            self.df[i] = final

    def OneHotEncoder(self):
        for i in self.object_column:
            new_df = pd.get_dummies(self.df[i])
            self.new_df = pd.concat([self.df,new_df],axis=1)
        self.new_df.drop(columns=self.object_column,inplace=True)
        self.df = self.new_df



if __name__ == "__main__":
    import pandas as pd

    data = pd.read_csv("/Users/williammckeon/Sync/youtube videos/novembers 2021/Parsing data/code/travel_times.csv")
    # data = pd.read_csv('https://raw.githubusercontent.com/jldbc/coffee-quality-database/master/data/arabica_data_cleaned.csv')
    # data = pd.read_csv("travel_times.csv")
    print(type(data))
    stringtodate = Encoder(df=data)
    data = stringtodate.check()
    print(data.dtypes)
    # print(stringtodate.new_df.columns)
