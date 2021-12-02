import json

import pytest
from cuid import cuid
from mock import MagicMock
from qcalibrateremote._browser import BrowserPresenter
from qcalibrateremote._client import QOptimizerClient, _OptimizationRunner
from qcalibrateremote._fom import (EvaluateFigureOfMerit,
                                   EvaluateFigureOfMeritFactory, FigureOfMerit)
from qcalibrateremote._grpc import qcalibrate_pb2 as pb2
from qcalibrateremote._grpc.qcalibrate_pb2_grpc import QCalibrateStub
from qcalibrateremote._observer import OptimizationObserver


@pytest.fixture
def fom() -> FigureOfMerit:
    return FigureOfMerit(0.5, '{"ab":7}')


@pytest.fixture
def evaluate_fom(fom) -> EvaluateFigureOfMerit:
    fixture = MagicMock(spec=EvaluateFigureOfMerit)
    fixture.evaluate.return_value = fom
    return fixture


@pytest.fixture
def evaluate_fom_factory(evaluate_fom) -> EvaluateFigureOfMerit:
    fixture = MagicMock(spec=EvaluateFigureOfMeritFactory)
    fixture.return_value = evaluate_fom
    return fixture


@pytest.fixture
def stub():
    return MagicMock()


@pytest.fixture
def observer():
    return MagicMock(spec=OptimizationObserver)


@pytest.fixture
def presenter():
    return MagicMock(spec=BrowserPresenter)


@pytest.fixture
def runner(observer, stub, evaluate_fom_factory):
    return _OptimizationRunner(
        stub=stub,
        experiment_id='experiment_id',
        evaluate_fom_factory=evaluate_fom_factory,
        process_timeout=3600,
        observers=[observer]
    )


@pytest.fixture
def parameters_message() -> pb2.Parameters:
    message = pb2.Parameters(
        iteration=77,
        values=[2.2, 3.3],
        pulses=[
            pb2.Pulse(times=[0, 0.5, 1], values=[0, 0.7, 0]),
            pb2.Pulse(times=[0, 0.5, 1], values=[0, -0.3, 0]),
        ],
    )

    return pb2.Response(parameters=message)


@pytest.fixture
def initialized_message() -> pb2.Response:
    message = pb2.Initialized(
        experiment_id='experiment_id',
        run_id='1234',
        typ="TestType",
        module_name="testfom",
        class_name="TestFom",
        arguments=[
            pb2.Argument(name="PI", double=3.14),
            pb2.Argument(name="TAG", string="tag1"),
        ],
        configuration='{"dummy":7}',
        parameter_metas=[
            pb2.ParameterMeta(index=0, name="param1", configuration="dataParam1"),
            pb2.ParameterMeta(index=1, name="param2", configuration="dataParam2"),
        ],
        pulse_metas=[
            pb2.PulseMeta(index=0, name="pulse1", configuration="dataPulse1"),
            pb2.PulseMeta(index=1, name="pulse2", configuration="dataPulse2"),
        ],
    )
    return pb2.Response(initialized=message)


@pytest.fixture
def end_message_without_error() -> pb2.Response:
    return pb2.Response(end=pb2.End())


@pytest.fixture
def end_message_with_error() -> pb2.Response:
    return pb2.Response(end=pb2.End(typ=Exception.__class__.__name__, error='Some error'))


@pytest.fixture
def client(stub):
    return QOptimizerClient(stub)


def test_run_without_error(initialized_message, parameters_message, end_message_without_error, stub, runner):
    stub.Run.return_value = (
        [initialized_message, parameters_message, end_message_without_error])
    runner.run()


def test_run_with_error(initialized_message, parameters_message, end_message_with_error, stub, runner):
    stub.Run.return_value = (
        [initialized_message, parameters_message, end_message_with_error])
    with pytest.raises(Exception):
        runner.run()


