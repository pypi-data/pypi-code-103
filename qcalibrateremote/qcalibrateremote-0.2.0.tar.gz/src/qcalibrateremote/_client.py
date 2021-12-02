#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import inspect
import logging
from contextlib import contextmanager
from typing import ContextManager, Iterable, Optional, Type, TypeVar, Union

import numpy as np
from cuid import cuid
from icecream import ic

from ._browser import BrowserPresenter
from ._buffer import QueueBuffer
from ._endpoint import EndpointSecureKey
from ._fom import EvaluateFigureOfMerit, EvaluateFigureOfMeritFactory, Pulse
from ._grpc import qcalibrate_pb2 as pb2
from ._grpc.qcalibrate_pb2_grpc import QCalibrateStub
from ._observer import OptimizationObserver, OptimizationResultCollector
from .builders import ExperimentBuilder


def _is_request_end(request: pb2.Request) -> bool:
    return request.HasField('end')


#:TypeVar("T"): Type variable serving as a parameter for an optimization observer type.
TObserver = TypeVar('TObserver', bound=OptimizationObserver)

OpenBrowserOption = Union[None, bool]


class RemoteClientException(Exception):
    pass


class _OptimizationRunner:

    def __init__(
        self,
        stub: QCalibrateStub,
        experiment_id: str,
        evaluate_fom_factory: EvaluateFigureOfMeritFactory,
        process_timeout: float,
        observers: Iterable[OptimizationObserver],
        configuration: Optional[str] = None,
    ) -> None:

        self._stub = stub
        self._experiment_id = experiment_id
        self._evaluate_fom_factory = evaluate_fom_factory
        self._fom: EvaluateFigureOfMerit = None
        self._process_timeout = process_timeout
        self._buffer = QueueBuffer[pb2.Request](
            is_end=_is_request_end,
            timeout=process_timeout)
        self._configuration = configuration
        self._initialized: pb2.Initialized = None
        self._session_id = cuid()
        self._observers = observers

    def _send(self, request: pb2.Request) -> None:
        ic()
        ic(request)
        self._buffer.put(request)

    def _create_fom(self, initialized: pb2.Initialized) -> None:
        self._initialized = initialized

        for observer in self._observers:
            observer.on_start(
                run_id=initialized.run_id,
                configuration=initialized.configuration,
                parameter_metas=initialized.parameter_metas,
                pulse_metas=initialized.pulse_metas)

        arguments = initialized.arguments
        kvargs = {arg.name: getattr(arg, arg.WhichOneof(
            'value')) for arg in arguments}
        self._fom = self._evaluate_fom_factory(**kvargs)
        self._send(pb2.Request(start=pb2.Start()))

    def _evaluate_fom(self, parameters: pb2.Parameters) -> None:
        try:
            iteration = parameters.iteration
            merged_parameters = {k.name: v for (k, v) in zip(
                self._initialized.parameter_metas, parameters.values)}
            merged_pulses = {k.name: Pulse(np.array(v.times), np.array(v.values)) for (k, v) in zip(
                self._initialized.pulse_metas, parameters.pulses)}
            fom = self._fom.evaluate(
                parameters=merged_parameters, pulses=merged_pulses)

            for observer in self._observers:
                observer.on_iteration(
                    iteration=iteration,
                    parameters=merged_parameters,
                    pulses=merged_pulses,
                    figure_of_merit=fom.figure_of_merit,
                    data=fom.data)

            self._send(pb2.Request(fom=pb2.Fom(
                iteration=iteration,
                figure_of_merit=fom.figure_of_merit, data=fom.data)))

        except Exception as ex:
            logging.exception(ex)
            self._send(pb2.Request(end=pb2.End(
                typ=ex.__class__.__name__, error=str(ex))))

    def _end(self, typ: str = None, error: str = None):
        self._send(pb2.Request(end=pb2.End(typ=typ, error=error)))

    def run(self):
        ic(self._experiment_id, self._session_id)
        self._buffer.put(pb2.Request(initialize=pb2.Initialize(
            experiment_id=self._experiment_id, session_id=self._session_id, configuration=self._initialized)))

        response_stream = self._stub.Run(self._buffer.get())
        self._run_loop(response_stream)

    def _run_loop(self, response_stream: Iterable[pb2.Response]) -> None:
        try:
            response: pb2.Response

            for response in response_stream:
                message = response.WhichOneof('message')
                if message == 'initialized':
                    self._create_fom(response.initialized)
                elif message == 'parameters':
                    self._evaluate_fom(response.parameters)
                elif message == 'end':
                    # signal to producer to close
                    self._buffer.put(None)
                    if response.end.error:
                        raise RemoteClientException(
                            "Error during execution {}".format(response.end.error))
                else:
                    raise Exception(message="Invalid message", arg=message)

            for observer in self._observers:
                observer.on_end()

        except RemoteClientException as ex:
            # ic()
            # ic(traceback.format_exc(ex))
            for observer in self._observers:
                observer.on_error(exception=ex)
            raise
        except Exception as ex:

            logging.exception(ex)
            # ic()
            # ic(traceback.format_exc(ex))
            self._end(typ=ex.__class__.__name__, error=str(ex))  # end cycle
            for observer in self._observers:
                observer.on_error(exception=ex)
        finally:
            if self._fom:
                self._fom.close()


