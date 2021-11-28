from encoder2 import Encoder
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
class MissingValues:
    '''MissingValues is dessigned to make correcting missing values alot more accesable.
    MissingValues(df)
    df: is the inputted pandas dataframe what will have corrections made to it
    check is the method used to tell the module to start the corrections, this method will return the corrected dataframe
    if you wish to get the original dataframe call the copy variable.
    currently you are only able to use the median stratagy however other methods are in the work'''
    def __init__(self, df, strategy = ["median"], columns = [], columns_drop = [],
                 columns_fill =[],whole_df = False, fill_with = 0, round = True):
        # data = Encoder(df = df)
        # self.df = data.check()
        self.df = df
        # print(self.df.dtypes)
        self.strategy = strategy
        self.columns = columns
        self.whole_df = whole_df
        self.np_df = self.df.iloc[:,:].values
        self.fill_with = fill_with
        self.column_location = {}
        self.round = round
        self.columns_drop = columns_drop
        self.columns_fill = columns_fill
    def check(self):
        self.column_location = {}
        count = 0
        for i in self.columns:
            self.column_location[i] = count
            count+=1
        for i in self.strategy:
            if i.upper()=="MEDIAN":
                self.median()
                # self.df = pd.DataFrame(self.np_df, columns=self.df.columns)
            elif i.upper()=="FILL":
                self.df.fillna(self.fill_with, inplace = True)
            elif i.upper()=="DROP":
                self.df.dropna(inplace = 0)
        return self.df
    def median(self):
        for i in self.columns:
            for j in range(len(self.np_df[:][self.column_location[i]])):
                print(j)
                if np.isnan(self.np_df[j][self.column_location[i]]):
                    self.np_df[j][self.column_location[i]] = self.np_df[j][self.column_location[i]].mean()
                    # j = round(self.np_df[j][self.column_location[i]].mean())
        # self.isnull = []
        # for i in self.df.columns:
        #     if (self.df[i].isnull().values.any()):
        #         self.isnull.append(i)
        # if (len(self.isnull) >0):
        #     self.Imputer()
        # return self.df
    # def Imputer(self):
    #     imputer = SimpleImputer(strategy="median")
    #     new_data = imputer.fit_transform(self.df)
    #     convert = pd.DataFrame(new_data, columns=self.df.columns,index=self.df.index)
    #     self.df = convert
if __name__ == "__main__":
    import pandas as pd
    from stringtodatetime import StringToDateTime
    data = pd.read_csv("/Users/williammckeon/Sync/youtube videos/novembers 2021/Parsing data/code/travel_times.csv",index_col=0)
    # data = pd.read_csv('https://raw.githubusercontent.com/jldbc/coffee-quality-database/master/data/arabica_data_cleaned.csv')
    # data = pd.read_csv("travel_times.csv")
    # print(type(data))
    print(data.dtypes)
    stringtodate = StringToDateTime(data)
    data = stringtodate.check()
    print(data.info())
    missing = MissingValues(data, columns=["AvgSpeed","FuelEconomy"])
    data = missing.check()

    # for i in data.columns:
    #     print(data[i].count())
    # # print(stringtodate.new_df.columns)