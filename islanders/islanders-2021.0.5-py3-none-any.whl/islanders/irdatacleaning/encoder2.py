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
        columns: when you have specific columns you want to be be corrected a specific way
        then import the column or column names to this variable and only those columns will get corrected
        they type you specificed
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
        self.np = self.df.iloc[:,:].values
    def check(self):
        if (len(self.columns)==0):
            self.object_column = []
            for i in self.df.columns:
                if (self.df[i].dtype == "object"):
                    self.object_column.append(i)
        else:
            # print("yes")

            self.object_column = [i for i in self.columns]
        self.Correct()
        # print(self.object_column)
        # print("yes")
        # print(self.df)
        return self.df
    def Correct(self):
        if (self.type == "" or self.type.upper() == "ONEHOTENCODER"):
            self.OneHotEncoder()
        elif (self.type.upper() == "ORDINALENCODER"):
            self.OrdinalEncoder()
    def OrdinalEncoder(self):
        columns = [i for i in self.df.columns]
        for i in self.object_column:
            for j in range(len(self.df.columns)):
                if (columns[j] == i):
                    translate = OrdinalEncoder()
                    final = translate.fit_transform(self.np[i].reshape(-1, 1))
                    self.df.drop(columns=i, inplace=True)
                    self.df[i] = final

    def OneHotEncoder(self):
        for i in self.object_column:
            new_df = pd.get_dummies(self.df[i])
            for  j in new_df.columns:
                self.df[j] = new_df[j]
        self.df.drop(columns=self.object_column,inplace=True)




if __name__ == "__main__":
    import pandas as pd

    data = pd.read_csv("/Users/williammckeon/Sync/youtube videos/novembers 2021/Parsing data/code/travel_times.csv")
    # data = pd.read_csv('https://raw.githubusercontent.com/jldbc/coffee-quality-database/master/data/arabica_data_cleaned.csv')
    # data = pd.read_csv("travel_times.csv")
    # print(type(data))
    import  irdatacleaning

    stringtodate = Encoder(df=data, columns = ["DayOfWeek"])
    data = stringtodate.check()
    # print(data.info())
    print(data.info())
    # print(stringtodate.new_df.columns)
