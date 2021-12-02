import json
from abc import ABC
from contextlib import contextmanager
from inspect import signature
from typing import Any, Callable, Dict, List, Set, Union

import numpy as np

CfgDict = Dict[str, Any]
Real = Union[float, int]


class InvalidConfigurationException(Exception):
    """Custom exception thrown by builder's validation rules."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Builder(ABC):
    """A base class for a configuration builder."""

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__()
        self._cfg = cfg

    def validate(self):
        """Validates the builder values, invoked on builder context close, or before persisting of the configuration.
        Normally it should not be necessary to call that method explicitly."""
        ...

    @staticmethod
    def _get_or_create_item(items: List, name_key: str, name: str, creator: Callable[[str], CfgDict]):
        existing_items = list(filter(lambda p: p[name_key] == name, items))
        existing_items_len = len(existing_items)
        if existing_items_len == 0:
            item = creator(name)
            items.append(item)
            return item
        if existing_items_len == 1:
            item: CfgDict = existing_items[0]
            return item
        else:
            raise InvalidConfigurationException(
                f"More than one item with {name_key} == {name}")


class ParameterBuilder(Builder):
    """Optimization parameter settings builder"""

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__(cfg)

    @property
    def name(self) -> str:
        """Gets parameter name, the key of the parameter the in dictionary passed to an evaluator."""
        return self._cfg["parameter_name"]

    @property
    def lower_limit(self) -> float:
        """Gets and sets a lower limit for parmater value."""
        return float(self._cfg["lower_limit"])

    @lower_limit.setter
    def lower_limit(self, value: Real):
        self._cfg["lower_limit"] = float(value)

    @property
    def upper_limit(self) -> float:
        """Gets and sets an upper limit for parmater value."""
        return float(self._cfg["upper_limit"])

    @upper_limit.setter
    def upper_limit(self, value: Real):
        self._cfg["upper_limit"] = float(value)

    @property
    def initial_value(self) -> float:
        """Gets and sets an initial paramater value. 
        Must be be within :attr:`.ParameterBuilder.lower_limit` and :attr:`.ParameterBuilder.upper_limit`.
        """
        return float(self._cfg["initial_value"])

    @initial_value.setter
    def initial_value(self, value: Real):
        self._cfg["initial_value"] = float(value)

    @property
    def initial_variation(self) -> float:
        """Gets ans sets an initial variation for parameter value. 
        Must be less than :attr:`.ParameterBuilder.upper_limit` - :attr:`.ParameterBuilder.lower_limit`.
        """
        return float(self._cfg["amplitude_variation"])

    @initial_variation.setter
    def initial_variation(self, value: Real):
        self._cfg["amplitude_variation"] = float(value)

    def validate(self) -> None:
        if not self.initial_value >= self.lower_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.initial_value=} must be greater or equal then than {self.lower_limit=}")
        if not self.initial_value <= self.upper_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.initial_value=} must be smaller or equal then than {self.upper_limit=}")
        if not self.lower_limit < self.upper_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.lower_limit=} must be smaller than {self.upper_limit=}")
        if self.initial_variation > self.upper_limit - self.lower_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.initial_variation=} must be smaller or equal then than {self.upper_limit - self.lower_limit=}")

    @staticmethod
    def _create_cfg(name: str):
        return {
            "parameter_name": name,
            "lower_limit": 0.0,
            "upper_limit": 1.0,
            "initial_value": 0.5,
            "amplitude_variation": 0.5
        }


class UniformSuperParameterDistributionBuilder(Builder):
    """Super parameter distribution and bins range, i.e. frequency range for fourier basis. Reduce upper limit to suppress high-frequency harmonics"""

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__(cfg)

    @staticmethod
    def _create(cfg: CfgDict):
        if cfg["distribution_name"] == "Uniform":
            return UniformSuperParameterDistributionBuilder(cfg)
        else:
            return UniformSuperParameterDistributionBuilder(
                UniformSuperParameterDistributionBuilder._create_cfg())

    @property
    def lower_limit(self) -> float:
        """Gets and sets bins lower range, i.e. frequency range for fourier basis"""
        return float(self._cfg["lower_limit"])

    @lower_limit.setter
    def lower_limit(self, value: Real):
        value = float(value)
        if value <= 0:
            raise InvalidConfigurationException(
                "lower_limit must be greater than 0")
        self._cfg["lower_limit"] = value

    @property
    def upper_limit(self) -> float:
        """Gets ans sets bins upper range, i.e. frequency range for fourier basis. Reduce upper limit to suppress high-frequency harmonics. 
        **Default:30**
        """
        return float(self._cfg["upper_limit"])

    @upper_limit.setter
    def upper_limit(self, value: Real):
        value = float(value)
        if value <= 0:
            raise InvalidConfigurationException(
                "upper_limit must be greater than 0")
        self._cfg["upper_limit"] = value

    def validate(self) -> None:
        if self.lower_limit > self.upper_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.lower_limit=} must be smaller than {self.upper_limit=}")

    @staticmethod
    def _create_cfg():
        return {
            "distribution_name": "Uniform",
            "distribution_class": "Uniform",
            "distribution_module": "quocslib.pulses.super_parameter.Uniform",
            "lower_limit": 0.1,
            "upper_limit": 30.0
        }


class PulseFourierBasisBuilder(Builder):

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__(cfg)

    @staticmethod
    def _create(cfg: CfgDict):
        if cfg["basis_name"] == "Fourier":
            return PulseFourierBasisBuilder(cfg)
        else:
            return PulseFourierBasisBuilder(
                {
                    "basis_name": "Fourier",
                    "basis_class": "Fourier",
                    "basis_module": "quocslib.pulses.basis.Fourier",
                    "basis_vector_number": cfg["basis_vector_number"],
                    "random_super_parameter_distribution": cfg["random_super_parameter_distribution"]
                }
            )

    @property
    def basis_vector_number(self) -> int:
        """Gets and sets subset of randomly selected basis function to fit the function.
        Default: 10

        Raises
        ------
        InvalidConfigurationException
            if the value is less or equal to 0
        """
        return int(self._cfg["basis_vector_number"])

    @basis_vector_number.setter
    def basis_vector_number(self, value: int):
        value = int(value)
        if value <= 0:
            raise InvalidConfigurationException(
                "basis_vector_number must be greater than 0")
        self._cfg["basis_vector_number"] = value

    @contextmanager
    def uniform_super_parameter_distribution(self):
        """        
        Returns
        -------
        UniformSuperParameterDistributionBuilder
            A builder for uniform super parameter distribution settings
        """
        cfg: CfgDict = self._cfg["random_super_parameter_distribution"]
        builder = UniformSuperParameterDistributionBuilder._create(cfg)
        yield builder
        builder.validate()
        self._cfg["random_super_parameter_distribution"] = builder._cfg

    @staticmethod
    def _create_cfg():
        return {
            "basis_name": "Fourier",
            "basis_class": "Fourier",
            "basis_module": "quocslib.pulses.basis.Fourier",
            "basis_vector_number": 10,
            "random_super_parameter_distribution":
                UniformSuperParameterDistributionBuilder._create_cfg()
        }


class FunctionBuilder(Builder):
    """Builds scaling function or initial guess as a function."""

    @property
    def function(self) -> Union[List[float], str]:
        """Gets and sets the function definition.

        
        Examples
        --------


        * list_function

        This example implicitly sets :attr:`FunctionBuilder.type` `== 'list_function'`.
        *Note: Size of the list must match bin_number, specified in the pulse.*

        .. code-block:: python 

            scale_function.function = [0,1,2,3,4,5,4,3,2,1]


        * lambda_function
        
        This example implicitly sets :attr:`FunctionBuilder.type` `== 'lambda_function'`.

        .. code-block:: python 

            scale_function.function = "lambda t: np.exp(-(t - 0.5)**2/(2*0.2**2))"

        Raises
        ------
        InvalidConfigurationException
            the value is invalid
        """
        if self.type == "list_function":
            return json.loads(self._cfg["list_function"])
        else:
            return self._cfg["lambda_function"]

    @function.setter
    def function(self, value) -> None:
        """Set the value of function.

        Parameters
        ----------
        value : Union[str, List, numpy.ndarray]
            function value as list of floats or a lambda function (as string)

        """
        self._cfg.clear()

        if isinstance(value, np.ndarray):
            self._set_ndarray(value)
        elif isinstance(value, List):
            value = np.asarray(value, dtype=np.double)
            self._set_ndarray(value)
        else:
            self._set_lambda(value)

    def _set_lambda(self, value):
        fun = str(value)
        try:
            compiled = eval(fun, {"np": np})
        except Exception as e:
            raise InvalidConfigurationException(
                f"Exception while compiling function {fun}") from e
        if not isinstance(compiled, Callable):
            raise InvalidConfigurationException(
                f"{fun} does not evaluate to a Callable, should be a function")
        s = signature(compiled)
        if len(s.parameters) != 1:
            raise InvalidConfigurationException(
                f"{fun} must be a lambda function of a single argument")
        try:
            compiled(0)
        except Exception as e:
            raise InvalidConfigurationException(
                f"{fun} can't be evalated at t=0") from e

        self._cfg["function_type"] = "lambda_function"
        self._cfg["lambda_function"] = fun

    def _set_ndarray(self, value):
        if len(value.shape) != 1:
            raise InvalidConfigurationException(
                "List function must be a single element array")
        value = value.tolist()
        self._cfg["function_type"] = "list_function"
        self._cfg["list_function"] = json.dumps(value)

    @property
    def type(self) -> str:
        """Gets the type of the function.

        Returns
        -------
        str
            `"list_function"` or `"lambda_function"`
        """
        return str(self._cfg["function_type"])


class PulseBuilder(Builder):

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__(cfg)

    @property
    def name(self) -> str:
        """Gets a name of a pulse."""
        return self._cfg["parameter_name"]

    @property
    def lower_limit(self) -> float:
        """Gets and sets the lower clipping limit of a pulse value."""
        return float(self._cfg["lower_limit"])

    @lower_limit.setter
    def lower_limit(self, value: Real):
        self._cfg["lower_limit"] = float(value)

    @property
    def upper_limit(self) -> float:
        """Gets and sets upper clipping limit of a pulse value."""
        return float(self._cfg["upper_limit"])

    @upper_limit.setter
    def upper_limit(self, value: Real):
        self._cfg["upper_limit"] = float(value)

    @property
    def bins_number(self) -> int:
        """Gets and sets the samples number. 
        The pulse values are sampled at :code:`np.linspace(0, time, bins_number)` instants"""
        return int(self._cfg["bins_number"])

    @bins_number.setter
    def bins_number(self, value: Real):
        self._cfg["bins_number"] = int(value)

    @property
    def initial_variation(self) -> float:
        """Gets and sets an initial variation amplitude
        
        Raises
        ------
        InvalidConfigurationException
            the value is less or equal to 0
        """
        return float(self._cfg["amplitude_variation"])

    @initial_variation.setter
    def initial_variation(self, value: Real):
        if value <= 0:
            raise InvalidConfigurationException("initial_variation must be positive")
        self._cfg["amplitude_variation"] = value

    @property
    def time_name(self) -> str:
        """Gets and sets a referenced time name. 
        The name must match one time name out of specified in the configuration."""
        return self._cfg["time_name"]

    @time_name.setter
    def time_name(self, value: str):
        self._cfg["time_name"] = value

    def _function(self: str, key: str):
        cfg: CfgDict = self._cfg[key]
        builder = FunctionBuilder(cfg)
        yield builder
        builder.validate()

    @contextmanager
    def scaling_function(self):
        """        
        Returns
        -------
        FunctionBuilder
            A builder for a scaling function
        """
        return self._function("scaling_function")

    @contextmanager
    def initial_guess(self):
        """        
        Returns
        -------
        FunctionBuilder
            A builder for an initial guess function
        """
        return self._function("initial_guess")

    @contextmanager
    def fourier_basis(self):
        """Selects fourier basis 
        
        Returns
        -------
        PulseFourierBasisBuilder
            A fourier basis settings builder.
        """
        cfg: CfgDict = self._cfg["basis"]
        builder = PulseFourierBasisBuilder._create(cfg)
        yield builder
        builder.validate()
        self._cfg["basis"] = builder._cfg

    def validate(self) -> None:
        if self.lower_limit > self.upper_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.lower_limit=} must be smaller than {self.upper_limit=}")
        if self.initial_variation > self.upper_limit - self.lower_limit:
            raise InvalidConfigurationException(
                f"parameter: {self.name}, {self.initial_variation=} must be smaller or equal then than {self.upper_limit - self.lower_limit=}")

    @staticmethod
    def _get_time_names(times: List[CfgDict]) -> Set[str]:
        return set(map(lambda p: p["time_name"], times))

    @staticmethod
    def _create_cfg(name: str):
        return {
            "pulse_name": name,
            "upper_limit": 1.0,
            "lower_limit": -1.0,
            "bins_number": 11,
            "time_name": "time1",
            "amplitude_variation": 0.5,
            "basis": PulseFourierBasisBuilder._create_cfg(),
            "scaling_function": {
                "function_type": "lambda_function",
                "lambda_function": "lambda t: 1.0"
            },
            "initial_guess": {
                "function_type": "lambda_function",
                "lambda_function": "lambda t: 0.0"
            }
        }


class TimeBuilder(Builder):
    """Defines an eventually optimized pulse duration, referenced by one or more pulse definitions"""

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__(cfg)

    @property
    def name(self) -> float:
        """Gets a name of time."""
        return self._cfg["time_name"]

    @property
    def initial_value(self) -> float:
        """Gets and sets the initial value.
        
        Raises
        ------
        InvalidConfigurationException
            A value is not positive
        """
        return float(self._cfg["initial_value"])

    @initial_value.setter
    def initial_value(self, value: Real):
        if (value <= 0):
            raise InvalidConfigurationException(
                f"Time {self.name}, initial_value must be positive")
        self._cfg["initial_value"] = value

    @property
    def optimize(self) -> bool:
        """Gets and sets whether the pulse duration should be optimized as well as shape"""
        return bool(self._cfg["is_optimization"])

    @optimize.setter
    def optimize(self, value: bool):
        self._cfg["is_optimization"] = bool(value)

    @staticmethod
    def _get_time_names(times: List[CfgDict]) -> Set[str]:
        return set(map(lambda p: p["time_name"], times))

    @staticmethod
    def _create_cfg(name: str):
        return {
            "time_name": name,
            "initial_value": 1.0,
            "is_optimization": False
        }


class DCRABSettingsBuilder(Builder):
    """Defines parameters for meta-optimization using dressed CRAB (Chopped RAndom Basis)"""

    @property
    def super_iteration_number(self) -> int:
        """Gets and sets super iteration number. 
        **Default: 5**
        """
        return int(self._cfg["initial_value"])

    @super_iteration_number.setter
    def super_iteration_number(self, value: int):
        if (value <= 0):
            raise InvalidConfigurationException(
                f"super_iteration_number must be positive")
        self._cfg["super_iteration_number"] = value

    @property
    def maximum_iterations_per_super_iteration(self) -> int:
        """Gets and sets iterations per super iteration.
        Note: Current implementation can make up several iterations more than specified.
        **Default: 20**"""
        return int(self._cfg["initial_value"])

    @maximum_iterations_per_super_iteration.setter
    def maximum_iterations_per_super_iteration(self, value: int):
        if (value <= 0):
            raise InvalidConfigurationException(
                f"maximum_function_evaluations_number must be positive")
        self._cfg["maximum_function_evaluations_number"] = value

    @staticmethod
    def _create_cfg():
        return {
            "super_iteration_number": 5,
            "maximum_function_evaluations_number": 20
        }


class StoppingCriteriaBuilder(Builder):
    ...

    @property
    def iterations_number(self) -> int:
        """Gets ans sets maximum iteration number.
        Note: Current implementation can make up several iterations more than specified.
        **Default: 100**.
        
        Raises
        ------
        InvalidConfigurationException
            An iteration number is not positive.
        """
        return int(self._cfg["iterations_number"])

    @iterations_number.setter
    def iterations_number(self, value: int):
        if value <= 0:
            raise InvalidConfigurationException(
                f"iterations_number must be positive")
        self._cfg["iterations_number"] = int(value)

    @property
    def xatol(self) -> float:
        """Gets ans sets the variation of argument, where the optimization stops if below. 
        ** Default: 1e-13 **
        """
        return float(self._cfg["xatol"])

    @xatol.setter
    def xatol(self, value: Real):
        if value < 1e-13:
            raise InvalidConfigurationException(
                "Stoping parameter variation (xatol) must be greater or equal to than 1E-13")
        self._cfg["xatol"] = float(value)

    @property
    def frtol(self) -> float:
        """Gets ans sets the variation of figure of merit function, where the optimization stops if below.         
        ** Default: 1e-13 **
        """
        return float(self._cfg["frtol"])

    @frtol.setter
    def frtol(self, value: Real):
        if value < 1e-13:
            raise InvalidConfigurationException(
                "Stoping parameter variation (xatol) must be greater or equal to than 1E-13")
        self._cfg["frtol"] = float(value)

    @staticmethod
    def _create_cfg():
        return {
            "iterations_number": 100,
            "xatol": 1e-13,
            "frtol": 1e-13
        }


class DSMSettingsBuilder(Builder):

    @property
    def is_adaptive(self) -> bool:
        """Gets ans sets whether the algorithm adapts to dimensionality of problem: Useful for high-dimensional minimization """
        return bool(self._general_settings["is_adaptive"])

    @is_adaptive.setter
    def is_adaptive(self, value: bool):
        self._general_settings["is_adaptive"] = value

    @property
    def _general_settings(self):
        return self._cfg["general_settings"]

    @contextmanager
    def stopping_criteria(self):
        """
        Returns
        -------
        StoppingCriteriaBuilder
            a builder for a stopping criteria.
        """
        cfg = self._cfg["stopping_criteria"]
        builder = StoppingCriteriaBuilder(cfg)
        yield builder
        builder.validate()

    @staticmethod
    def _create_cfg():
        return {
            "general_settings": {
                "dsm_name": "nelder_mead",
                "is_adaptive": True
            },
            "stopping_criteria": StoppingCriteriaBuilder._create_cfg()
        }


class ConfigurationBuilder(Builder):

    def __init__(self, cfg: CfgDict) -> None:
        super().__init__(cfg)

    @contextmanager
    def parameter(self, name: str):
        """Creates a builder for specified parameter.
        If an item with a same was previously defined, binds the context to it,
        otherwise create a new item.
        
        Parameters
        ----------
        name : str
            A name of a parameter to define or edit.
                
        Returns
        -------
        ParameterBuilder
            The parameter builder.
        """
        parameters: List[CfgDict] = self._parameters
        builder = ParameterBuilder(Builder._get_or_create_item(
            parameters, "parameter_name", name, ParameterBuilder._create_cfg))
        yield builder
        builder.validate()

    @contextmanager
    def pulse(self, name: str):
        """Creates a builder for specified pulse.
        If an item with a same was previously defined, binds the context to it,
        otherwise create a new item.
        
        Parameters
        ----------
        name : str
            A name of a pulse to define or edit.
                
        Returns
        -------
        PulseBuilder
            The parameter builder.
        """        
        pulses: List[CfgDict] = self._pulses
        builder = PulseBuilder(Builder._get_or_create_item(
            pulses, "parameter_name", name, PulseBuilder._create_cfg))
        yield builder
        builder.validate()

    @contextmanager
    def time(self, name: str):
        """Creates a builder for specified time.
        If an item with a same was previously defined, binds the context to it,
        otherwise create a new item.
        
        Parameters
        ----------
        name : str
            A name of a time to define or edit.
                
        Returns
        -------
        TimeBuilder
            The parameter builder.
        """        
        parameters: List[CfgDict] = self._times
        builder = TimeBuilder(Builder._get_or_create_item(
            parameters, "parameter_name", name, TimeBuilder._create_cfg))
        yield builder
        builder.validate()

    def clear_times(self) -> None:
        """Removes all time definitions."""
        if not self.is_pulse_optimization:
            raise InvalidConfigurationException(
                "Times can be defined only with pulse optimization algorithm")
        self._optimization_dictionary["times"] = []

    def clear_pulses(self) -> None:
        """Removes all pulses definitions."""
        if not self.is_pulse_optimization:
            raise InvalidConfigurationException(
                "Pulses can be defined only with pulse optimization algorithm")
        self._optimization_dictionary["pulses"] = []

    def clear_parameters(self) -> None:
        """Removes all parameters definitions."""
        self._optimization_dictionary["parameters"] = []

    @contextmanager
    def dcrab_settings(self):
        """
        Raises
        -------
        InvalidConfigurationException 
            The setting is not applicable for selected optimization algorithm

        Returns
        -------
        DCRABSettingsBuilder
            A builder for changing dCRAB settings
        """
        if not self.is_pulse_optimization:
            raise InvalidConfigurationException(
                "Times can be defined only with pulse optimization algorithm")
        cfg = self._optimization_dictionary["algorithm_settings"]
        builder = DCRABSettingsBuilder(cfg)
        yield builder
        builder.validate()

    @contextmanager
    def direct_search_method_settings(self):
        """
        Returns
        -------
        DSMSettingsBuilder
            A builder for changing direct search method settings.
        """
        cfg = self._optimization_dictionary["dsm_settings"]
        builder = DSMSettingsBuilder(cfg)
        yield builder
        builder.validate()

    @property
    def _optimization_dictionary(self) -> CfgDict:
        return self._cfg["optimization_dictionary"]

    @property
    def _parameters(self) -> List[CfgDict]:
        return self._optimization_dictionary["parameters"]

    @property
    def _pulses(self) -> List[CfgDict]:
        if not self.is_pulse_optimization:
            raise InvalidConfigurationException(
                "Pulses can be defined only with pulse optimization algorithm")
        return self._optimization_dictionary["pulses"]

    @property
    def _times(self) -> List[CfgDict]:
        if not self.is_pulse_optimization:
            raise InvalidConfigurationException(
                "Times can be defined only with pulse optimization algorithm")
        return self._optimization_dictionary["times"]

    @property
    def optimization_algorithm_name(self):
        """Optimization algorithm name"""
        return self._optimization_dictionary["opti_algorithm_name"]

    def validate(self):
        if self.is_pulse_optimization:
            if len(self._pulses) == 0:
                raise InvalidConfigurationException(
                    f"{self.optimization_algorithm_name=} but no pulses specified")

            referenced_times = PulseBuilder._get_time_names(self._pulses)
            defined_times = TimeBuilder._get_time_names(self._times)

            undefined = referenced_times.difference(defined_times)
            if len(undefined) > 0:
                raise InvalidConfigurationException(
                    f"Times referenced by pulses but defined: {undefined}")

            unused = defined_times.difference(referenced_times)
            if len(unused) > 0:
                raise InvalidConfigurationException(f"Times unused by pulses: {unused}")
        else:
            if len(self._parameters) == 0:
                raise InvalidConfigurationException(
                    f"{self.optimization_algorithm_name=} but no optimization parameter specified")

    @property
    def is_pulse_optimization(self):
        """Get whether the configuration is a pulse optimization configuration"""
        return self.optimization_algorithm_name == "dCRAB"

    @staticmethod
    def _create_cfg_dcrab(name: str):
        return {
            "optimization_dictionary": {
                "optimization_client_name": name,
                "opti_algorithm_name": "dCRAB",
                "opti_algorithm_module": "quocslib.optimalalgorithms.dCRABAlgorithm",
                "opti_algorithm_class": "DCrabAlgorithm",
                "algorithm_settings": DCRABSettingsBuilder._create_cfg(),
                "dsm_settings": DSMSettingsBuilder._create_cfg(),
                "pulses": [],
                "times": [],
                "parameters": []
            },
            "communication": {
                "communication_type": "AllInOneCommunication"
            },
            "figure_of_merit": ConfigurationBuilder._create_cfg_fom()
        }

    @staticmethod
    def _create_cfg_parameter(name):
        return {
            "optimization_dictionary": {
                "optimization_client_name": name,
                "opti_algorithm_name": "DirectSearchMethod",
                "opti_algorithm_module": "quocslib.optimalalgorithms.DirectSearchAlgorithm",
                "opti_algorithm_class": "DirectSearchAlgorithm",
                "dsm_settings": DSMSettingsBuilder._create_cfg(),
                "pulses": [],
                "times": [],
                "parameters": []
            },
            "communication": {
                "communication_type": "AllInOneCommunication"
            },
            "figure_of_merit": ConfigurationBuilder._create_cfg_fom()
        }

    @staticmethod
    def _create_cfg_fom():
        return {
            "further_args": [],
            "program_type": "ClientDefined"
        }


class ExperimentBuilder(Builder):

    def __init__(
        self,
        name: str,
        description: str,
        configuration: str,
        **kwargs,
    ) -> None:
        self._name = name
        self._description = description
        self._configuration = configuration
        self._extentions = kwargs

    @property
    def name(self) -> str:
        """Gets and sets the experiment name."""
        return self._name

    @name.setter
    def name(self, value: str):
        if value is None:
            raise InvalidConfigurationException("name must not be empty")
        self._name = value

    @property
    def description(self) -> str:
        """Gets and sets the experiment description."""
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @contextmanager
    def configuration(self):
        """
        Returns
        -------
        ConfigurationBuilder
            A configuration builder."""
        cfg = json.loads(self._configuration)
        builder = ConfigurationBuilder(cfg)
        yield builder
        builder.validate()
        self._configuration = json.dumps(cfg)

    def validate(self):
        if self._configuration is None:
            raise InvalidConfigurationException("configuration is empty")
        if self._name is None:
            raise InvalidConfigurationException("name must not be empty")
        # Make sure the name matches
        cfg = json.loads(self._configuration)
        cfg["optimization_dictionary"]["optimization_client_name"] = self._name
        self._configuration = json.dumps(cfg)

    def to_dict(self) -> CfgDict:
        """Un-structures the experiment builder for persistance or de-serialization."""
        return {
            "name": self._name,
            "description": self._description,
            "configuration": self._configuration,
            **self._extentions
        }

    @staticmethod
    def _new_pulse_optimization(name: str, description: str):
        configuration = json.dumps(ConfigurationBuilder._create_cfg_dcrab(name))
        return ExperimentBuilder(name=name, description=description, configuration=configuration)

    @staticmethod
    def _new_parameter_optimization(name: str, description: str):
        configuration = json.dumps(ConfigurationBuilder._create_cfg_parameter(name))
        return ExperimentBuilder(name=name, description=description, configuration=configuration)
