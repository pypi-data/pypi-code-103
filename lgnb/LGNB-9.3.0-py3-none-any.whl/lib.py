#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   lib.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/14 16:55   wangcc     1.0         None

module for quick numpy calculation
includings: ts_mean, ts_sum, ts_std, ts_argmin, ts_argmax, ts_rank, ts_min
            ts_max, ts_decayl, ts_return, ts_zscore, ts_cov, ts_corr
'''

# import lib
import numpy as np
import numba as nb
import bottleneck as bn


def ts_mean(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_mean(mat, window, min_count=min_periods, axis=0)


def ts_sum(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_sum(mat, window, min_count=min_periods, axis=0)


def ts_std(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_std(mat, window, min_count=min_periods, axis=0)


def ts_argmin(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_argmin(mat, window, min_count=min_periods, axis=0)


def ts_argmax(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_argmax(mat, window, min_count=min_periods, axis=0)


def ts_rank(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_rank(mat, window, min_count=min_periods, axis=0)


def ts_min(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_min(mat, window, min_count=min_periods, axis=0)


def ts_max(mat, window, min_periods):
    if mat.shape[0] < window:
        return np.full_like(mat, np.nan)
    return bn.move_max(mat, window, min_count=min_periods, axis=0)


@nb.jit(nopython=True)
def ts_decayl(mat, window, min_periods):
    w = np.ones((window,), dtype=np.float64).cumsum()
    tmp = np.full_like(mat, np.nan)
    nrow, ncol = tmp.shape
    for i in range(window, nrow):
        for j in range(ncol):
            arr = mat[i - window:i, j]
            mask = ~np.isnan(arr)
            if np.sum(mask) > min_periods:
                tmp[i, j] = np.dot(w[mask], arr[mask]) / np.sum(w[mask])
    return tmp


@nb.jit(nopython=True)
def ts_return(mat, window, min_periods):
    tmp = np.full_like(mat, np.nan)
    nrow, ncol = tmp.shape
    for i in range(window, nrow):
        for j in range(ncol):
            arr = mat[i - window:i, j]
            mask = ~np.isnan(arr)
            if np.sum(mask) > min_periods:
                arr = arr[mask]
                arr[0] = np.nan if arr[0] == 0 else arr[0]
                tmp[i, j] = arr[-1] / arr[0] - 1
    return tmp


def ts_zscore(mat, window, min_periods):
    mean = ts_mean(mat, window, min_periods)
    std = ts_std(mat, window, min_periods)
    mask = std == 0
    std[mask] = np.nan
    output = (mat - mean) / std
    output[mask] = 0
    return output


@nb.jit(nopython=True)
def ts_cov(mat, window, min_periods):
    nrow, ncol = mat.shape
    tmp = np.full((nrow, int(ncol * (ncol - 1) / 2)), np.nan)
    for i in range(window - 1, nrow):
        cov_loc = 0
        for j in range(ncol):
            for k in range(ncol):
                if k > j:
                    arr_j = mat[i - window + 1:i + 1, j]
                    arr_k = mat[i - window + 1:i + 1, k]
                    mask = ~(np.isnan(arr_j) | np.isnan(arr_k))
                    arr_j = arr_j[mask]
                    arr_k = arr_k[mask]
                    nval = np.sum(mask)
                    if nval > min_periods:
                        if (np.std(arr_j) * np.std(arr_k)) == 0:
                            tmp[i, cov_loc] = 0
                        else:
                            tmp[i, cov_loc] = np.dot(
                                arr_j - np.mean(arr_j), arr_k - np.mean(arr_k)
                            ) / nval
                    cov_loc += 1
    return tmp


@nb.jit(nopython=True)
def ts_corr(mat, window, min_periods):
    nrow, ncol = mat.shape
    tmp = np.full((nrow, int(ncol * (ncol - 1) / 2)), np.nan)
    for i in range(window - 1, nrow):
        cov_loc = 0
        for j in range(ncol):
            for k in range(ncol):
                if k > j:
                    arr_j = mat[i - window + 1:i + 1, j]
                    arr_k = mat[i - window + 1:i + 1, k]
                    mask = ~(np.isnan(arr_j) | np.isnan(arr_k))
                    arr_j = arr_j[mask]
                    arr_k = arr_k[mask]
                    nval = np.sum(mask)
                    if nval > min_periods:
                        value = np.dot(
                            arr_j - np.mean(arr_j), arr_k - np.mean(arr_k)
                        )
                        domi = (nval * np.std(arr_j) * np.std(arr_k))
                        if domi == 0:
                            tmp[i, cov_loc] = 0
                        else:
                            tmp[i, cov_loc] = value / domi
                    cov_loc += 1
    return tmp