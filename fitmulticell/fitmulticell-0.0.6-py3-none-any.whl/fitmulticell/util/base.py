import copy
import os
from typing import Union

import pandas as pd


def tsv_to_df(loc: str, file_: str = "logger.csv"):
    """
    Read in the morpheus logging file `file_`, which should be in
    tab-separated tsv format and defaults to "logger.csv", inside
    directory `loc`.

    Parameters
    ----------

    loc: str
        The simulations results folder.
    file_: str, optional (default="logger.csv")
        The logger file containing the results in tsv format.

    Returns
    -------

    data_frame: pandas.DataFrame
        A dataframe of the file contents.
    """
    data_file = os.path.join(loc, file_)
    data_frame = pd.read_csv(data_file, sep="\t")
    return data_frame


def split_list(alist, wanted_parts):
    """
    Take a set of lists based on the number of particles and turn that into a
    set of list based on the number of summary statistics.

    Parameters
    ----------
    alist: str
        list of particles readout
    wanted_parts: int
        should be equal to the number of summary statistics functions.
    Returns
    -------
        A list of lists, were the number of lists equal to the number of
        summary statistic functions.
    """
    return [alist[i::wanted_parts] for i in range(wanted_parts)]


def scaling_parameter(par_vals, par_scale: Union[str, dict]):
    """
    Rescaling parameter value to match the parameter space define in the
    prior distribution
    Parameters
    ----------
    par_vals: dict
        parameters name as a key and parameter value as a value of the dict.
    par_scale: str, or dict
        the scale to be used. It can be passed as a single value to be use for
         all parameters, or a dict to be applied to each parameter
         individually ,e.g., "log10".
    Returns
    -------
        a dictionary of the parameters value rescaled according to the
        par_scale.
    """
    #    if isinstance(par_scale, str):
    #        if par_scale == "log10":
    #            par_vals.update((x, 10**y) for x, y in par_vals.items())
    #        elif par_scale == "log2":
    #            par_vals.update((x, 2**y) for x, y in par_vals.items())
    #        elif par_scale == "linear":
    #            par_vals
    #        else:
    #            raise ValueError(
    #                f"The entered parameter scale 'par_scale'= {par_scale} is "
    #                f"not supported")

    #    if isinstance(par_scale, dict):
    #        for key, scale in par_scale.items():
    #            if scale == "log10":
    #                par_vals[key] = 10 ** par_vals[key]
    #            elif scale == "log2":
    #                par_vals[key] = 2 ** par_vals[key]
    #            elif scale == "linear":
    #                continue
    #            else:
    #                raise ValueError(
    #                    f"One of the entered parameter scale 'par_scale'=
    #                       {scale} is "
    #                    f"not supported")

    scaled_dict = copy.deepcopy(par_vals)
    if isinstance(par_scale, str):
        if par_scale == "log10":
            scaled_dict.update((x, 10 ** y) for x, y in par_vals.items())
        elif par_scale == "log2":
            scaled_dict.update((x, 2 ** y) for x, y in par_vals.items())
        elif par_scale == "lin":
            scaled_dict
        else:
            raise ValueError(
                f"The entered parameter scale 'par_scale'= {par_scale} is "
                f"not supported"
            )
        return scaled_dict
    else:
        for key, val in par_scale.items():
            if val == "log10":
                scaled_dict[key] = 10 ** par_vals[key]
            elif val == "log2":
                scaled_dict[key] = 2 ** par_vals[key]
            elif val == "lin":
                scaled_dict[key] = par_vals[key]
            else:
                raise ValueError(
                    f"The entered parameter scale 'par_scale'= {par_scale} is "
                    f"not supported"
                )
        return scaled_dict


def from_Morpheus_log_to_sumstat(loc: str):
    """
    Use the simulation output directly as a summary statistics.

    Parameters
    ----------
    loc: str
        The simulation folder.

    Returns
    -------
    sumstat: dict
        output file in a proper format
    """
    df = tsv_to_df(loc, "logger.csv")
    return df