def test_create_pulse_experiment(stub: QCalibrateStub, client: QOptimizerClient):
    # Arrange

    expected_experiment_id = cuid()

    stub.AddExperiment.return_value = pb2.AddExperimentResult(
        experiment_id=expected_experiment_id)

    # Act
    experiment = client.create_pulse_optimization_experiment("Experiment-99")
    experiment.description = "Some Description"

    with experiment.configuration() as cfg:
        with cfg.parameter("Param1") as param1:
            param1.lower_limit = -2
            param1.upper_limit = 2
            param1.initial_value = 0.15
            param1.initial_variation = 1.1

        with cfg.time("tick") as tick:
            tick.initial_value = 32
            tick.optimize = False

        with cfg.pulse("I") as pulse1:
            pulse1.lower_limit = -7
            pulse1.upper_limit = 7
            pulse1.bins_number = 9
            pulse1.initial_variation = 5.5
            with pulse1.initial_guess() as initial_guess:
                initial_guess.function = "lambda t: -0.07"
            with pulse1.scaling_function() as scaling_function:
                scaling_function.function = "lambda t: -(t - 16)/8 * np.exp(0.5) * np.exp(-(t - 16)**2/(2*8**2))"
            pulse1.time_name = "tick"

            with pulse1.fourier_basis() as basis:
                basis.basis_vector_number = 3
                with basis.uniform_super_parameter_distribution() as distribution:
                    distribution.lower_limit = 0.05
                    distribution.upper_limit = 5

        with cfg.dcrab_settings() as dcrab_settings:
            dcrab_settings.super_iteration_number = 3
            dcrab_settings.maximum_iterations_per_super_iteration = 11

        with cfg.direct_search_method_settings() as dsm_settings:
            dsm_settings.is_adaptive = False

    experiment_id = client.add_experiment(experiment)

    # Assert

    assert experiment_id == expected_experiment_id

    request: pb2.AddExperimentRequest = stub.AddExperiment.call_args_list[0].args[0]
    assert isinstance(request, pb2.AddExperimentRequest)
    assert request.name == "Experiment-99"
    assert request.description == "Some Description"

    cfg = json.loads(request.configuration)
    assert cfg == {
        "optimization_dictionary": {
            "optimization_client_name": "Experiment-99",
            "opti_algorithm_name": "dCRAB",
            "opti_algorithm_module": "quocslib.optimalalgorithms.dCRABAlgorithm",
            "opti_algorithm_class": "DCrabAlgorithm",
            "algorithm_settings": {
                "super_iteration_number": 3,
                "maximum_function_evaluations_number": 11
            },
            "dsm_settings": {
                "general_settings": {
                    "dsm_name": "nelder_mead",
                    "is_adaptive": False
                },
                "stopping_criteria": {
                    "iterations_number": 100,
                    "xatol": 1e-13,
                    "frtol": 1e-13
                }
            },
            "pulses": [
                {
                    "pulse_name": "I",
                    "upper_limit": 7.0,
                    "lower_limit": -7.0,
                    "bins_number": 9,
                    "time_name": "tick",
                    "amplitude_variation": 5.5,
                    "basis": {
                        "basis_name": "Fourier",
                        "basis_class": "Fourier",
                        "basis_module": "quocslib.pulses.basis.Fourier",
                        "basis_vector_number": 3,
                        "random_super_parameter_distribution": {
                            "distribution_name": "Uniform",
                            "distribution_class": "Uniform",
                            "distribution_module": "quocslib.pulses.super_parameter.Uniform",
                            "lower_limit": 0.05,
                            "upper_limit": 5.0
                        },
                    },
                    "scaling_function": {
                        "function_type": "lambda_function",
                        "lambda_function": "lambda t: -(t - 16)/8 * np.exp(0.5) * np.exp(-(t - 16)**2/(2*8**2))"
                    },
                    "initial_guess": {
                        "function_type": "lambda_function",
                        "lambda_function": "lambda t: -0.07"
                    }
                }
            ],
            "times": [
                {
                    "time_name": "tick",
                    "initial_value": 32,
                    "is_optimization": False
                }
            ],
            "parameters": [
                {
                    "parameter_name": "Param1",
                    "lower_limit": -2.0,
                    "upper_limit": 2.0,
                    "initial_value": 0.15,
                    "amplitude_variation": 1.1
                }
            ]
        },
        "communication": {
            "communication_type": "AllInOneCommunication"
        },
        "figure_of_merit": {
            "further_args": [],
            "program_type": "ClientDefined"
        }
    }


def test_create_parameter_experiment(stub: QCalibrateStub, client: QOptimizerClient):
    # Arrange

    expected_experiment_id = cuid()

    stub.AddExperiment.return_value = pb2.AddExperimentResult(
        experiment_id=expected_experiment_id)

    # Act
    experiment = client.create_parameter_optimization_experiment("Experiment-98")
    experiment.description = "Some Other Description"

    with experiment.configuration() as cfg:
        with cfg.parameter("Param1") as param1:
            param1.lower_limit = -3
            param1.upper_limit = 3
            param1.initial_value = 0.27
            param1.initial_variation = 1.2
        with cfg.direct_search_method_settings() as dsm_settings:
            dsm_settings.is_adaptive = True
            with dsm_settings.stopping_criteria() as stopping_criteria:
                stopping_criteria.iterations_number = 123
                stopping_criteria.xatol = 1.1e-13
                stopping_criteria.frtol = 2.2e-13

    experiment_id = client.add_experiment(experiment)

    # Assert

    assert experiment_id == expected_experiment_id

    request: pb2.AddExperimentRequest = stub.AddExperiment.call_args_list[0].args[0]
    assert isinstance(request, pb2.AddExperimentRequest)
    assert request.name == "Experiment-98"
    assert request.description == "Some Other Description"

    cfg = json.loads(request.configuration)
    assert cfg == {
        "optimization_dictionary": {
            "optimization_client_name": "Experiment-98",
            "opti_algorithm_name": "DirectSearchMethod",
            "opti_algorithm_module": "quocslib.optimalalgorithms.DirectSearchAlgorithm",
            "opti_algorithm_class": "DirectSearchAlgorithm",
            "dsm_settings": {
                "general_settings": {
                    "dsm_name": "nelder_mead",
                    "is_adaptive": True
                },
                "stopping_criteria": {
                    "iterations_number": 123,
                    "xatol": 1.1e-13,
                    "frtol": 2.2e-13
                }
            },
            "pulses": [],
            "times": [],
            "parameters": [
                {
                    "parameter_name": "Param1",
                    "lower_limit": -3,
                    "upper_limit": 3,
                    "initial_value": 0.27,
                    "amplitude_variation": 1.2
                }
            ]
        },
        "communication": {
            "communication_type": "AllInOneCommunication"
        },
        "figure_of_merit": {
            "further_args": [],
            "program_type": "ClientDefined"
        }
    }


