from sklearn.cluster import DBSCAN
from sklearn.neighbors import LocalOutlierFactor as lof

import numpy as np
import pandas as pd 

class STDEV_outlier():
    def __init__(self, data, outlier_column):
        self.data = data
        self.outlier_column = outlier_column
        self.outlier = ''
        self.data_return = ''
        self.lower_limit = .0
        self.upper_limit = .0
        self.standard_dev = .0
        self.mean = .0

    def get_params(self):
        print('-----GLOBAL OUTLIER DETECTION: STANDARD DEVIATION-----')
        print('STDEV model uses an upper limit of (mean + std(data.column)*3)')
        print('and a lower limit of (mean - std(data.column)*3)')
        
    def fit_predict(self):
        # Fit and predict data then return for dbscan
        self.standard_dev = np.std(self.data[self.outlier_column])
        self.mean = np.mean(self.data[self.outlier_column])
        cutoff = self.standard_dev * 3

        self.lower_limit = self.mean - cutoff
        self.upper_limit = self.mean + cutoff
        # This one finds the values between the upper and lower limits
        self.data_return = self.data.loc[(self.data[self.outlier_column] < self.upper_limit) & 
                                         (self.data[self.outlier_column] > self.lower_limit)]
        # This one finds the values above the upper limit and below the lower limits
        # Note: odds are, there won't be any below the limit because it will most likely
        # be below 0 and we cannot have inventory less than 0 and price less than 0
        self.outlier = self.data.loc[(self.data[self.outlier_column] > self.upper_limit) | 
                                           (self.data[self.outlier_column] < self.lower_limit)]
        return self.data_return
       
    def return_model_(self):
        print('-----GLOBAL OUTLIER DETECTION: STANDARD DEVIATION-----')
        print('Upper Limit: {}\t\t Lower Limit: {}'.format(round(self.upper_limit,4),round(self.lower_limit,4)))
        print('Standard Deviation: {}'.format(round(self.standard_dev,4)))
        print('Mean: {}'.format(round(self.mean,4)))

    def return_outliers_(self):
        self.outlier['detected_in'] = 'STDEV'
        return self.outlier

class DBSCAN_outlier():
    def __init__(self, data, outlier_column,group_column,dbscan_params):
        self.data = data
        self.outlier_column = outlier_column
        self.outliers = pd.Series()
        self.data_return = pd.Series()
        self.model:object
        self.params = dbscan_params
        self.group_column = group_column

    def get_params(self):
        print('\n--------GLOBAL OUTLIER DETECTION: DBSCAN--------')
        for key in self.params.keys():
            print(key)
    
    def build_model(self):
        #print('values ',self.params['metric'],self.params['eps'],self.params['min_samples'],self.params['n_jobs'])
        try:
            self.model = DBSCAN(metric = self.params['metric'],
            eps = self.params['eps'], 
            min_samples = self.params['min_samples'],
            n_jobs = self.params['n_jobs'])
        except:
            error = 'Please input the correct values in the dictionary:\neps, metric, min_samples, n_jobs'
            raise TypeError(error)
        
    def fit_predict(self):
        self.build_model()
        # if self.group_colum != None loop through the values in the group column
        if self.group_column != None:
            for value in self.data[self.group_column].drop_duplicates():
                data = self.data.loc[self.data[self.group_column] == value]
                if len(data) == 1:
                    continue
                else:
                    x = np.array(data[self.outlier_column]).reshape(-1,1)
                    data['result'] = pd.Series(self.model.fit_predict(x))

                    self.data_return = pd.concat([data.loc[data.result == 1],self.data_return])
                    self.outliers = pd.concat([self.outliers,data.loc[data.result == -1]])
        else:
            x = np.array(self.data[self.outlier_column]).reshape(-1,1)
            self.data['result'] = pd.Series(self.model.fit_predict(x))

            self.data_return = pd.concat([self.data.loc[self.data.result == 1],self.data_return])
            self.outliers = pd.concat([self.outliers,self.data.loc[(self.data.result == -1)]])
        return self.data_return.drop_duplicates()

    def return_model_(self):
        if self.group_column == None:
            print('-----GLOBAL OUTLIER DETECTION: DBSCAN-----')
            for key in self.params.keys():
                print('{} = {}'.format(key,self.params[key]))
            return self.model
        else:
            print('Sorry, due to the various models we had to build for')
            print('the group_column, we are unable to return the model')

    def return_outliers_(self):
        self.outliers['detected_in'] = 'DBSCAN'
        return self.outliers

