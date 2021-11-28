import pandas as pd

class NeedsToBeADict(Exception):
    pass
class NeedsToBeAPandasDataFrame(Exception):
    pass
class InconsistentData:
    def __init__(self, df):
        '''this class is dessigned to help you in the process of correcting inconsitent data
        you have the ability to use use,
        seperatingwords(origin,change):
        this method is created so that you will be able to make sure all the columns
        names with more then one word is seperated correctly
        origin is the original format used to seperate the words
        change is the format you would like to be used to seperate words
        changeing_column_cases(case = "title")
        this method is used to correct the columns nanes so that they are all in
        full caps, full lower, or title case
        case will be used to tell the method what case you would like
        by defalut case will be set equal to title but by saying
        case = upper the column names will be put to full lower
        and the same for case = upper
        column_names_white_space():
        this method will be used to correct white space in column names
        data_white_space():
        this method will be used to correct white space in the dataset
        correcting(column_name, corrections ):
        this method is dessigned to help you make the needed changes to the data in the cells
        so that your data is more consistent
        column_name is the var used to identify which column will get the corrections
        corrections is the dictionary with the corrected valuescheck(seperatingwords = False, origin = "", corrections = "" , change_case = False,case = "title", correcting = False, column_name = "", cell_corrections=None):
        this methode is designed to automate all the steps. needed except you will have to provide some
        input arguments
        first is seperatingwords by defalut is false when you set this to true you will be calling the
        seperatingwords words method
        therefore you will have to add what the origin is set equal
        as well as corrections these will both be some kind string values
        next input value will be case

        change_case = False to be able to have all your column names changed to the same case you will want change the value of change_case to true
        case = "title"
        you can change this depending on how you would like to formate your column names
        when you want to correct specifica values in the data you will set correcting to true as well as
        column_name = to the column name that will get these corrections done
        then
        cell_corrections = to a dictionary
        the corrected pandas data frame will be return
        autocheck():
        does the same as what check does but walks you through the proccess of making all the changes
        resources():
        a method dessigned to give you links for more information on the class'''

        if (isinstance(df, pd.core.frame.DataFrame)):
            self.df = df
            self.copy_df = df.copy
        else:
            raise NeedsToBeAPandasDataFrame(self.df)

    def seperatingwords(self,origin, change):
        '''this method is created so that you will be able to make sure all the columns
        names with more then one word is seperated correctly
        origin is the original format used to seperate the words
        change is the format you would like to be used to seperate words'''
        for i in self.df.columns:
            if origin in i:
                self.df.rename(columns = {i:i.replace(origin,change)}, inplace = True )
        return self.df
    def changeing_column_cases(self, case = "title"):
        '''this method is used to correct the columns nanes so that they are all in
        full caps, full lower, or title case
        case will be used to tell the method what case you would like
        by defalut case will be set equal to title but by saying
        case = upper the column names will be put to full lower
        and the same for case = upper'''
        for i in self.df.columns:
            if (case.lower() == "title"):
                self.df.rename(columns = {i:i.title()}, inplace = True )
            if (case.lower() == "upper"):
                self.df.rename(columns = {i:i.upper()}, inplace = True )
            if (case.lower() == "lower"):
                self.df.rename(columns = {i:i.lower()}, inplace = True )
        return self.df
    def column_names_white_space(self):
        '''this method will be used to correct white space in column names'''

        for i in self.df.columns:
            self.df.rename(columns = {i:i.strip()}, inplace = True )
        return self.df
    def data_white_space(self):
        '''this method will be used to correct white space in the dataset'''

        for i in self.df.columns:
            if self.df[i].dtype == "O":
                for j in self.df[i]:
                    try:
                        self.df[i].replace(to_replace={j:j.strip()}, inplace=True)
                    except AttributeError:
                        pass
        return self.df
    def correcting(self, column_name, corrections ):
        '''this method is dessigned to help you make the needed changes to the data in the cells
        so that your data is more consistent
        column_name is the var used to identify which column will get the corrections
        corrections is the dictionary with the corrected values'''

        if isinstance(corrections,dict):
            self.df.replace(to_replace=corrections, inplace=True)
        else:
            raise NeedsToBeADict
        return self.df
    def check(self, seperatingwords = False, origin = "", corrections = "" , change_case = False,case = "title", correcting = False, column_name = "", cell_corrections=None):
        '''this methode is designed to automate all the steps. needed except you will have to provide some
        input arguments
        first is seperatingwords by defalut is false when you set this to true you will be calling the
        seperatingwords words method
        therefore you will have to add what the origin is set equal
        as well as corrections these will both be some kind string values
        next input value will be case

        change_case = False to be able to have all your column names changed to the same case you will want change the value of change_case to true
        case = "title"
        you can change this depending on how you would like to formate your column names
        when you want to correct specifica values in the data you will set correcting to true as well as
        column_name = to the column name that will get these corrections done
        then
        cell_corrections = to a dictionary
        the corrected pandas data frame will be return'''
        if seperatingwords:
            self.seperatingwords(origin = origin,change = corrections)
        if change_case:
            self.changeing_column_cases(case)
        self.column_names_white_space()
        self.data_white_space()
        if correcting:
            self.correcting(column_name = column_name, corrections = cell_corrections)
        return self.df
    def autocheck(self):
        '''this method with automate every step of this class'''
        for i in self.df.columns:
            print(i)
        print("these are the names of all your columns")
        user = input("enter yes if you would like to correct the ways the words are seperated")
        if user.upper() == "YES":
            origin = input("enter the original format of the names you would like to change")
            corrections = input("how would you like the format to be")
            self.seperatingwords(origin = origin, change =corrections)
        user = input("enter yes if you would like to have all the column names the same")
        if user.upper() == "YES":
            case = input("enter upper to have all the column names to be full upper case\n"
                         "enter lower to have all the column names to be full lower case\n"
                         "enter title to have all the column names to be in title case")
            self.changeing_column_cases(case = case)
        self.column_names_white_space()
        print("after all the corrections these are your title names")
        for i in self.df.columns:
            print(i)
        self.data_white_space()
        for i in self.df.columns:
            if self.df[i].dtype == "object":
                print(f"the {i} column is an object type")
                user = input("enter yes if you would like to to view what values are in this column")
                if user.upper() == "YES":
                    print(self.df[i].value_counts())

                    user = input("enter yes if there are some values you wish to correct")
                    if user.upper() == "YES":
                        values = [j for j in self.df[i].value_counts().items()]
                        corrections = {}

                        while user.lower() =="yes" or len(values)!=0:
                            count = 0
                            for i in values:
                                print(f"{count}:{i}")
                                count+=1

                            print("from the list above pick the number corresponding with the value you want to correcct or enter any key to quit")
                            try:
                                origin = int(input(":"))
                                new_choice = input("what would you like this value to be instead")
                                corrections[values[origin]]= new_choice
                                values.pop(origin)
                            except ValueError:
                                break

        return self.df


    def resources(self):
        git = "https://github.com/Islanderrobotics/inconsistent_data"
        youtube = "https://youtu.be/KycIq40BhhI"
        print(f"you can find more resurces on youtube at {youtube}")
        print(f"as well as on git hub at {git}")
