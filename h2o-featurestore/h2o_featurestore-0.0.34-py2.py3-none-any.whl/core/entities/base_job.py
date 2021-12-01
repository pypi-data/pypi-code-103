import json
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from .. import CoreService_pb2 as pb
from .. import interactive_console
from ..utils import Utils


class BaseJob(ABC):
    def __init__(self, stub, job_id):
        self._stub = stub
        self._job_id = job_id
        self._result = None
        self._job = self._stub.GetJob(self._job_id)
        self._progress = interactive_console.Progress(self._stub, self._job_id)
        self._thread_pool = ThreadPoolExecutor(5)

    @property
    def id(self):
        return self._job_id.job_id

    @property
    def job_type(self):
        return pb.JobType.Name(self._job.job_type)

    @property
    def done(self):
        return self.is_done()

    @abstractmethod
    def _response_method(self):
        raise NotImplementedError(
            "Method `_response_method` needs to be implemented by the child class"
        )

    def is_done(self) -> bool:
        return self._stub.GetJob(self._job_id).done

    def get_result(self):
        if not self._result:
            if not self.is_done():
                raise Exception("Job has not finished yet!")
            self._result = self._response_method(self._job_id)
        return self._result

    def show_progress(self):
        self._progress.show()

    def __repr__(self):
        return f"""Job(id={self.id}, type={self.job_type}, done={self.done})"""
