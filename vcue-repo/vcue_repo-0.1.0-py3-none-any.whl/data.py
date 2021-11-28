import sys
sys.path.append('../')

import copy
import numpy as np
import pandas as pd


# ~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<
# Order & Aesthetic FUNCTIONS <~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~
# ~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<

def rename(data, oldnames, newname): 
    '''
    Rename variable names in a dataset, returns a dataframe with new names ~ 
    df.columns = ['var1','var2'....'var30']
    df = rename(df, ['var1','var25'], ['name','id'])

    Parameters
    ----------
    data : pandas.DataFrame()
    oldnames : str or list of strs. 
        Name(s) to replace.
    newname : str or list of strs. 
        Name(s) to replace with. If list, must match order of oldnames

    Raises
    ------
    ValueError
        Column not found in dataset.

    Returns
    -------
    data : pandas.DataFrame()
        The dataframe with the renamed columns.

    '''
    if type(oldnames) == str:
        oldnames = [oldnames]
        newname = [newname]
    i = 0 
    for name in oldnames:
        oldvar = [c for c in data.columns if name in c]
        if len(oldvar) == 0: 
            raise ValueError("Sorry, couldn't find "+str(name)+" column in the dataset")
        if len(oldvar) > 1: 
            print("Found multiple columns that matched " + str(name) + " :")
            for c in oldvar:
                print(str(oldvar.index(c)) + ": " + str(c))
            ind = input('please enter the index of the column you would like to rename: ')
            oldvar = oldvar[int(ind)]
        if len(oldvar) == 1:
            oldvar = oldvar[0]
        data = data.rename(columns = {oldvar : newname[i]})
        i += 1 
    return data   


def order(frame, var):
    '''Brings the var to the front of the dataframe. e.g. df = order(df, ['col4','col12'])
    
    - frame : pandas dataframe
    - var : str or list of str. Variables you want to bring to the front. 
    '''
    if type(var) == str:
        var = [var]          
    varlist =[w for w in frame.columns if w not in var]
    frame = frame[var+varlist]
    return frame   



def replace_infs_wmaxmin(dataframe, colname): 
    '''
    Replace the inf and -inf values in a dataframe column with the non-inf max and mins. Returns the dataframe with the column values replaced 

    Parameters
    ----------
    dataframe : pandas.DataFrame().
    colname : str. 

    Returns
    -------
    df : pandas.DataFrame()

    '''
    df = copy.deepcopy(dataframe)
    # replace negative infinity with the non-inf minimum 
    non_inf_min = df[~np.isneginf(df[colname])][colname].min()
    df.loc[np.isneginf(df[colname]), colname] = non_inf_min
    # replace the positive infinity with the non-inf maximum 
    non_inf_max = df[~np.isposinf(df[colname])][colname].min()
    df.loc[np.isposinf(df[colname]), colname] = non_inf_max
    
    return df 

# ~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<
# DATA MANAGEMENT FUNCTIONS <~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~
# ~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<~<

def meatloaf(left, right, left_on, right_on, leftovers='left_only'):
    '''
    Merge two datasets and return the merged and residuals

    Parameters
    ----------
    left : pandas.DataFrame()
    right : pandas.DataFrame()
    left_on : str.
        merge key.
    right_on : str.
        merge key.
    leftovers : str, optional
        which residuals to return. The default is 'left_only'.

    Returns
    -------
    mrg : pandas.DataFrame()
        Merged dataset.
    residuals : pandas.DataFrame()
        Residual dataset.
    '''
    mrg = pd.merge(left, right, left_on=left_on, right_on=right_on, how='outer', indicator=True) # merge the two datasets 
    # print(mrg['_merge'].value_counts())                                          
    residuals = mrg[mrg['_merge']==leftovers][left.columns]                      # get the data that didn't merge 
    mrg = mrg[mrg['_merge']=='both']                                             # keep the data that did merge 
    return mrg, residuals 


def full_value_count(data, col):
    '''Return the value count and percentages'''
    table = pd.merge(
        pd.DataFrame(data[col].value_counts().sort_index()),
        pd.DataFrame(data[col].value_counts().sort_index()/data[col].value_counts().sum()), 
        right_index=True, left_index=True, how='inner')
    table.columns = [col+'_#', col+'_%']
    return table 


def import_full_excel(xl_file):
    '''Returns a dictionary with the sheet names as keys and the data as values
    - xl_file : string. filepath to excel file 
    '''
    xls = pd.ExcelFile(xl_file)

    db = {} 
    for sheet in xls.sheet_names: 
        db[sheet] = pd.read_excel(xls, sheet)    # read in the excel sheets 
        db[sheet] = db[sheet].fillna(0)          # fill in the missing values with 0's 
        for c in db[sheet].columns:              # make numeric fields integers
            try: 
                db[sheet][c] = db[sheet][c].astype(int)
            except: 
                pass
        
    print("Sheet names are: "+", ".join(list(db.keys())))

    return db
