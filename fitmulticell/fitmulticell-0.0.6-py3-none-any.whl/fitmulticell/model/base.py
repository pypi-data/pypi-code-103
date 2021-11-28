import copy
import logging
import numbers
import os
import shutil
import xml.etree.ElementTree as ET  # noqa: S405
from types import ModuleType
from typing import Callable, List, Union

import numpy as np
import pandas as pd

from ..sumstat import IdSumstatFun
from ..util import base as util_base

logger = logging.getLogger("FitMultiCell.Model")

try:
    from pyabc.external.base import ExternalModel
    from pyabc.parameters import Parameter
except ImportError:
    logger.error("pyabc must be installed.")


class MorpheusModel(ExternalModel):
    """
    Derived from pyabc.ExternalModel. Allows pyABC to call morpheus
    in order to do the model simulation, and then record the results
    for further processing.

    Parameters
    ----------

    model_file:
        The XML file containing the morpheus model.
    par_map:
        A dictionary from str to str, the keys being the parameter ids
        to be used in pyabc, and the values xpaths in the `morpheus_file`.
    par_scale:
        A dictionary or str to state the scale used to define the parameter
        space, e.g., lin, log10, log2
    sumstat_funs:
        List of functions to calculate summary statistics. The list entries
        are instances of fitmulticell.sumstat.SumstatFun.
    executable:
        The path to the morpheus executable. If None given,
        'morpheus' is used.
    suffix, prefix:
        Suffix and prefix to use for the temporary folders created.
    dir:
        Directory to put the temporary folders into. The default is
        the system's temporary files location. Note that these files
        are usually deleted upon system shutdown.
    show_stdout, show_stderr:
        Whether to show or hide the stdout and stderr streams.
    raise_on_error:
        Whether to raise on an error in the model execution, or
        just continue.
    name:
        A name that can be used to identify the model, as it is
        saved to db. If None is passed, the model_file name is used.
    time_var:
        The name of the time variable as define in Morpheus model.
    ignore_list:
        A list of columns to ignore from Morpheus output. This is introduced to
        solve the issue with result that cannot be eliminated from morpheus
        output but yet are not used in the fitting process.
    timeout:
        A time in seconds used to early stop Morpheus simulation when exceed.
    ss_post_processing:
        A callable function to perform post processing on Morpheus output. If
        a dict is passed, then specific function will be applied to each
        summary statistics.
    output_file:
        A name of the file containing the simulation output.
    """

    def __init__(
        self,
        model_file: str,
        par_map: dict,
        par_scale: Union[dict, str] = "lin",
        exp_cond_map: dict = None,
        sumstat_funs: List = None,
        executable: str = "morpheus",
        suffix: str = None,
        prefix: str = "morpheus_model_",
        dir: str = None,
        clean_simulation: bool = False,
        show_stdout: bool = False,
        show_stderr: bool = True,
        raise_on_error: bool = False,
        name: str = None,
        time_var: str = "time",
        ignore_list: list = None,
        timeout: float = np.inf,
        ss_post_processing: Union[Callable, dict] = None,
        output_file: str = "logger.csv",
    ):
        if name is None:
            name = model_file
        super().__init__(
            executable=executable,
            file=model_file,
            fixed_args=None,
            create_folder=True,
            suffix=suffix,
            prefix=prefix,
            dir=dir,
            clean_simulation=clean_simulation,
            show_stdout=show_stdout,
            show_stderr=show_stderr,
            raise_on_error=raise_on_error,
            name=name,
        )

        self.par_map = par_map
        self.par_scale = par_scale
        self.exp_cond_map = exp_cond_map
        if sumstat_funs is None:
            if self.exp_cond_map is None:
                sumstat_funs = [IdSumstatFun()]
            else:
                sumstat_funs = [
                    IdSumstatFun(name=list(self.exp_cond_map.keys())[0])
                ]
        self.clean_simulation = clean_simulation
        self.sumstat_funs = sumstat_funs
        self._check_sumstat_funs()
        self.time_var = time_var
        if ignore_list is None:
            ignore_list = []
        self.ignore_list = ignore_list
        self.timeout = timeout
        self.ss_post_processing = ss_post_processing
        self.output_file = output_file
        self._sanity_chceck_model()

    def __str__(self):
        s = (
            f"MorpheusModel {{\n"
            f"\tname      : {self.name}\n"
            f"\tpar_map      : {self.par_map}\n"
            f"\tsumstat_funs      : {self.sumstat_funs}\n"
            f"\texecutable      : {self.eh.executable}\n"
            f"\toutput_file      : {self.output_file}\n"
            f"}}"
        )
        return s

    def __repr__(self):
        return self.__str__()

    def __call__(self, pars: Parameter):
        """
        This function is used in ABCSMC (or rather the sample() function,
        which redirects here) to simulate data for given parameters `pars`.
        """

        # TODO: move all the content to another function and just call here.

        # create target on file system
        loc = self.eh.create_loc()
        file_ = os.path.join(loc, "model.xml")

        # write new file with parameter modifications
        self.write_modified_model_file(file_, pars)

        # create command
        cmd = self.eh.create_executable(loc)
        self.eh.timeout = self.timeout
        cmd = cmd + f" -file={file_} -outdir={loc}"

        # call the model
        status = self.eh.run(args=pars, cmd=cmd, loc=loc)

        # compute summary statistics
        if status == -15:
            msg = (
                f"Simulation exceed time limit limit: {self.timeout}s "
                f"for arguments {pars}: returncode {status}."
            )
            logger.warning(msg)
            return -15
        sumstats = self.compute_sumstats(loc)

        # remove simulation output
        if self.clean_simulation:
            clean_simulation_output(loc)

        # perform data post-process on Morpheus output
        sumstats = self.call_post_processing_ss(sumstats)
        return sumstats

    def get_parmap_xpath_attr(self, key, attrib='value'):
        """
        Get the xpath and for the parameter of interest

        Parameters
        ----------
        key: str
            name of parameter of interest.
        attrib: str
            the type of attribute that need to be changed on the xml file.

        """

        par = self.par_map[key]
        if isinstance(par, str):
            return par, attrib
        elif isinstance(par, (list, tuple)) and len(par) == 2:
            return par[0], par[1]
        else:
            raise TypeError(
                f"par_map[{key}] should be a str or a list/tuple of length 2"
            )

    def get_expcondmap_xpath_attr(self, key, attrib='value'):
        """
        Get the xpath and for the experimental conditions of interest

        Parameters
        ----------
        key: str
            name of experimental condition of interest.
        attrib: str
            the type of attribute that need to be changed on the xml file.

        """

        exp_cond = self.exp_cond_map[key]
        if isinstance(exp_cond, str):
            return exp_cond, attrib
        elif isinstance(exp_cond, (list, tuple)) and len(exp_cond) == 2:
            return exp_cond[0], exp_cond[1]
        else:
            raise TypeError(
                f"par_map[{key}] should be a str or a list/tuple of length 2"
            )

    def write_modified_model_file(self, file_, pars):
        """
        Write a modified version of the morpheus xml file to the target
        directory.
        """
        temp_par = copy.deepcopy(pars)
        rescaled_pars = util_base.scaling_parameter(temp_par, self.par_scale)
        tree = ET.parse(self.eh.file)  # noqa: S314
        root = tree.getroot()
        for key, val in rescaled_pars.items():
            xpath, attr = self.get_parmap_xpath_attr(key)
            node = root.findall(xpath)
            if node.__len__() == 1:
                node[0].set(attr, str(val))
            else:
                raise KeyError(f"Key {key} is not unique or does not exist.")

        if self.exp_cond_map:
            if len(self.exp_cond_map) < 2:
                for condition, val in self.exp_cond_map.items():
                    for element, inner_val in val.items():
                        if type(inner_val) != list:
                            xpath = element
                        else:
                            xpath = element
                            attr = inner_val[0]
                            inner_val = inner_val[1]
                        node = root.findall(xpath)
                        if node.__len__() == 1:
                            node[0].set(attr, str(inner_val))
                        else:
                            raise KeyError(
                                f"condition {condition} "
                                f"is not unique or does not exist."
                            )
            else:
                raise KeyError(
                    "It seems that the model has more that one condition. "
                    "Please try to use only one condition or"
                    " use appropriate model class."
                )

        tree.write(file_, encoding="utf-8", xml_declaration=True)

    def get_par_value_form_xml_file(self, file_, param):
        """
        Get a parameter value from the model's xml file. This is currently
        being used for testing purposes.
        """
        temp_par = copy.deepcopy(param)
        tree = ET.parse(self.eh.file)  # noqa: S314
        root = tree.getroot()
        xpath, attr = self.get_parmap_xpath_attr(temp_par)
        node = root.findall(xpath)
        return node[0].attrib[attr]

    def compute_sumstats(self, loc):
        """
        Compute summary statistics from the simulated data according to the
        provided list of summary statistics functions.
        """
        sumstat_dict = {'loc': loc}
        if "IdSumstat" in self.sumstat_funs[0].name:
            sumstat_dict = self.sumstat_funs[0](
                loc, self.ignore_list, self.output_file
            )
            sumstat_dict['loc'] = loc

            # here add the prepare function,e.g., 0: val,val,val
            # safe_append_sumstat(sumstat_dict, sumstat, self.sumstat_funs[0])
            return sumstat_dict
        else:
            for sumstat_fun in self.sumstat_funs:
                sumstat = sumstat_fun(loc, self.ignore_list, self.output_file)
                # here add the prepare function,e.g., 0: val,val,val
                safe_append_sumstat(sumstat_dict, sumstat, sumstat_fun.name)
            return sumstat_dict

    def _check_sumstat_funs(self):
        """
        Check sumstat functions for validity.
        """
        names = [ssf.name for ssf in self.sumstat_funs]
        if not len(set(names)) == len(names):
            raise AssertionError(
                f"The summary statistics passed to MorpheusModel must have"
                f"unique names, but obtained {names}"
            )

    def _sanity_chceck_model(self):
        """
        Sanity check of the model upon construction.
        """

        loc = self.eh.create_loc()
        file_ = os.path.join(loc, "model.xml")

        # write new file with for the model
        tree = ET.parse(self.eh.file)  # noqa: S314
        tree.write(file_, encoding="utf-8", xml_declaration=True)

        # create command
        cmd = self.eh.create_executable(loc)
        # self.eh.timeout = self.timeout
        cmd = cmd + f" -file={file_} -outdir={loc}"

        # call the model
        status = self.eh.run(cmd=cmd, loc=loc)
        if status["returncode"] == 0:
            logger.info("Successfully loaded model")
        else:
            raise ValueError(
                f"The model is not running well. "
                f"The simulation seems to fail. "
                f"Returncode: {status['returncode']}"
            )
        clean_simulation_output(loc)

    def call_post_processing_ss(self, sumstats, function_name='main'):
        if self.ss_post_processing is not None:
            if isinstance(self.ss_post_processing, Callable):
                sumstats = self.ss_post_processing(sumstats)
            elif isinstance(self.ss_post_processing, dict):
                if not set(self.ss_post_processing.keys()).issubset(
                    sumstats.keys()
                ):
                    raise ValueError(
                        "the keys on the 'ss_post_processing' does not "
                        "match the one on the summary statistics names."
                    )
                if isinstance(
                    list(self.ss_post_processing.values())[0], Callable
                ):
                    sumstats = self._call_post_processing_ss_use_function(
                        sumstats
                    )
                elif isinstance(
                    list(self.ss_post_processing.values())[0], ModuleType
                ):
                    sumstats = self._call_post_processing_ss_use_module(
                        sumstats, function_name
                    )
            else:
                raise ValueError(
                    f"the type of 'post_processing_ss' should be str or dict."
                    f" However, {type(self.ss_post_processing)} was given."
                )
        return sumstats

    def _call_post_processing_ss_use_module(self, sumstats, function_name):
        sumstat_pp = {}
        for key, _module in self.ss_post_processing.items():
            try:
                func = getattr(
                    self.ss_post_processing[key], function_name, None
                )
                sumstat_pp[key] = func({key: sumstats[key]})
            except Exception as e:
                raise RuntimeError(
                    f"the selected ss_post_processing function "
                    f"can not be called. Be sure that the main "
                    f"function called `main(). `{e}"
                )
        return sumstat_pp

    def _call_post_processing_ss_use_function(self, sumstats):
        sumstat_pp = {}
        for key, function in self.ss_post_processing.items():
            try:
                post_process_ss = function({key: sumstats[key]})
                sumstat_pp[key] = post_process_ss[key]
            except Exception as e:
                raise RuntimeError(
                    f"the selected ss_post_processing function "
                    f"can not be called. `{e}"
                )
        return sumstat_pp