class InconsistencyException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class QOptimizerClient:
    """Interface to an remote QCalibrate optimizer
    """

    def __init__(self, stub: QCalibrateStub, browser_presenter: Optional[BrowserPresenter] = None, remote_timeout: float = None):
        """Constructs optimization clients
        """
        self._stub = stub
        self._browser_presenter = browser_presenter
        self._process_timeout = remote_timeout

    def create_pulse_optimization_experiment(self, name: str, description: str = None) -> ExperimentBuilder:
        """Creates a pulse optimization experiment builder
        use :meth:`~QOptimizerClient.add_experiment` to upload it to backend

        Parameters
        ----------
        name : str
            experiment name
        description : str, optional
            experiment description

        Examples
        ---------        
        Example creating a simple parameter optimization experiment

        .. code-block:: python
        
            experiment = optimizer_client.create_pulse_optimization_experiment("Example1")
        
            with experiment.configuration() as configuration:
                with configuration.time("time1") as time1:
                    time1.initial_value = 1
                    time1.optimize = False
                with configuration.parameter("pulse1") as pulse1:
                    pulse1.time_name = "time1"
                    pulse1.lower_limit = -1
                    pulse1.upper_limit = 1
                    pulse1.bins_number = 101       
                    with pulse1.initial_guess() as initial_guess:
                        initial_guess.function = "lambda t: 1"
                    with pulse1.scaling_function() as scaling_function:
                        scaling_function.function = "lambda t: np.exp(-(t - 0.5)**2/(2*0.2**2))"
                    with pulse1.fourier_basis() as fourier_basis:
                        fourier_basis.basis_vector_number = 5
                        with fourier_basis.uniform_super_parameter_distribution() as uniform_super_parameter_distribution:
                            uniform_super_parameter_distribution.lower_limit = 0.01
                            uniform_super_parameter_distribution.upper_limit = 5
                with configuration.dcrab_settings() as dcrab_settings:
                    dcrab_settings.maximum_iterations_per_super_iteration = 50
                    dcrab_settings.super_iteration_number = 6
                    
            experiment_id = optimizer_client.add_experiment(experiment)

        Returns
        -------
        ExperimentBuilder
            the experiment builder object
        """
        return ExperimentBuilder._new_pulse_optimization(name=name, description=description)

    def create_parameter_optimization_experiment(self, name: str, description: str = None) -> ExperimentBuilder:
        """Creates a parameter optimization experiment builder
        use :meth:`~QOptimizerClient.add_experiment` to upload it to backend

        Parameters
        ----------
        name : str
            experiment name
        description : str, optional
            experiment description

        Examples
        ---------        
        Example creating a simple parameter optimization experiment

        .. code-block:: python
        
            experiment = optimizer_client.create_parameter_optimization_experiment("Example experiment")
        
            with experiment.configuration() as configuration:            
                with configuration.parameter("parameter1") as parameter1:
                    parameter1.initial_value = 0.1                    
                with configuration.direct_search_method_settings() as dsm_settings:
                    with dsm_settings.stopping_criteria() as stopping_criteria:
                        stopping_criteria.iterations_number = 30
                    
            experiment_id = optimizer_client.add_experiment(experiment)


        Returns
        -------
        ExperimentBuilder
            the experiment builder object
        """
        return ExperimentBuilder._new_parameter_optimization(name=name, description=description)

    def add_experiment(self, builder: ExperimentBuilder) -> str:
        """Validates and saves an experiment defined by an experiment builder

        Parameters
        ----------
        builder : ExperimentBuilder
            experiment builder object to be saved to the backend


        Examples
        ---------
        Example creating a simple parameter optimization experiment

        .. code-block:: python
        
            experiment = optimizer_client.create_parameter_optimization_experiment("Example experiment")
        
            with experiment.configuration() as configuration:
                with configuration.parameter("parameter1") as parameter1:
                    parameter1.initial_value = 0.1
                    
            experiment_id = optimizer_client.add_experiment(experiment)

        Returns
        -------
        str
            experiment_id, to be used as an argument on :meth:`~QOptimizerClient.run` to run the optimization
        """
        builder.validate()
        request = pb2.AddExperimentRequest(**builder.to_dict())
        result = self._stub.AddExperiment(request)
        return result.experiment_id

    @contextmanager
    def update_experiment(self, experiment_id: str):
        """Creates a builder context to modify an existing experiment

        Parameters
        ----------
        experiment_id : str
            Id of an experiment to modify 

        Returns
        -------
        ContextManager[ExperimentBuilder]
            the experiment builder object

        Examples
        ---------
        Example changing the initial value of a parameter

        .. code-block:: python
        
            with optimizer_client.update_experiment(experiment_id=experiment_id) as experiment:
                with experiment.configuration() as cfg:
                    with cfg.parameter("parameter1") as parameter1:
                        parameter1.initial_value = 0.1

        Raises
        ------
        InvalidConfigurationException
            Validation of the configuration failed
        InconsistencyException
            Configuration could ot be stored (eventually deleted)
        """

        request = pb2.GetExperimentRequest(experiment_id=experiment_id)
        experiment: pb2.GetExperimentResult = self._stub.GetExperiment(request)

        builder = ExperimentBuilder(
            experiment_id=experiment_id,
            name=experiment.name,
            description=experiment.description,
            configuration=experiment.configuration
        )
        yield builder
        builder.validate()
        result = self._stub.UpdateExperiment(
            pb2.UpdateExperimentRequest(**builder.to_dict()))
        if not result.success:
            raise InconsistencyException("Update experiment update failed")

    def run(
            self,
            experiment_id: str,
            evaluate_fom_class: Optional[Union[Type[EvaluateFigureOfMerit],
                                               EvaluateFigureOfMeritFactory]] = None,
            evaluate_fom_object: Optional[EvaluateFigureOfMerit] = None,
            observer: Union[Type[TObserver], TObserver] = OptimizationResultCollector,
            debug=False,
            show_progress: OpenBrowserOption = False,
    ) -> TObserver:
        """Runs an optimization using a remote optimizer, evaluates figure of merit locally use specified class
        class is instantiated with optional arguments, specified in the the experiment configuration.

        Parameters
        ----------
        experiment_id : str
            the experiment id, used to configure the optimizer 
        evaluate_fom_class : Optional[Union[Type[EvaluateFigureOfMerit], EvaluateFigureOfMeritFactory]]
            class to evaluate figure of merit, must be specified if evaluate_fom_object is None
        evaluate_fom_object: Optional[EvaluateFigureOfMerit]
            object to evaluate figure of merit (optional), must be specified if evaluate_fom_class is None
        observer : OptimizationObserver
            class or object to observe and accumulate optimization results, default :py:class:`OptimizationResultCollector`
        debug : bool, optional
            Enables addition logs, can help debugging the issues, by default False
        show_progress : bool, optional
            Open browser with run details (if running in a notebook), by default False

        Returns
        -------
        TObserver
            The observer object object specified by the 'observer' parameter, by default returns an instance of :py:class:`OptimizationResultCollector`
        """

        if inspect.isclass(observer):
            observer_instance: TObserver = observer()
        else:
            observer_instance: TObserver = observer

        observers = [observer_instance]
        if show_progress and self._browser_presenter:
            observers.append(self._browser_presenter)

        if evaluate_fom_class is None:
            if evaluate_fom_object is None:
                raise ValueError(
                    "Either evaluate_fom_class or evaluate_fom_object must be specified!")
            else:
                evaluate_fom_factory = lambda **kvargs: evaluate_fom_object
        else:
            if evaluate_fom_object is None:
                evaluate_fom_factory = evaluate_fom_class
            else:
                raise ValueError(
                    "Don not specify both evaluate_fom_class and evaluate_fom_object!")

        was_enabled = ic.enabled
        if not debug:
            ic.disable()
        try:
            _OptimizationRunner(
                stub=self._stub,
                experiment_id=experiment_id,
                evaluate_fom_factory=evaluate_fom_factory,
                process_timeout=self._process_timeout,
                observers=observers,
            ).run()
            return observer_instance
        finally:
            if was_enabled:
                ic.enable()


def create_optimizer_client(
        host: str,
        port: int,
        token: str,
        ca_cert: Union[bytes, str] = None,
        remote_timeout: float = None
) -> QOptimizerClient:
    """Creates remote optimizer client

    Parameters
    ----------
    host : str
        endpoint host
    port : int
        endpoint port
    token : str
        client authentication token
    ca_cert : Union[bytes, str], optional
        server CA certificate file content or certificate file name (.pem)
        used to verify server identity in case it uses a self-signed server certificate
        default None
    process_timeout : float, optional
        Timeout in seconds to wait for a remote reply, by default None - wait forever

    Returns
    -------
    QOptimizerClient
        creates remote optimizer client object
    """
    endpoint = EndpointSecureKey(host=host, port=port, token=token, ca_cert=ca_cert)

    browser_presenter = BrowserPresenter.from_endpoint(host, port)
    stub = QCalibrateStub(endpoint.create_channel())

    return QOptimizerClient(stub=stub, browser_presenter=browser_presenter, remote_timeout=remote_timeout)
