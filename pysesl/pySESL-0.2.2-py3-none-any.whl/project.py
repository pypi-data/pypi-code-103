from math import ceil

import numpy as np
import pandas as pd
import xarray as xr

from .historical import calc_sl, calc_T0, calc_temp
from .io import load_data_SESL


def get_ics(n_fair_sims, sesl_trained_params, sesl_hyperparams, sesl_input_dir):
    """Get initial conditions T0_2000 and c_2000 necessary for projecting using SESL.
    Also return T_ref, or the mean temperature over the reference period as defined in
    ``sesl_hyperparams``.

    TODO: finish docstring
    """
    # figure out how many historical temp draws to use
    n_sesl_samps = len(sesl_trained_params.sample)
    n_sesl_data_samps = len(sesl_trained_params.T_data)

    T_num = ceil(n_fair_sims / n_sesl_samps / n_sesl_data_samps)

    T0_2000 = []
    T_ref = []
    c_2000 = []

    T_ref_range = np.arange(
        sesl_hyperparams["T_bias_correction_period"][0],
        sesl_hyperparams["T_bias_correction_period"][1] + 1,
    )

    for dat in sesl_hyperparams["T_data"]:
        historical_data = load_data_SESL(
            sesl_input_dir / (sesl_hyperparams["SL_data"] + ".mat"),
            sesl_input_dir / (dat + ".mat"),
            sesl_hyperparams["use_cov"],
            sesl_hyperparams["use_Mar_T0"],
            Mar_fpath=sesl_input_dir / "Marcott13_RegEM-HC3_20.mat",
            T_err_sc=sesl_hyperparams["T_err_sc"],
            cov_tau=sesl_hyperparams["cov_tau"],
            no_neg_cov=sesl_hyperparams["no_neg_cov"],
            baseperiod=sesl_hyperparams["baseperiod"],
            T0_temp_level=sesl_hyperparams["T0_temp_level"],
            T0_period_st=sesl_hyperparams["T0_period"][0],
        )

        T_sims = calc_temp(
            historical_data,
            sesl_hyperparams["T_err"],
            T_num,
            sesl_trained_params.dims["sample"],
            tau_ar1=sesl_hyperparams["tau_ar1"],
        )

        T_ref.append(T_sims.interp(year=T_ref_range).mean("year"))

        if dat[:4] == "Mann":
            dat_short = "Mn"
        elif dat[:4] == "Marc":
            dat_short = "Mar"
        else:
            raise NotImplementedError(dat)
        T0_sims = calc_T0(
            T_sims,
            historical_data,
            sesl_trained_params.sel(T_data=dat_short, drop=True),
            sesl_hyperparams["optim_T0"],
            sesl_hyperparams["model"],
            T0_period_end=sesl_hyperparams["T0_period"][1],
        )
        T0_2000.append(T0_sims.interp(year=2000).drop("year"))

        _, _, c, _, _ = calc_sl(
            T_sims,
            T0_sims,
            sesl_trained_params.sel(T_data=dat_short, drop=True),
            sesl_hyperparams["model"],
            [
                min(sesl_hyperparams["period"][0], sesl_hyperparams["calibperiod"][0]),
                max(sesl_hyperparams["period"][1], sesl_hyperparams["calibperiod"][1]),
            ],
        )

        c_2000.append(c.sel(year=2000, drop=True))

    dim = pd.Index(sesl_hyperparams["T_data"], name="T_data")
    T0_2000, c_2000, T_ref = list(
        map(
            lambda x: xr.concat(x, dim=dim),
            [T0_2000, c_2000, T_ref],
        )
    )

    new_T_data = T0_2000.T_data.str[:3]
    new_T_data = new_T_data.where(new_T_data == "Mar", "Mn")
    T0_2000["T_data"] = new_T_data
    c_2000["T_data"] = new_T_data
    T_ref["T_data"] = new_T_data

    return xr.Dataset({"T0_2000": T0_2000, "c_2000": c_2000, "T_ref": T_ref})


def bias_correct_temps_and_resample_ics(
    temps, bc_period, ics, sesl_trained_params, sesl_hyperparams, first_year=None
):
    """Bias correct a temperature dataset such that it matches with the reference period
    used to calculate the T0_2000 initial condition. Also, resample ICs such that they
    have the same number of samples as are in the temperature projections ``temps``.

    TODO: finish docstring
    """
    # get T0_2000, T_ref in index of FAIR samples
    def resample_full(ds):
        return ds.stack(simulation=["T_sim_id", "sample", "T_data"]).isel(
            simulation=slice(None, len(temps.simulation))
        )

    T0_2000, T_ref = list(map(resample_full, [ics.T0_2000, ics.T_ref]))
    assert (T0_2000.simulation == T_ref.simulation).all()

    # new_T_data = T0_2000.T_data.str[:3]
    # new_T_data = new_T_data.where(sesl_p["T_data"] == "Mar", "Mn")

    # get the appropriate parameters for each of the 3k sims
    def resample_partial(ds):
        out = ds.stack(simulation=["sample", "T_data"]).sel(
            simulation=pd.MultiIndex.from_arrays(
                (T0_2000.sample.values, T0_2000.T_data.values),
                names=["sample", "T_data"],
            )
        )
        out["simulation"] = temps.simulation
        return out

    param_sims, c_2000 = list(map(resample_partial, [sesl_trained_params, ics.c_2000]))
    T0_2000["simulation"] = temps.simulation
    T_ref["simulation"] = temps.simulation
    out_params = xr.merge((T0_2000, c_2000, T_ref, param_sims))

    # Get temps in units of reconstruction data (to match T0) and bias correct to the 2
    # draws of reconstructed T over the reference period
    out_temps = (temps - temps.sel(year=slice(*bc_period)).mean("year") + T_ref).sel(
        year=slice(first_year, None)
    )

    return out_temps, out_params


def project_sesl(temps, params):
    """Project GMSL given input temperatures and params (including initial conditions).
    Note that ``temps`` must already be corrected to have the same reference period as
    ``params.T0_2000``.

    TODO: finish docstring
    """

    temp_arr = temps.copy()
    sl = 0 * temp_arr

    a = params.a
    tau = params.tau
    tau_c = params.tau_c

    T0 = params.T0_2000.broadcast_like(temp_arr.isel(year=0, drop=True)).copy()
    c = params.c_2000.broadcast_like(tau_c).copy()

    # iterate over years
    for yr in sl.year:
        TminusT0 = temp_arr.sel(year=yr, drop=True) - T0

        # update SL
        if yr > sl.year[0]:
            sl.loc[{"year": yr}] = sl.sel(year=yr - 1, drop=True) + a * TminusT0 + c

        # update T0
        T0 += 1 / tau * TminusT0

        # update c
        c *= 1 - 1 / tau_c

    # convert to DataArray
    return sl
