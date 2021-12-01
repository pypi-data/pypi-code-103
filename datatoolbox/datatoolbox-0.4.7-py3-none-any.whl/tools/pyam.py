#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 09:14:25 2021

@author: ageiges
"""
import pyam
import pandas as pd
import xarray as xr

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


def idf_to_xarray(s, **stacked_dims):
    """
    Convert multiindex series or pyam dataframe to xarray
    """
    
    
    if isinstance(s, pyam.IamDataFrame):
         # meta
        meta_dims = dict(pathway=("model", "scenario"))
        index, labels = _pack_dimensions(s.meta.index, **meta_dims)
        x_meta = xr.DataArray(s.meta).rename({'dim_0':'pathway',
                                      'dim_1': 'meta'}).assign_coords(labels)
        # data
        s = s._data
    
    if not stacked_dims:
        stacked_dims = dict(pathway=("model", "scenario"), varunit=("variable", "unit"))

    index, labels = _pack_dimensions(s.index, **stacked_dims)
    
    return xr.DataArray.from_series(s.set_axis(index)).assign_coords(labels).assign_attrs({'iamc_meta' : x_meta})

def pd_long_to_xarray(s, **stacked_dims):
    """
    Convert multiindex series or pyam dataframe to xarray
    """
    
    
    if isinstance(s, pyam.IamDataFrame):
         # meta
        meta_dims = dict(pathway=("model", "scenario"))
        index, labels = _pack_dimensions(s.meta.index, **meta_dims)
        x_meta = xr.DataArray(s.meta).rename({'dim_0':'pathway',
                                      'dim_1': 'meta'}).assign_coords(labels)
        # data
        # s = s._data
    
    if not stacked_dims:
        stacked_dims = dict(pathway=("model", "scenario"), varunit=("variable", "unit"))

    index, labels = _pack_dimensions(s.index, **stacked_dims)
    
    return xr.DataArray.from_series(s.set_axis(index)).assign_coords(labels).assign_attrs({'iamc_meta' : x_meta})


import datatoolbox as dt
tbs = dt.getTables(dt.find().index[:10])
idf = tbs.to_IamDataFrame()
xda = idf_to_xarray(idf)
# labels
# tbs.xda


#%%
tbs = dt.getTables(dt.find(entity='Emissions|CO2').index[:10])
xds = xr.Dataset()
stacked_dims= {'pathway': ('model', 'scenario')}
for var in tbs.variables():
    idf = tbs.filter(variable=var).to_LongTable().set_index(['variable','scenario','model', 'region'])
    xds[var] = pd_long_to_xarray(idf, **stacked_dims)
