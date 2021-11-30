# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 16:31:27 2021

@author: nkdi
"""

def load_packaged_model(model_file):
    import os
    import pickle
    # this_dir = os.getcwd()
    name,extension = os.path.splitext(model_file)
    if not extension:
        extension = '.sav'
    model_file = name + extension
    try:
        this_dir, this_filename = os.path.split(__file__)  # Get path of .pkl file
    except:
        this_dir = os.getcwd()
    data_path = os.path.join(this_dir, model_file)
    model = pickle.load(open(data_path, 'rb'))
    return model