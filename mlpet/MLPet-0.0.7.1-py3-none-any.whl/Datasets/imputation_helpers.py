import numpy as np
import pandas as pd
import joblib
import warnings
import os
from . import helpers

from sklearn.experimental import enable_iterative_imputer # necessary for iterative imputer
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import BayesianRidge, LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def _simple_impute(df, cat_original=[], old_new_cols={}):
    """
    Imputes missing values in specified columns with simple imputer

    Args:
        df (pd.DataFrame): dataframe with columns to impute

    Returns:
        pd.DataFrame: dataframe with imputed values
    """
    num_cols, cat_cols = helpers._make_col_dtype_lists(df, old_new_cols, cat_original)

    # Impute numerical columns
    missing_fractions_num          = df[num_cols].isnull().sum()/df.shape[0]
    partially_missing_features_num = missing_fractions_num.loc[missing_fractions_num.values!=1].index.tolist()
    if 'DEPTH' in partially_missing_features_num:
        partially_missing_features_num.remove('DEPTH')
    num_imputer = SimpleImputer(strategy='mean')
    num_imputer.fit(df[partially_missing_features_num])
    df.loc[:, partially_missing_features_num] = pd.DataFrame(
        num_imputer.transform(df[partially_missing_features_num]), 
        columns=partially_missing_features_num
    )    

    # Impute the categorical columns
    missing_fractions_cat          = df[cat_cols].isnull().sum()/df.shape[0]
    partially_missing_features_cat = missing_fractions_cat.loc[missing_fractions_cat.values!=1].index.tolist()
    cat_imputer                    = SimpleImputer(strategy='most_frequent')
    cat_imputer.fit(df[partially_missing_features_cat])
    df.loc[:, partially_missing_features_cat] = pd.DataFrame(
        cat_imputer.transform(df[partially_missing_features_cat]), 
        columns=partially_missing_features_cat
    )    

    return df

def _iterative_impute(df, cat_original=[], old_new_cols={}, imputer=None):
    """
    Imputes missing values in specified columns with iterative imputer

    Args:
        df (pd.DataFrame): dataframe with columns to impute
        imputer (str, optional): imputer method. Defaults to None.

    Returns:
        pd.DataFrame: dataframe with imputed values
    """
    num_cols, _ = helpers._make_col_dtype_lists(df, old_new_cols, cat_original)
    # Iterative imputer at 
    missing_fractions = df[num_cols].isnull().sum()/df.shape[0]
    partially_missing_features = missing_fractions.loc[missing_fractions.values!=1].index.tolist()
    if 'DEPTH' in partially_missing_features:
        partially_missing_features.remove('DEPTH')
    if imputer is None:
        imputer = IterativeImputer(estimator=BayesianRidge())
        imputer.fit(df[partially_missing_features])
    else:
        warnings.warn("Providing an imputer is not implemented yet!")
    df.loc[:, partially_missing_features] = pd.DataFrame(
        imputer.transform(df[partially_missing_features]), 
        columns=partially_missing_features
    )    
    return df

def _generate_imputation_models(df, curves):
    """
    Generates polynomial regression models for curves in dataframe against DEPTH

    Args:
        df (pd.DataFrame): dataframe to get data
        curves (list): list of strings with curves names to generate models

    Returns:
        dict: dictionary with models for each curve based on DEPTH
    """
    imputation_models = {c: {'poly_transform': None, 'model':None} for c in curves}
    
    for c in curves:
        #remove nan values
        df   = df[(df[c].notna()) & (df.DEPTH.notna())]
        # polynomial features and regression fitting
        poly = PolynomialFeatures(3)
        poly.fit(np.array(df.DEPTH.values).reshape(-1, 1))
        depth_poly   = poly.transform(np.array(df.DEPTH.values).reshape(-1, 1))
        linear_model = LinearRegression()
        linear_model.fit(depth_poly, df[c])
        imputation_models[c]['poly_transform'] = poly
        imputation_models[c]['model'] = linear_model
    return imputation_models