class MorpheusModels(ExternalModel):
    """
    Derived from pyabc.ExternalModel. Allows pyABC to call morpheus
    in order to do the models simulation, and then record the results
    for further processing.

    Parameters
    ----------
    model_file:
        The XML file containing the morpheus model.
    par_map:
        A dictionary from str to str, the keys being the parameter ids
        to be used in pyabc, and the values xpaths in the `morpheus_file`.
    sumstat_funs:
        List of functions to calculate summary statistics. The list entries
        are instances of fitmulticell.sumstat.SumstatFun.
    executable:
        The path to the morpheus executable. If None given,
        'morpheus' is used.
    suffix, prefix:
        Suffix and prefix to use for the temporary folders created.
    dir:
        Directory to put the temporary folders into. The default is
        the system's temporary files location. Note that these files
        are usually deleted upon system shutdown.
    show_stdout, show_stderr:
        Whether to show or hide the stdout and stderr streams.
    raise_on_error:
        Whether to raise on an error in the model execution, or
        just continue.
    name:
        A name that can be used to identify the model, as it is
        saved to db. If None is passed, the model_file name is used.
    time_var:
        The name of the time variable as define in Morpheus model.
    ignore_list:
        A list of columns to ignore from Morpheus output. This is introduced to
        solve the issue with result that cannot be eliminated from morpheus
        output but yet are not used in the fitting process.
    timeout:
        A time in seconds used to early stop Morpheus simulation when exceed.
    ss_post_processing:
        A callable function to perform post processing on Morpheus output. If
        a dict is passed, then specific function will be applied to each
        summary statistics.
    """

    def __init__(self, models_list: List[MorpheusModel], name: str = None):
        self.models_list = models_list
        self.name = name

    def __str__(self):
        s = f"MorpheusModels {{\n" f"\tname      : {self.name}\n" f"}}"
        return s

    def __repr__(self):
        return self.__str__()

    def __call__(self, pars: Parameter):
        """
        This function is used in ABCSMC (or rather the sample() function,
        which redirects here) to simulate data for given parameters `pars`
        and given experimental conditions.
        """

        # TODO: move all the content to another function and just call here.

        # a list that will hold result for each experimental condition.
        sumstats_all = {}
        # create target on file system
        for model in self.models_list:
            # cond_sumstats = {}
            sumstats = model(pars)
            # for ss_key, ss_val in sumstats.items():
            #     cond_sumstats[list(model.exp_cond_map.keys())[0]
            #     + '__' + ss_key] = sumstats[ss_key]
            sumstats_all.update(sumstats)
        return sumstats_all

    def get_parmap_xpath_attr(self, key, attrib='value'):
        """
        Get the xpath and for the parameter of interest

        Parameters
        ----------
        key: str
            name of parameter of interest.
        attrib: str
            the type of attribute that need to be changed on the xml file.

        """
        # TODO: this function is written twice
        par = self.par_map[key]
        if isinstance(par, str):
            return par, attrib
        elif isinstance(par, (list, tuple)) and len(par) == 2:
            return par[0], par[1]
        else:
            raise TypeError(
                f"par_map[{key}] should be a str or a list/tuple of length 2"
            )

    def write_modified_models_file(self, file_, pars, exp_cod):
        """
        Write a modified version of the morpheus xml file to the target
        directory.
        """
        temp_par = copy.deepcopy(pars)
        rescaled_pars = util_base.scaling_parameter(temp_par, self.par_scale)
        tree = ET.parse(self.eh.file)  # noqa: S314
        root = tree.getroot()
        # parameters
        for key, val in rescaled_pars.items():
            xpath, attr = self.get_parmap_xpath_attr(key)
            node = root.findall(xpath)
            if node.__len__() == 1:
                node[0].set(attr, str(val))
            else:
                raise KeyError(f"Key {key} is not unique or does not exist.")
        # conditions
        for key, val in exp_cod.items():
            xpath, attr = self.get_parmap_xpath_attr(key)
            node = root.findall(xpath)
            if node.__len__() == 1:
                node[0].set(attr, str(val))
            else:
                raise KeyError(f"Key {key} is not unique or does not exist.")

        tree.write(file_, encoding="utf-8", xml_declaration=True)

    def call_post_processing_ss(self, sumstats, function_name='main'):
        if self.ss_post_processing is not None:
            if isinstance(self.ss_post_processing, Callable):
                sumstats = self.ss_post_processing(sumstats)
            elif isinstance(self.ss_post_processing, dict):
                if not set(self.ss_post_processing.keys()).issubset(
                    sumstats.keys()
                ):
                    raise ValueError(
                        "the keys on the 'ss_post_processing' does not "
                        "match the one on the summary statistics names."
                    )
                if isinstance(
                    list(self.ss_post_processing.values())[0], Callable
                ):
                    sumstats = self._call_post_processing_ss_use_function(
                        sumstats
                    )
                elif isinstance(
                    list(self.ss_post_processing.values())[0], ModuleType
                ):
                    sumstats = self._call_post_processing_ss_use_module(
                        sumstats, function_name
                    )
            else:
                raise ValueError(
                    f"the type of 'post_processing_ss' should be str or dict."
                    f" However, {type(self.ss_post_processing)} was given."
                )
        return sumstats

    def _call_post_processing_ss_use_module(self, sumstats, function_name):
        sumstat_pp = {}
        for key, _module in self.ss_post_processing.items():
            try:
                # sumstat_pp[key] = module.main(sumstats)
                func = getattr(
                    self.ss_post_processing[key], function_name, None
                )
                sumstat_pp[key] = func(sumstats[key])
            except Exception as e:
                raise RuntimeError(
                    f"the selected ss_post_processing function "
                    f"can not be called. Be sure that the main "
                    f"function called `main(). `{e}"
                )
        return sumstat_pp

    def _call_post_processing_ss_use_function(self, sumstats):
        sumstat_pp = {}
        for key, function in self.ss_post_processing.items():
            try:
                sumstat_pp[key] = function(sumstats[key])
            except Exception as e:
                raise RuntimeError(
                    f"the selected ss_post_processing function "
                    f"can not be called. `{e}"
                )
        return sumstat_pp


def safe_append_sumstat(sumstat_dict, sumstat, key):
    types_ = (numbers.Number, np.ndarray, pd.DataFrame)
    if isinstance(sumstat, types_):
        if key in sumstat_dict:
            raise KeyError(
                f"Key {key} for sumstat {sumstat} already in the "
                f"sumstat dict {sumstat_dict}."
            )
        sumstat_dict[key] = sumstat
        return
    if isinstance(sumstat, dict):
        if key in sumstat_dict:
            raise KeyError(
                f"Key {key} for sumstat {sumstat} already in the "
                f"sumstat dict {sumstat_dict}."
            )
        sumstat_dict.update(sumstat)
        return
    raise ValueError(
        f"Type {type(sumstat)} of sumstat {sumstat} " f"is not permitted."
    )


def clean_simulation_output(loc):
    """
    Remove the simulation output directory after calculating the
    summary statistics.

    Parameters
    ----------
    loc: str
        Location of the simulation directory.
    """

    shutil.rmtree(loc, ignore_errors=True)
