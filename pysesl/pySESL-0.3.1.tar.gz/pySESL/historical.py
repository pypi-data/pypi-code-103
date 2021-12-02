from math import ceil, floor
from typing import Sequence, Union

import numpy as np
import pandas as pd
import xarray as xr
from scipy.linalg import toeplitz


def calc_temp(
    data: xr.Dataset,
    T_err: Union[str, None],
    T_num: int,
    n_samples: int,
    tau_ar1: float = 10,
    random_state: Union[int, None] = 0,
) -> xr.DataArray:
    """Simulate draws of historical temperature time series based on AR1 processes.

    Parameters
    ----------
    data : :class:`xarray.Dataset`
        Output of ``load_data_SESL`` function. Contains mean estimate and standard
        deviation for each year.
    T_err : str or None,
        Approach to simulating the time series using the standard deviation. Currently,
        only ``ar1ts`` is supported:
            - ``ar1ts``: AR(1) Parameter timescale == exp(-abs(t2-t1)/timescale)
            - ``ar1``: T as AR(1) process with sigma as "default"
            - ``default``: T + random noise as in KE11
            - ``no``: Don't add uncertainty
    T_num : int
        Number of simulated time series to create
    n_samples : int
        Number of draws of the parameter posteriors
    tau_ar1 : float, optional
        If ``T_err==ar1ts``, this is the ``timescale`` parameter. Otherwise, ignored.
    random_state : int, optional
        If set, controls the random state for the :function:`numpy.random.default_rng`
        function used to generate time series draws. If None, will result in
        non-deterministic outputs

    Returns
    -------
    :class:`xarray.DataArray`
        Contains ``T_num`` sims of historical annual mean GMST values.
    """
    rng = np.random.default_rng(random_state)
    if T_err == "ar1ts":
        T = data.T
        err_vec = T.sel(kind="err").values
        err_sq = np.expand_dims(err_vec, 1) * np.expand_dims(err_vec, 0)
        yr_vec = T.T_year.values
        yr_vec_neg_diff_norm = -np.abs(
            (np.expand_dims(yr_vec, 1) - np.expand_dims(yr_vec, 0)) / tau_ar1
        )
        cov_ar1 = err_sq * np.exp(yr_vec_neg_diff_norm)
        sims = rng.multivariate_normal(
            T.sel(kind="val"), cov_ar1, size=(T_num, n_samples)
        )
        return xr.DataArray(
            sims.T,
            coords={
                "T_sim_id": np.arange(sims.shape[0]),
                "year": T.T_year.values,
                "sample": np.arange(n_samples),
            },
            dims=["year", "sample", "T_sim_id"],
        )
    elif T_err == "no":
        return data.T.sel(kind="val").rename(T_year="year")
    raise NotImplementedError


def calc_T0(
    T_sims: xr.Dataset,
    historical_data: xr.Dataset,
    params: xr.Dataset,
    optim_T0: bool,
    model: str,
    T0_period_end: int = -1800,
) -> xr.Dataset:
    """Calculate draws of ``T0`` parameter from historical temperature draws.

    Parameters
    ----------
    T_sims : :class:`xarray.Dataset`
        Output of :func:`calc_temp`. Contains draws of historical temps.
    historical_data : :class:`xarray.Dataset`
        Output of :func:`pySESL.io.load_data_SESL`. Contains mean and SDs for temp and
        sea level reconstructions.
    params : :class:`xarray.Dataset`
        Output of :func:`pySESL.io.load_params`. Contains posterior distributions of
        trained SESL model parameters.
    optim_T0 : bool
        Whether to use the optimized T0(0) posterior distribution from ``params``
    model : "CRdecay", "ConstRate", "CRovTau", "TwoTau", or "simpel"
        Which model was used to train SESL model and generate ``params``.
    T0_period_end : int, optional
        Ending year of period used to calculate an initial T0(0). Default -1800.

    Returns
    -------
    :class:`xarray.Dataset`
        Contains the T0 parameter for each year and for each of the sims of historical
        GMST contained in ``T_sims``
    """
    if optim_T0:
        T0_rnd = params.T01
    else:
        T0_rnd = 0
    tau1 = params.tau
    # tau2 = params.tau_c

    n_yrs = len(T_sims.year)

    def toepify(arr):
        return toeplitz(arr, np.concatenate((arr[:1], np.zeros(len(arr) - 1))))

    # if use_Mar_T0 was used
    if "T0burnin" in historical_data.data_vars:
        n_burnin = historical_data.T0burnin.item()
        yrs1 = historical_data.T_year[1].item() - historical_data.T_year[0].item()
        yrs2 = historical_data.T_year[-1].item() - historical_data.T_year[-2].item()
        tau1_1 = tau1 / yrs1
        tau1_2 = tau1 / yrs2
        tau1_ = xr.concat([tau1_1, tau1_2], dim=pd.Index(["T0", "T"], name="T_type"))
        G = ((1 - 1 / tau1_) * xr.ones_like(T_sims.year)) ** xr.DataArray(
            np.arange(n_yrs), dims=["year"]
        )
        G_M = xr.apply_ufunc(
            toepify,
            G,
            input_core_dims=[["year"]],
            output_core_dims=[["year", "year2"]],
            vectorize=True,
        )

        GM_T0 = G_M.sel(T_type="T0").isel(year2=slice(None, n_burnin))
        GM_T = G_M.sel(T_type="T").isel(year2=slice(n_burnin, None))
        G_M1 = xr.concat((GM_T0, GM_T), dim="year2")

        temp_1_T0 = T_sims.isel(year=slice(None, n_burnin)) / tau1_1
        temp_1_T = T_sims.isel(year=slice(n_burnin, None)) / tau1_2
        temp_1 = xr.concat((temp_1_T0, temp_1_T), dim="year")
        temp_1[{"year": 0}] = (
            T_sims.isel(year=(historical_data.T_year <= T0_period_end).values).mean(
                "year"
            )
            + T0_rnd
        )
    else:
        raise NotImplementedError

    if model == "TwoTau":
        raise NotImplementedError

    T01 = xr.dot(G_M1, temp_1.rename(year="year2"), dims=["year2"])
    return T01


