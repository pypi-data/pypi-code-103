from pathlib import Path
from typing import Sequence, Union

import numpy as np
import pandas as pd
import xarray as xr
from scipy.io import loadmat


def load_data_SESL(
    sl_fpath: Union[str, Path],
    T_fpath: Union[str, Path],
    use_cov: bool,
    use_Mar_T0: bool,
    Mar_fpath: Union[str, Path, None] = None,
    T_err_sc: float = 1,
    cov_tau: float = 100,
    no_neg_cov: bool = True,
    baseperiod: Sequence[int] = [1400, 1800],
    T0_temp_level: float = 100,
    T0_period_st: int = -2000,
) -> xr.Dataset:
    """Load historical temperature and sea level reconstructions

    Parameters
    ----------
    sl_fpath : str or :class:`pathlib.Path`
        Path to sea level reconstruction input ``.mat`` file.
    T_fpath : str or :class:`pathlib.Path`
        Path to temperature reconstruction input ``.mat`` file.
    use_cov : bool
        If True, use covariance matrix of SL reconstruction data (if existing) to
        estimate likelihood of parameter set.
    use_Mar_T0 : bool
        If True, use Marcott long-running temperature reconstruction to calculate ``T0``
        value until reconstruction at ``T_fpath`` starts.
    Mar_fpath : str or :class:`pathlib.Path` or None, optional
        Path to Marcott sea level reconstruction input ``.mat`` file. Only used if
        ``use_Mar_T0`` is True.
    T_err_sc : float, optional
        Scaling factor for temperature error uncertainty.
    cov_tau : float, optional
        Time scale for covariance. If not null, take the elementwise product of the
        covariance and a tapering function exp(-delta(t)/cov_tau). Only used if
        ``use_cov`` is True.
    no_neg_cov : bool, optional
        Bound covariance matrix to be non-negative. Default True.
    baseperiod : array-like, optional
        Reference period used for sea level data. Data are normed to have 0 mean over
        this period. Default [1400, 1800].
    T0_temp_level : int, optional
        If ``use_Mar_T0`` is True, number of years over which to harmonize the mean of
        the Marcott T time series and time series at ``T_fpath`` in order to calculate
        T0 from Marcott.
    T0_period_st : int, optional
        Starting year of period used to calculate an initial T0(0).

    Returns
    -------
    :class:`xarray.Dataset`
        Contains the processed estimated value and error for the temperature
        reconstruction at ``T_fpath``, the sea level reconstruction at ``sl_fpath``, and
        the derived T0 timeseries using ``sl_fpath`` and (optionally) the long-running
        Marcott reconstruction
    """

    # load SL proxy data
    sl_data = loadmat(sl_fpath, squeeze_me=True)
    sl = sl_data["sl"]
    proxy_sl = pd.DataFrame(
        {
            "val": (sl[:, 1] / 10).astype(np.float64),
            "err": (sl[:, 2] / 10).astype(np.float64),
        },
        index=pd.Index(sl[:, 0].astype(np.int16), name="year"),
    )
    C = (sl_data["C"] / 100).astype(np.float64)
    C += np.eye(len(C)) * np.finfo(C.dtype).eps

    if use_cov:
        if cov_tau is not None:
            Csc = np.exp(
                -np.abs(
                    np.expand_dims(proxy_sl.index.values, 0)
                    - np.expand_dims(proxy_sl.index.values, 1)
                )
                / cov_tau
            )
            C *= Csc
        else:
            raise NotImplementedError
        if no_neg_cov:
            C = np.maximum(C, 0)

    # rebase proxy SL data to base period
    proxy_sl["val"] -= proxy_sl.loc[baseperiod[0] : baseperiod[1], "val"].mean()

    # convert to long format
    proxy_sl = proxy_sl.stack()
    proxy_sl.index = proxy_sl.index.rename("kind", level=-1)
    proxy_sl.name = "sl"

    # load T reconstruction data
    T = loadmat(T_fpath, squeeze_me=True)["T"]
    T = pd.DataFrame(
        T[:, 1:3],
        columns=["val", "err"],
        index=pd.Index(T[:, 0], name="year").astype(np.int16),
    )

    # assert common timestep
    dyr = np.diff(T.index)
    assert len(np.unique(dyr)) == 1
    dyr = dyr[0]

    # scale by predefined scaling factor
    T["err"] *= T_err_sc

    # convert to long format
    T_long = T.stack()
    T_long.index = T_long.index.rename("kind", level=-1)
    T_long.name = "T"

    # aggregate into Dataset
    data = xr.merge(
        (
            proxy_sl.to_xarray().rename(year="sl_year"),
            T_long.to_xarray().rename(year="T_year"),
        )
    )

    # Use Mar data for early T values if using for initializing T0
    if use_Mar_T0:
        T_mar = loadmat(Mar_fpath)["T"]
        T_mar = pd.DataFrame(
            T_mar[:, 1:],
            columns=["val", "err"],
            index=pd.Index(T_mar[:, 0], name="year").astype(np.int16),
        )
        T_mar_overlap_mean = T_mar.loc[
            T.index.min() : T.index.min() + T0_temp_level, "val"
        ].mean()
        T_overlap_mean = T.loc[: T.index.min() + T0_temp_level, "val"].mean()
        T_mar["val"] = T_mar["val"] - T_mar_overlap_mean + T_overlap_mean
        T_mar = T_mar.loc[: T.index.min() - int((dyr - 1) / 2)]

        T0_temp = pd.concat((T_mar, T))

        # only care about part after beginning of burnin period
        T0_temp = T0_temp.loc[T0_period_st:]
        T0burnin = (T0_temp.index < T.index.min()).sum()

        # convert to long format
        T0_temp = T0_temp.stack()
        T0_temp.index = T0_temp.index.rename("kind", level=-1)
        T0_temp.name = "T"

        data = data.drop(["T", "T_year"]).assign(
            {"T": T0_temp.to_xarray().rename(year="T_year")}
        )
        data["T0burnin"] = T0burnin

    C = xr.DataArray(
        C,
        dims=["sl_year", "sl_year_cov"],
        coords={"sl_year": data.sl_year.values, "sl_year_cov": data.sl_year.values},
        name="sl_C",
    )
    data = xr.merge((data, C))
    return data


def _load_params_from_struct(struct):
    """Load SESL parameter posterior distributions from a MATLAB struct."""
    return pd.DataFrame(
        {
            "a": struct["a"].item(),
            "c": struct["c"].item(),
            "tau": struct["tau"].item(),
            "tau_c": struct["tau_c"].item(),
            "T01": struct["T01"].item(),
        },
        index=pd.Index(np.arange(len(struct["a"].item())), name="sample"),
    ).to_xarray()


def load_param_file(fpath: str) -> xr.Dataset:
    """Load posterior parameter distribution from a trained SESL model (run in the
    MATLAB version of the codebase).
    """
    data = loadmat(fpath, squeeze_me=True)["P"]
    mar = data["Mar"].item()
    mn = data["Mn"].item()
    return xr.concat(
        [_load_params_from_struct(struct) for struct in [mar, mn]],
        dim=pd.Index(["Mar", "Mn"], name="T_data"),
    )