def test_update_parameter_experiment(stub: QCalibrateStub, client: QOptimizerClient):
    # Arrange
    experiment_id = cuid()

    stub.GetExperiment.return_value = pb2.GetExperimentResult(
        name="NameOld",
        description="DescriptionOld",
        configuration=json.dumps({
            "optimization_dictionary": {
                "optimization_client_name": "Experiment-98",
                "opti_algorithm_name": "DirectSearchMethod",
                "opti_algorithm_module": "quocslib.optimalalgorithms.DirectSearchAlgorithm",
                "opti_algorithm_class": "DirectSearchAlgorithm",
                "dsm_settings": {
                    "general_settings": {
                        "dsm_name": "nelder_mead",
                        "is_adaptive": True
                    },
                    "stopping_criteria": {
                        "iterations_number": 123,
                        "xatol": 1.1e-13,
                        "frtol": 2.2e-13
                    }
                },
                "pulses": [],
                "times": [],
                "parameters": [
                    {
                        "parameter_name": "Param1",
                        "lower_limit": -3,
                        "upper_limit": 3,
                        "initial_value": 0.27,
                        "amplitude_variation": 1.2
                    }
                ]
            },
            "communication": {
                "communication_type": "AllInOneCommunication"
            },
            "figure_of_merit": {
                "further_args": [],
                "program_type": "ClientDefined"
            }
        })
    )
    
    # Act

    with client.update_experiment(experiment_id) as experiment:
        experiment.name = "Experiment-99"
        experiment.description = "Some New Description"
        
        with experiment.configuration() as cfg:
            with cfg.parameter("Param2") as param1:
                param1.lower_limit = -2
                param1.upper_limit = 2
                param1.initial_value = 0.22
                param1.initial_variation = 1.3
            with cfg.direct_search_method_settings() as dsm_settings:
                with dsm_settings.stopping_criteria() as stopping_criteria:
                    stopping_criteria.iterations_number = 213
                    
    # Assert
    request_get: pb2.GetExperimentRequest = stub.GetExperiment.call_args_list[0].args[0]
    assert isinstance(request_get, pb2.GetExperimentRequest)
    assert request_get.experiment_id == experiment_id
    
    
    request_update: pb2.UpdateExperimentRequest = stub.UpdateExperiment.call_args_list[0].args[0]
    assert isinstance(request_update, pb2.UpdateExperimentRequest)
        
    assert request_update.experiment_id == experiment_id
    assert request_update.name == "Experiment-99"
    assert request_update.description == "Some New Description"
    cfg = json.loads(request_update.configuration)
    assert cfg == {
            "optimization_dictionary": {
                "optimization_client_name": "Experiment-99",
                "opti_algorithm_name": "DirectSearchMethod",
                "opti_algorithm_module": "quocslib.optimalalgorithms.DirectSearchAlgorithm",
                "opti_algorithm_class": "DirectSearchAlgorithm",
                "dsm_settings": {
                    "general_settings": {
                        "dsm_name": "nelder_mead",
                        "is_adaptive": True
                    },
                    "stopping_criteria": {
                        "iterations_number": 213,
                        "xatol": 1.1e-13,
                        "frtol": 2.2e-13
                    }
                },
                "pulses": [],
                "times": [],
                "parameters": [
                    {
                        "parameter_name": "Param1",
                        "lower_limit": -3,
                        "upper_limit": 3,
                        "initial_value": 0.27,
                        "amplitude_variation": 1.2
                    },
                    {
                        "parameter_name": "Param2",
                        "lower_limit": -2,
                        "upper_limit": 2,
                        "initial_value": 0.22,
                        "amplitude_variation": 1.3
                    }
                ]
            },
            "communication": {
                "communication_type": "AllInOneCommunication"
            },
            "figure_of_merit": {
                "further_args": [],
                "program_type": "ClientDefined"
            }
        }
        
