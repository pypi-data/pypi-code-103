"""Library to initiate backend RIME service requests."""

import csv
import time
from datetime import datetime
from typing import Any, Dict, List, NamedTuple, Optional

import grpc
import simplejson
from google.protobuf.json_format import MessageToDict
from semver import VersionInfo

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.internal.throttle_queue import ThrottleQueue
from rime_sdk.protos.model_testing.model_testing_pb2 import (
    CustomImage,
    GetLatestLogsRequest,
    GetTestJobRequest,
    JobMetadata,
    JobStatus,
    ListTestJobsRequest,
    StartStressTestRequest,
)
from rime_sdk.protos.results_upload.results_upload_pb2 import (
    CreateProjectRequest,
    GetTestRunResultCSVRequest,
    GetTestRunResultCSVResponse,
    VerifyProjectIDRequest,
)
from rime_sdk.protos.test_run_tracker.test_run_tracker_pb2 import (
    GetOperationStateRequest,
    GetOperationStateResponse,
    OperationStatus,
)
from rime_sdk.protos.test_run_tracker.test_run_tracker_pb2_grpc import (
    TestRunTrackerStub,
)

default_csv_header = ["test_name", "feature(s)", "status"]


class RIMEStressTestJob:
    """An interface to a RIME stress testing job."""

    def __init__(self, backend: RIMEBackend, job_id: str,) -> None:
        """Create a new RIME Job.

        Args:
            backend: RIMEBackend
                The RIME backend used to query about the status of the job.
            job_id: str
                The identifier for the RIME job that this object monitors.
        """
        self._backend = backend
        self._job_id = job_id

    def __eq__(self, obj: Any) -> bool:
        """Check if this job is equivalent to 'obj'."""
        # Always compare start times in UTC timezone for consistency in tests.
        return isinstance(obj, RIMEStressTestJob) and self._job_id == obj._job_id

    def _get_progress(self, test_tracker: TestRunTrackerStub) -> Optional[str]:
        """Pretty print the progress of the test run."""
        op_res: Optional[GetOperationStateResponse] = None
        try:
            op_req = GetOperationStateRequest(job_id=self._job_id)
            op_res = test_tracker.GetOperationState(op_req)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            else:
                raise e
        if op_res:
            total_batches = len(op_res.test_suite_state.test_batch_states)
            if total_batches == 0:
                return None
            n = sum(
                batch.operation_status == OperationStatus.OPERATION_STATUS_COMPLETED
                for batch in op_res.test_suite_state.test_batch_states
            )
            return "{:<2} / {:>2} tests completed".format(n, total_batches)
        return None

    def get_status(
        self,
        verbose: bool = False,
        wait_until_finish: bool = False,
        poll_rate_sec: float = 5.0,
    ) -> Dict:
        """Query the ModelTest service for the job's status.

        This query includes an option to wait until the job is finished.
        It will either have succeeded or failed.

        Arguments:
            verbose: bool
                whether or not to print diagnostic information such as logs.
            wait_until_finish: bool
                whether or not to block until the job is SUCCEEDED or FAILED.
            poll_rate_sec: float
                the frequency with which to poll the job's status.

        Returns:
            A dictionary representing the job's state.
        """
        # Create backend client stubs to use for the remainder of this session.
        with self._backend.get_model_testing_stub() as model_tester, self._backend.get_test_run_tracker_stub() as test_tracker:  # pylint: disable=line-too-long
            job_req = GetTestJobRequest(job_id=self._job_id)
            try:
                job: JobMetadata = model_tester.GetTestJob(job_req).job
            except grpc.RpcError as e:
                # TODO(QuantumWombat): distinguish errors
                raise ValueError(e)
            if verbose:
                print(
                    "Job '{}' started at {}".format(
                        job.name, datetime.fromtimestamp(job.start_time_secs)
                    )
                )

            # Do not repeat if the job is finished or blocking is disabled.
            while wait_until_finish and not job.status in (
                JobStatus.SUCCEEDED,
                JobStatus.FAILING,
            ):
                time.sleep(poll_rate_sec)
                try:
                    job = model_tester.GetTestJob(job_req).job
                    progress = self._get_progress(test_tracker)
                except grpc.RpcError as e:
                    # TODO(QuantumWombat): distinguish other special errors
                    if e.code() == grpc.StatusCode.UNAVAILABLE:
                        if verbose:
                            print("reconnecting to the RIME backend...")
                        continue
                    raise ValueError(e)
                if verbose:
                    minute, second = divmod(job.running_time_secs, 60)
                    hour, minute = divmod(minute, 60)
                    progress_str = " ({})".format(progress) if progress else ""
                    print(
                        "Status: {}, Running Time: {:02}:{:02}:{:05.2f}{}".format(
                            JobStatus.Name(job.status),
                            int(hour),
                            int(minute),
                            second,
                            progress_str,
                        )
                    )

            # Only get the logs if verbose is enabled and the job has failed, as the
            # primary purpose is debuggability during development.
            if verbose and job.status == JobStatus.FAILING:
                log_req = GetLatestLogsRequest(job_id=self._job_id)
                try:
                    for log_res in model_tester.GetLatestLogs(request=log_req):
                        print(log_res.chunk, end="")
                except grpc.RpcError as e:
                    # TODO(QuantumWombat): distinguish errors
                    raise ValueError(e)

        # Manually remove deprecate job_name field.
        job_dict = MessageToDict(job)
        job_dict.pop("name", None)
        return job_dict

    def get_result_csv(
        self, filepath: str, version: Optional[str] = None,  # pylint: disable=W0613
    ) -> None:
        """Retrieve a CSV of test run results and store in filepath."""
        if version and not VersionInfo.isvalid(version):
            raise ValueError(f"Invalid version string: {version}")
        # TODO (QuantumWombat): return different versions of the CSV output based
        # on an optional keyword argument.

        # Create backend client stubs to use for the remainder of this session.
        with self._backend.get_model_testing_stub() as model_tester, self._backend.get_test_run_tracker_stub() as test_tracker, self._backend.get_result_store_stub() as results_store:  # pylint: disable=line-too-long
            # This first step only prevents a rare case where the RIME engine has
            # signaled the test suite has completed but before the upload has completed.
            job_req = GetTestJobRequest(job_id=self._job_id)
            try:
                job: JobMetadata = model_tester.GetTestJob(job_req).job
            except grpc.RpcError as e:
                # TODO(QuantumWombat): distinguish errors
                raise ValueError(e)
            if job.status != JobStatus.SUCCEEDED:
                raise ValueError(
                    "Job has status {}; it must have status {} to get results".format(
                        JobStatus.Name(job.status), JobStatus.Name(JobStatus.SUCCEEDED)
                    )
                )
            op_req = GetOperationStateRequest(job_id=self._job_id)
            try:
                op_res = test_tracker.GetOperationState(op_req)
            except grpc.RpcError as e:
                # TODO(QuantumWombat): more sophisticated handling of NOT_FOUND.
                raise ValueError(e)
            result_id = op_res.test_suite_state.test_suite_id
            csv_req = GetTestRunResultCSVRequest(test_run_id=result_id)
            # Default value for the CSV header.
            try:
                with open(filepath, "w", newline="") as f:
                    csv_writer = csv.writer(f, delimiter=",")
                    csv_writer.writerow(default_csv_header)
                    for csv_res in results_store.GetTestRunResultCSV(csv_req):
                        row = [
                            csv_res.test_batch_name,
                            ",".join(csv_res.features),
                            GetTestRunResultCSVResponse.TestCaseStatus.Name(
                                csv_res.test_case_status
                            ),
                        ]
                        csv_writer.writerow(row)
            except grpc.RpcError as e:
                # TODO(QuantumWombat): distinguish errors
                raise ValueError(e)