def calc_sl(
    T_sims: xr.DataArray,
    T0_sims: xr.DataArray,
    params: xr.Dataset,
    model: str,
    period: Sequence,
    interp_method: str = "nearest",
) -> tuple:
    """Calculate draws of sea level and ``c`` parameter using historical temperature
    draws.

    Parameters
    ----------
    T_sims : :class:`xarray.Dataset`
        Output of :func:`calc_temp`. Contains draws of historical temps.
    T0_sims : :class:`xarray.Dataset`
        Output of :func:`calc_T0`. Contains T0 associated with historical T draws.
    params : :class:`xarray.Dataset`
        Output of :func:`pySESL.io.load_params`. Contains posterior distributions of
        trained SESL model parameters.
    model : "CRdecay", "ConstRate", "CRovTau", "TwoTau", or "simpel"
        Which model was used to train SESL model and generate ``params``.
    period : length-2 array-like
        Period of data to include in results
    interp_method : str, optional
        Interpolation method used to annualize ``T_sims`` and ``T0_sims`` variables.

    Returns
    -------
    sea : :class:`xarray.DataArray`
        Sea Level by year for each parameter sample X temperature reconstruction sample
    dsea : :class:`xarray.DataArray`
        Annual change in sea Level by year for each parameter sample X temperature
        reconstruction sample
    c : :class:`xarray.DataArray`
        Value of ``c`` parameter by year for each parameter sample
    T_sims, T0_sims : :class:`xarray.DataArray`
        Same as the input ``T_sims`` and ``T0_sims`` but interpolated to annual values
        using ``interp_method`` and clipped to range bounded by ``period`` and
        ``calibperiod``
    """

    if model != "CRdecay":
        raise NotImplementedError

    T_sims, T0_sims = resize_T(period, T_sims, T0_sims, interp_method=interp_method)
    g = 1 - 1 / params.tau_c
    G = g ** xr.DataArray(
        np.arange(T_sims.year.size), coords={"year": T_sims.year}, dims=["year"]
    )
    c = params.c * G
    dsea = c + params.a * (T_sims - T0_sims)
    sea = dsea.cumsum("year")

    return sea, dsea, c, T_sims, T0_sims


def resize_T(
    period: Sequence, *das: xr.DataArray, interp_method: str = "nearest"
) -> Sequence:
    """Interpolate DataArrays of values at (potentially varying) time intervals to
    annual time series, and clip them

    Parameters
    ---------
    period : length-2 array-like
        Starting and ending values for desired period of output DataArrays
    interp_method : str, optional
        Interpolation method to use to annualize inputs. Default is "nearest".

    Returns
    -------
    tuple
        Tuple of DataArrays of same length as ``das``, interpolated and clipped
    """

    da = das[0]

    fyr = max(da.year[0].item(), period[0])
    lyr = period[1]

    out_range = da.year.isel(year=(da.year >= fyr) & (da.year <= lyr))
    diffs = out_range.diff("year")
    yrs_st = diffs[0]
    yrs_end = diffs[-1]
    yrs_out = np.arange(
        out_range[0] - floor((yrs_st - 1) / 2),
        out_range[-1] + ceil((yrs_end - 1) / 2) + 1,
    )

    return list(
        map(
            lambda x: x.interp(
                year=yrs_out,
                method=interp_method,
                kwargs={"fill_value": "extrapolate"},
            ),
            das,
        )
    )