def _individual_imputation_models(df, curves, imputation_models):
    """
    Returns individual mdoels if they should be better than a global model.
    We check the percentage of missing data and the spread of actual data with some 
    thresholds to decide if we should use an individual model

    Args:
        df (pd.DataFrame): dataframe with data
        curves (list): list of curves to check
        imputation_models (dict): models given for each curve (usually global models) 

    Returns:
        dict: updated models with curves that would be better with models replaced
    """
    individual_models = []
    for c in curves:
        # if a curve model was not n the given models dicitonary, add it
        if c not in imputation_models.keys():
            individual_models.append(c)
        # also add it if an individual model would be better
        else:
            perc_missing = df[c].isna().mean()
            idx_nona = df[~df[c].isna()].index
            spread = (idx_nona.max()-idx_nona.min())/(df.index.max()-df.index.min())
            if spread>0.7 and perc_missing<0.6:
                individual_models.append(c)
    if len(individual_models)>0:
        individual_models = _generate_imputation_models(df, individual_models)
        #replace global models by individual ones
        imputation_models.update(individual_models)
        return imputation_models
    return imputation_models

def _apply_depth_trend_imputation(df, curves, imputation_models):
    """
    Apply imputation models to impute curves in given dataframe

    Args:
        df (pd.DataFrame): dataframe to which impute values
        curves (list): list of strings
        imputation_models (dict): models for each curve

    Returns:
        pd.DataFrame: dataframe with imputed values based on depth trend
    """
    for c in curves:
        missing = df[(df[c].isna()) & (df.DEPTH.notna())].index
        if len(missing)>0:
            well_data_missing = df.loc[missing, 'DEPTH']
            # impute values with depth trend - linear model
            poly_preds = imputation_models[c]['poly_transform'].transform(
                np.array(well_data_missing.values).reshape(-1, 1)
            )
            poly_preds = imputation_models[c]['model'].predict(poly_preds)
            df.loc[missing, c] = poly_preds  
    return df

def _impute_depth_trend(df, folder_path, mapper, **kwargs):
    """
    Imputation of curves based on polynomial regression models of the curve based on DEPTH

    Args:
        df (pd.DataFrame): df to impute curves

    Keyword Args:
        curves (list): llist of curves to depth impute
        imputation_models (dict): dictionary with curves as keys and the sklearn model as value
        save_imputation_models (bool): whether to sabe the models in the folder_path
        allow_individual_models (bool): whether to allow individual models if seen that it has enough data
        to do so (better performance per well)

    Returns:
        pd.DataFrame: dataframe with curves imputed
    """
    
    curves                  = kwargs.get('curves', None)
    imputation_models       = kwargs.get('imputation_models', None)
    save_imputation_models  = kwargs.get('save_imputation_models', False)
    allow_individual_models = kwargs.get('allow_individual_models', True)  

    if curves is not None:

        # we need to first standardize names
        curves, _ = helpers._standardize_names(curves, mapper)

        # check if depth and all other curves in df
        if not all(c in df.columns for c in curves+['DEPTH']):
            ValueError('Cannot perform depth trend imputation as not all curves are in the dataset.')

        # if imputation models do not exist
        if imputation_models is None:
            # generate models
            imputation_models = _generate_imputation_models(df, curves)
            if save_imputation_models:
                joblib.dump(
                    imputation_models,
                    os.path.join(folder_path, 'imputation_models.joblib')
                )
        else:
            # check if imputation models is provided as a dict with the same format
            if isinstance(imputation_models, dict):
                if not all(c in curves for c in imputation_models.keys()):     
                    if allow_individual_models:
                        warnings.warn("Some provided curves for imputing do not have models. Models will be generated.")
                    else:               
                        raise ValueError(
                            "Curves included in the imputation models dictionary inconsistent with curves to impute",
                            imputation_models.keys(), curves
                        )
            # check if it is preferable to use individual models instead of given global models
            if allow_individual_models:
                imputation_models = _individual_imputation_models(df, curves, imputation_models)

        # apply imputation
        df = _apply_depth_trend_imputation(df, curves, imputation_models)  

    return df       
