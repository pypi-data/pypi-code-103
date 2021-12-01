#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 10:43:55 2021

@author: ageiges
"""
import numpy as np
import pandas as pd
import xarray as xr


np.random.seed(0)
temperature = 15 + 8 * np.random.randn(2, 2, 3)
precipitation = 10 * np.random.rand(2, 2, 3)
lon = [[-99.83, -99.32], [-99.79, -99.23]]
lat = [[42.25, 42.21], [42.63, 42.59]]
time = pd.date_range("2014-09-06", periods=3)
reference_time = pd.Timestamp("2014-09-05")

#%%
ds = xr.Dataset(
    data_vars=dict(
        temperature=(["x", "y", "time"], temperature),
        precipitation=(["x", "y", "time"], precipitation),
    ),
    coords=dict(
        lon=(["x", "y"], lon),
        lat=(["x", "y"], lat),
        time=time,
        reference_time=reference_time,
    ),
    attrs=dict(description="Weather related data."),
)
ds

#%%
da = xr.DataArray(
    np.random.rand(4, 3),
    [
        ("time", pd.date_range("2000-01-01", periods=4)),
        ("space", ["IA", "IL", "IN"]),
    ],
)


da[:2]

da[0, 0]

da[:, [2, 1]]


def _pack_dimensions(index, **stacked_dims):
    packed_labels = {}
    packed_values = {}
    drop_levels = []
    
    for dim, levels in stacked_dims.items():
        labels = pd.MultiIndex.from_arrays([index.get_level_values(l) for l in levels])
        packed_labels[dim] = labels_u = labels.unique()
        packed_values[dim] = pd.Index(labels_u.get_indexer(labels), name=dim)
        drop_levels.extend(levels)

    return (
        pd.MultiIndex.from_arrays(
            [index.get_level_values(l) for l in index.names.difference(drop_levels)] +
            list(packed_values.values())
        ),
        packed_labels
    )


def to_dataset(data_dict,
               var_data_labels, # with different units
               packed_dimensions, # dependent dimenions
               ):
    
    
    
    pass



#%% test
import datatoolbox as dt
tbs = dt.getTables(dt.find(source='IAMC15_2019_R2').index[:10])
idf = tbs.to_IamDataFrame()
# xda = idf_to_xarray(idf)
stacked_dims= {'pathway': ('model', 'scenario')}

index, labels = _pack_dimensions(idf.index, **stacked_dims)
