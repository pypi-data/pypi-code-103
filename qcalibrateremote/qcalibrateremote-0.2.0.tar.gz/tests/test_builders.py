
import numpy as np
import pytest
from qcalibrateremote.builders import (ConfigurationBuilder,
                                       InvalidConfigurationException,
                                       ParameterBuilder, PulseBuilder)


@pytest.fixture
def configuration_builder():
    return ConfigurationBuilder(ConfigurationBuilder._create_cfg_parameter("name"))


@pytest.fixture
def pulse_builder():
    cfg = {
        "pulse_name": "pulse1",
        "upper_limit": 15.0,
        "lower_limit": -15.0,
        "bins_number": 11,
        "time_name": "time1",
        "amplitude_variation": 0.5,
        "basis": {
            "basis_name": "Fourier",
            "basis_class": "Fourier",
            "basis_module": "quocslib.pulses.basis.Fourier",
            "basis_vector_number": 10,
            "random_super_parameter_distribution": {
                "distribution_name": "Uniform",
                "distribution_class": "Uniform",
                "distribution_module": "quocslib.pulses.super_parameter.Uniform",
                "lower_limit": 0.1,
                "upper_limit": 30.0
            }
        },
        "scaling_function": {
            "function_type": "lambda_function",
            "lambda_function": "lambda t: 1.0 + 0.0*t"
        },
        "initial_guess": {
            "function_type": "lambda_function",
            "lambda_function": "lambda t: np.pi/3 + 0.0*t"
        }
    }

    return PulseBuilder(cfg)


@pytest.fixture
def parameter_builder():
    return ParameterBuilder(ParameterBuilder._create_cfg("test"))


def test_PulseBuilder_invalid_scaling_function_throws(pulse_builder: PulseBuilder):

    with pytest.raises(InvalidConfigurationException) as e_info:
        with pulse_builder.scaling_function() as scaling_function:
            scaling_function.function = "yxjui"

    assert "yxjui" in e_info.value.args[0]


def test_PulseBuilder_scaling_function_lambda(pulse_builder: PulseBuilder):
    with pulse_builder.scaling_function() as scaling_function:
        scaling_function.function = "lambda t: 1.0"

    with pulse_builder.scaling_function() as scaling_function:
        assert scaling_function.type == "lambda_function"
        assert scaling_function.function == "lambda t: 1.0"


def test_PulseBuilder_scaling_function_lambda_numpy(pulse_builder: PulseBuilder):
    with pulse_builder.scaling_function() as scaling_function:
        scaling_function.function = "lambda t: np.pi"

    with pulse_builder.scaling_function() as scaling_function:
        assert scaling_function.type == "lambda_function"
        assert scaling_function.function == "lambda t: np.pi"


def test_PulseBuilder_scaling_function_lambda_scipy_throws(pulse_builder: PulseBuilder):
    with pytest.raises(InvalidConfigurationException):
        with pulse_builder.scaling_function() as scaling_function:
            scaling_function.function = "lambda t: scipy.pi"


def test_PulseBuilder_scaling_function_two_arguments_lambda_throws(pulse_builder: PulseBuilder):
    with pytest.raises(InvalidConfigurationException):
        with pulse_builder.scaling_function() as scaling_function:
            scaling_function.function = "lambda x,y: x*y"


def test_PulseBuilder_scaling_function_values(pulse_builder: PulseBuilder):
    with pulse_builder.scaling_function() as scaling_function:
        scaling_function.function = [0, 1.2, 2, 1.2, 0]

    with pulse_builder.scaling_function() as scaling_function:
        assert scaling_function.type == "list_function"
        assert scaling_function.function == [0, 1.2, 2, 1.2, 0]
        assert scaling_function._cfg[scaling_function.type] == "[0.0, 1.2, 2.0, 1.2, 0.0]"


def test_PulseBuilder_scaling_function_matrix_throws(pulse_builder: PulseBuilder):
    with pytest.raises(InvalidConfigurationException):
        with pulse_builder.scaling_function() as scaling_function:
            scaling_function.function = [[0, 1.2], [2, 1.2]]


def test_PulseBuilder_scaling_function_ndarray(pulse_builder: PulseBuilder):
    with pulse_builder.scaling_function() as scaling_function:
        scaling_function.function = np.asarray([0, 1, 2, 1, 0])

    with pulse_builder.scaling_function() as scaling_function:
        assert scaling_function.type == "list_function"
        assert scaling_function.function == [0, 1, 2, 1, 0]
        assert scaling_function._cfg[scaling_function.type] == "[0, 1, 2, 1, 0]"


def test_ConfigurationBuilder_AddParameter(configuration_builder):
    with configuration_builder.parameter("P1") as p1:
        p1.lower_limit = -0.1
        p1.initial_value = 0.1
        p1.upper_limit = 0.7
        p1.initial_variation = 0.05

    with configuration_builder.parameter("P1") as p1:
        assert p1.name == "P1"
        assert p1.lower_limit == -0.1
        assert p1.initial_value == 0.1
        assert p1.upper_limit == 0.7
        assert p1.initial_variation == 0.05


def test_ConfigurationBuilder_parameter_with_name_duplicate_throws():
    builder = ConfigurationBuilder(ConfigurationBuilder._create_cfg_parameter("name"))
    with builder.parameter("P1") as p1:
        p1.lower_limit = -0.1
        p1.initial_value = 0.1
        p1.upper_limit = 0.7
        p1.initial_variation = 0.05

    # duplicate a parameter
    builder._parameters.append(builder._parameters[0])

    with pytest.raises(InvalidConfigurationException):
        with builder.parameter("P1") as p1:
            p1.initial_value == 0.0


def test_PulseBuilder_parameter_with_name_duplicate_throws():
    builder = ConfigurationBuilder(ConfigurationBuilder._create_cfg_parameter("name"))
    with builder.parameter("P1") as p1:
        p1.lower_limit = -0.1
        p1.initial_value = 0.1
        p1.upper_limit = 0.7
        p1.initial_variation = 0.05

    # duplicate a parameter
    builder._parameters.append(builder._parameters[0])

    with pytest.raises(InvalidConfigurationException):
        with builder.parameter("P1") as p1:
            p1.initial_value == 0.0


def test_ParameterBuilder_initial_value_higher_than_upper_limit_validate_throws(parameter_builder: ParameterBuilder):
    parameter_builder.initial_value = parameter_builder.upper_limit + 0.1
    with pytest.raises(InvalidConfigurationException):
        parameter_builder.validate()


def test_ParameterBuilder_initial_value_lower_than_lower_limit_validate_throws(parameter_builder: ParameterBuilder):
    parameter_builder.initial_value = parameter_builder.lower_limit - 0.1
    with pytest.raises(InvalidConfigurationException):
        parameter_builder.validate()


def test_ParameterBuilder_initial_value_equal_to_lower_and_upper_limits_validate_throws(parameter_builder: ParameterBuilder):
    parameter_builder.lower_limit = parameter_builder.initial_value
    parameter_builder.upper_limit = parameter_builder.initial_value
    with pytest.raises(InvalidConfigurationException):
        parameter_builder.validate()


def test_ParameterBuilder_variation_bigger_than_range_validate_throws(parameter_builder: ParameterBuilder):
    parameter_builder.initial_variation = parameter_builder.upper_limit - \
        parameter_builder.lower_limit + 0.1
    with pytest.raises(InvalidConfigurationException):
        parameter_builder.validate()