class LOF_outlier():
    def __init__(self, data, outlier_column,group_column,lof_params):
        self.data = data
        self.outlier_column = outlier_column
        self.outliers = pd.Series()
        self.data_return = pd.Series()
        self.model:object
        self.params = lof_params
        self.group_column = group_column
    
    def get_params(self):
        print('-----GLOBAL OUTLIER DETECTION: Local Outlier Factor-----')
        for key in self.params.keys():
            print(key)
    
    def build_model(self):
        try:
            self.model = lof(n_neighbors= self.params['n_neighbors'],
                                metric = self.params['metric'],
                                p = self.params['p'],
                                n_jobs = self.params['n_jobs']
                                )
        except:
            error = 'Please input the correct values in the dictionary:\np,n_jobs,metric,n_neighbors'
            raise TypeError(error)
        
    def fit_predict(self):
        self.build_model()
        # if self.group_colum != None loop through the values in the group column
        if self.group_column != None:
            for value in self.data[self.group_column].drop_duplicates():
                data = self.data.loc[self.data[self.group_column] == value]
                if len(data) == 1:
                    continue
                else:
                    x = np.array(data[self.outlier_column]).reshape(-1,1)
                    data['result'] = pd.Series(self.model.fit_predict(x))

                    self.data_return = pd.concat([data.loc[data.result == 1],self.data_return])
                    self.outliers = pd.concat([self.outliers,data.loc[(data.result == -1)]])
        else:
            x = np.array(self.data[self.outlier_column]).reshape(-1,1)
            self.data['result'] = pd.Series(self.model.fit_predict(x))

            self.data_return = pd.concat([self.data.loc[self.data.result == 1],self.data_return])
            self.outliers = pd.concat([self.outliers,self.data.loc[(self.data.result == -1)]])
        return self.data_return.drop_duplicates()

    def return_model_(self):
        if self.group_column == None:
            print('-----GLOBAL OUTLIER DETECTION: Local Outlier Factor-----')
            for key in self.params.keys():
                print('{} = {}'.format(key,self.params[key]))
            return self.model
        else:
            print('Sorry, due to the various models we had to build for')
            print('the group_column, we are unable to return the model')

    def return_outliers_(self):
        self.outliers['detected_in'] = 'LOF'
        return self.outliers

class Outlier_Analysis():
    def __init__(self,data,outlier_column,group_column = None,
                 dbscan_params = {'eps':0.1,'metric':'euclidean','min_samples':5,'n_jobs':-1},
                 lof_params = {'n_neighbors':1, 'metric':'l1','p':2,'n_jobs': -1}):
        self.data = data
        self.outlier_column = outlier_column
        self.outliers = ''
        self.group_column = group_column
        self.dbscan = DBSCAN_outlier(self.data,self.outlier_column,self.group_column,dbscan_params)
        self.lof = LOF_outlier(self.data,self.outlier_column,self.group_column,lof_params)
        self.stdev = STDEV_outlier(self.data,self.outlier_column)
        ######################################################
        # Error Handling Secion
        ######################################################
        # Check for correct input type
        if (type(lof_params) != dict):
            raise TypeError('lof_params needs to be type "dict", you had type {}'.format(type(lof_params)))
        if (type(dbscan_params) != dict):
            raise TypeError('dbscan_params needs to be type "dict", you had type {}'.format(type(dbscan_params)))
        # Check to make sure dbscan has all the correct parameters
        try:
            for param in ['eps','metric','min_samples','n_jobs']:
                dbscan_params[param]
        except:
            error = 'You must include all parameters if you wish to do a custom model: eps, metric, min_samples, n_jobs'
            raise ValueError(error)
        # Check lof params for all the correct parameters
        try:
            for param in ['n_neighbors','metric','p','n_jobs']:
                lof_params[param]
        except:
            error = 'You must include all parameters if you wish to do a custom model: n_neighbors, metric, p, n_jobs'
            raise ValueError(error)
        # Check to make sure columns passed in are within the dataset
        if self.group_column != None:
            if not(pd.Series(self.group_column).isin(self.data.columns)[0]):
               error =  'Make sure your group column is in your dataset'
               raise KeyError(error)

        if not(pd.Series(self.outlier_column).isin(self.data.columns)[0]):
            error = 'Make sure the outlier column is in your dataset'
            raise KeyError(error)
        # Make sure the data doesn't contain any NAs or missing values
        if pd.Series(self.outlier_column).isin(self.data.columns)[0]:
            if pd.Series([True]).isin(self.data[self.outlier_column].isna())[0]:
                error = 'Drop any MISSING values in the outlier column'
                raise TypeError(error)
                

        
    def get_params(self):
        self.stdev.get_params()
        self.dbscan.get_params()
        self.lof.get_params()

    def fit_general_(self):
        self.data = self.stdev.fit_predict()
        
    def fit_outlier_column_(self):
        self.data = self.dbscan.fit_predict()
    
    def fit_local_cluster_(self):
        self.data = self.lof.fit_predict()
    
    def clean_data(self):
        import warnings
        warnings.filterwarnings("ignore")
        self.fit_general_()
        self.fit_outlier_column_()
        self.fit_local_cluster_()
        self.data = self.data.drop(columns = 0)
        return self.data

    def return_stdev_model(self):
        self.stdev.return_model_()
    
    def return_dbscan_model(self):
        return self.dbscan.return_model_()
    
    def return_lof_model(self):
        return self.lof.return_model_()

    def return_all_models(self):
        self.return_stdev_model()
        print()
        self.return_dbscan_model()
        print()
        self.return_lof_model()

    def save_models(self):
        from joblib import dump
        print('Returned DBSCAN model with parameters:')
        dbscan = self.return_dbscan_model()
        print('\nReturned LOF model with parameters:')
        lof = self.return_lof_model()
        dump(dbscan,'dbscan_model.joblib')
        dump(lof,'lof_model.joblib')

    def return_outlier(self):
        self.outliers = pd.concat([self.stdev.return_outliers_(),self.dbscan.return_outliers_(),self.lof.return_outliers_()])
        return self.outliers
        
        