class RIMEProject(NamedTuple):
    """Information about a RIME project."""

    project_id: str
    name: str
    description: str


class RIMEClient:
    """RIMEClient provides an interface to RIME backend services."""

    # A throttler that limits the number of model tests to roughly 20 every 5 minutes.
    # This is a static variable for RIMEClient.
    _throttler = ThrottleQueue(desired_events_per_epoch=20, epoch_duration_sec=300)

    def __init__(
        self, domain: str, api_key: str = "", channel_timeout: float = 5.0
    ) -> None:
        """Create a new RIMEClient connected to the services available at `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.+
            api_key: str
                The api key providing authentication to RIME services
            channel_timeout: float
                The amount of time in seconds to wait for channels to become ready
                when opening connections to gRPC servers.

        Raises:
            ValueError
                If a connection cannot be made to a backend service within `timeout`.
        """
        self._backend = RIMEBackend(domain, api_key, channel_timeout=channel_timeout)

    # TODO(QuantumWombat): do this check server-side
    def _project_exists(self, project_id: str) -> bool:
        """Check if `project_id` exists.

        Args:
            project_id: the id of the project to be checked.

        Returns:
            whether or not project_id is a valid project.

        Raises:
            grpc.RpcError if the server has an error while checking the project.
        """
        verify_req = VerifyProjectIDRequest(project_id=project_id)
        try:
            with self._backend.get_result_store_stub() as results_store:
                results_store.VerifyProjectID(verify_req)
                return True
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise rpc_error

    def create_project(self, name: str, description: str) -> RIMEProject:
        """Create a new RIME project in RIME's backend.

        Args:
            name: str
                Name of the new project.
            description: str
                Description of the new project.

        Returns:
            A RIMEProject providing information about the new project.

        Raises:
            ValueError
                If the request to the Upload service failed.
        """
        req = CreateProjectRequest(name=name, description=description)
        try:
            with self._backend.get_result_store_stub() as results_store:
                resp = results_store.CreateProject(request=req)
                return RIMEProject(
                    project_id=resp.id, name=resp.name, description=resp.description
                )
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def start_stress_test(
        self,
        test_run_config: dict,
        project_id: Optional[str] = None,
        custom_image: Optional[CustomImage] = None,
    ) -> RIMEStressTestJob:
        """Start a RIME model stress test on the backend's ModelTesting service.

        Args:
            test_run_config: dict
                Configuration for the test to be run, which specifies paths to
                the model and datasets to used for the test.
            project_id: Optional[str]
                Identifier for the project where the resulting test run will be stored.
                If not specified, the results will be stored in the default project.
            custom_image: Optional[CustomImage]
                Specification of a customized container image to use running the model
                test. The image must have all dependencies required by your model.
                The image must specify a name for the image and optional a pull secret
                (of type CustomImage.PullSecret) with the name of the kubernetes pull
                secret used to access the given image.

        Returns:
            A RIMEStressTestJob providing information about the model stress test job.

        Raises:
            ValueError
                If the request to the ModelTest service failed.

        TODO(blaine): Add config validation service.
        """
        if not isinstance(test_run_config, dict):
            raise ValueError("The configuration must be a dictionary")

        if project_id and not self._project_exists(project_id):
            raise ValueError("Project id {} does not exist".format(project_id))

        req = StartStressTestRequest(
            test_run_config=simplejson.dumps(test_run_config).encode(),
        )
        if project_id:
            req.project_id = project_id
        if custom_image:
            req.testing_image.CopyFrom(custom_image)
        try:
            RIMEClient._throttler.throttle(
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            with self._backend.get_model_testing_stub() as model_tester:
                job: JobMetadata = model_tester.StartStressTest(request=req).job
                return RIMEStressTestJob(self._backend, job.id)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def list_stress_test_jobs(
        self,
        status_filters: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> List[RIMEStressTestJob]:
        """Query the ModelTest service for a list of jobs.

        Args:
            status_filters: Optional[List[str]]
                Filter for selecting jobs by a union of statuses.
                The following list enumerates all acceptable values.
                ['UNKNOWN_JOB_STATUS', 'PENDING', 'RUNNING', 'FAILING', 'SUCCEEDED']
                If omitted, jobs will not be filtered by status.
            project_id: Optional[str]
                Filter for selecting jobs by project ID.
                If omitted, jobs from all projects will be returned.

        Returns:
            A list of JobMetadata objects serialized to JSON.

        Raises:
            ValueError
                If the provided status_filters array has invalid values.
                If the request to the ModelTest service failed.
        """
        req = ListTestJobsRequest()
        if status_filters:
            # This throws a ValueError if status is not a valid JobStatus enum value.
            # TODO(QuantumWombat): should we catch the error and show something more
            #                      interpretable?
            # It looks like -> ValueError: Enum JobStatus has no value defined for name
            # 'does_not_exist'.
            req.selected_statuses.extend(
                [JobStatus.Value(status) for status in status_filters]
            )
        if project_id and not self._project_exists(project_id):
            raise ValueError("Project id {} does not exist".format(project_id))
        if project_id:
            req.project_id = project_id
        try:
            with self._backend.get_model_testing_stub() as model_tester:
                res = model_tester.ListTestJobs(req)
                return [RIMEStressTestJob(self._backend, job.id) for job in res.jobs]
        except grpc.RpcError as e:
            raise ValueError(e)
