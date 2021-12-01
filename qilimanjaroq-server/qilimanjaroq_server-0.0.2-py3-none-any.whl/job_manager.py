# job_manager.py

from abc import ABC
from qilimanjaroq_server.typings.job import JobRequest, JobResponse
from qilimanjaroq_server.typings.algorithm import AlgorithmDefinition, AlgorithmOptions, InitialValue, ProgramDefinition
from .program import Program
from qilimanjaroq_server.util import base64url_decode, base64url_encode
import json


class JobManager(ABC):
    """ class to handle all job operations and responsible to
        create the concrete algorithms that the job requires

    """

    def __init__(self, job_request: JobRequest) -> None:
        self._job_request = job_request

        algorithm_definitions = base64url_decode(self._job_request.description)
        algorithms_created = [AlgorithmDefinition(
            name=algorithm_definition['name'],
            type=algorithm_definition['type'],
            options=AlgorithmOptions(
                number_qubits=algorithm_definition['options']['number_qubits'],
                initial_value=InitialValue(algorithm_definition['options']['initial_value'])
            )
        )
            for algorithm_definition in algorithm_definitions]
        self._program = Program(
            program_definition=ProgramDefinition(algorithms=algorithms_created))

    def execute(self) -> JobResponse:
        job_results = self._program.execute(backend=self._job_request.backend)
        serialized_job_results = [base64url_encode(job_result.dumps()) for job_result in job_results]

        return JobResponse(
            description=self._job_request.description,
            result=base64url_encode(json.dumps(serialized_job_results))
        )
