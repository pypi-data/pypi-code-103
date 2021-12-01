from base64 import urlsafe_b64decode
from qilimanjaroq_server.typings.job import JobRequest, JobBackend, JobResponse
from qilimanjaroq_server.job_manager import JobManager
from qilimanjaroq_server.util import base64url_decode
import numpy as np


def test_a_job_execution():
    job_description = 'W3sibmFtZSI6ICJiZWxsLXN0YXRlIiwgInR5cGUiOiAiR2F0ZS1CYXNlZCBDaXJjdWl0IiwgIm9wdGlvbnMiOiB7Im51bWJlcl9xdWJpdHMiOiAyLCAiaW5pdGlhbF92YWx1ZSI6ICJvbmUifX1d'
    job_result = JobManager(job_request=JobRequest(
        description=job_description,
        backend=JobBackend.SIMULATOR)).execute()

    assert isinstance(job_result, JobResponse)
    assert job_result.description == job_description
    decoded_results = base64url_decode(job_result.result)
    decoded_results = [np.loads(urlsafe_b64decode(decoded_result))
                       for decoded_result in decoded_results]
    assert [decoded_results == np.array([1, 0, 0, 0]) for decoded_results in decoded_results]
