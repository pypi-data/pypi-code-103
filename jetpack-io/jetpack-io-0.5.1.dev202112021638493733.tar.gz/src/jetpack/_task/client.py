from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Awaitable, Dict, Optional, Tuple, Union, cast
import uuid

from google.protobuf.timestamp_pb2 import Timestamp
import grpc
import jsonpickle

from jetpack import __version__
from jetpack._remote import codec
from jetpack.config import namespace
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack._task.task import Task


class JetpackException(Exception):
    """Base class for exceptions in this module"""

    pass


class RuntimeException(JetpackException):
    """Exception raised for errors in the Jetpack runtime and kubernetes."""

    def __init__(self, message: str) -> None:
        self.message = message


class ApplicationException(JetpackException):
    """Exception raised for errors from application-code that is using the SDK.

    TODO DEV-157
    For exceptions raised by remote functions and jobs, we serialize the
    userland exception in the backend and save it here. The userland exception
    is re-raised by the SDK for the caller of the remote function or job.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class NoControllerAddressError(JetpackException):
    pass


class Client:
    def __init__(self) -> None:
        host = os.environ.get(
            "JETPACK_RUNTIME_SERVICE_HOST",
            "remotesvc.jetpack-runtime.svc.cluster.local",
        )
        port = os.environ.get("JETPACK_RUNTIME_SERVICE_PORT", "80")
        self.address: str = f"{host.strip()}:{port.strip()}"
        self.stub: Optional[remote_pb2_grpc.RemoteExecutorStub] = None
        self.async_stub: Optional[remote_pb2_grpc.RemoteExecutorStub] = None

    def dial(self, is_async: bool) -> remote_pb2_grpc.RemoteExecutorStub:
        if not self.address:
            raise NoControllerAddressError("Controller address is not set")
        # Since this is inter-cluster communication, insecure is fine.
        # In the future this won't even leave the pod, and use a sidecar so
        # it will be localhost.

        # TODO(Landau): When/how should we close the channels?
        if is_async:
            # Warning, this calls asyncio.get_event_loop() which will throw
            # exception if event loop has already been set and closed.
            if self.async_stub is None:
                async_channel = grpc.aio.insecure_channel(self.address)
                self.async_stub = remote_pb2_grpc.RemoteExecutorStub(async_channel)
            return self.async_stub
        else:
            if self.stub is None:
                channel = grpc.insecure_channel(self.address)
                self.stub = remote_pb2_grpc.RemoteExecutorStub(channel)
            return self.stub

    def get_stub(self) -> remote_pb2_grpc.RemoteExecutorStub:
        return self.dial(False)

    def get_async_stub(self) -> remote_pb2_grpc.RemoteExecutorStub:
        return self.dial(True)

    async def create_task(
        self,
        task: Task,
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> uuid.UUID:
        """Creates a Jetpack task. How the task gets executed is up to
        jetpack runtime.

        Keyword arguments:
        task -- task to create
        """

        request = self._build_create_task_request(task, args, kwargs)
        response: remote_pb2.CreateTaskResponse = (
            await self.get_async_stub().CreateTask(request)
        )
        return uuid.UUID(response.task_id)

    def post_result(
        self, exec_id: str, value: Any = None, error: Optional[Exception] = None
    ) -> remote_pb2.PostResultResponse:

        if not exec_id:
            # Note: value=None and error=None is acceptable because a job
            # can run successfully and return nothing.
            raise Exception("An exec_id is required to post a result")

        result = remote_pb2.Result()
        if error:
            result.error.code = remote_pb2.APPLICATION
            result.error.message = str(error)
            result.error.encoded_error = bytes(jsonpickle.encode(error), "utf-8")
        else:  # order matters, as 'value' can be None
            result.value.encoded_value = bytes(jsonpickle.encode(value), "utf-8")

        request = remote_pb2.PostResultRequest(
            exec_id=exec_id,
            result=result,
        )

        response = self.get_stub().PostResult(request)
        return cast(remote_pb2.PostResultResponse, response)

    def get_result(self, task_id: uuid.UUID) -> Any:
        request = remote_pb2.WaitForResultRequest(task_id=str(task_id))
        result = self.get_stub().WaitForResult(request)
        return self._transform_response_exception(result)

    # async version of get_result
    async def wait_for_result(self, task_id: uuid.UUID) -> Any:
        request = remote_pb2.WaitForResultRequest(task_id=str(task_id))
        result = await self.get_async_stub().WaitForResult(request)
        return self._transform_response_exception(result)

    def _build_create_task_request(
        self,
        task: Task,
        args: Optional[Tuple[Any, ...]],
        kwargs: Optional[Dict[str, Any]],
    ) -> remote_pb2.CreateTaskRequest:
        encoded_args = b""
        if args or kwargs:
            encoded_args = codec.encode_args(
                args if args else None,
                kwargs if kwargs else None,
            ).encode("utf-8")

        current_namespace = namespace.get()
        task_proto_obj = remote_pb2.Task(
            qualified_symbol=task.jetpack_function.name(),
            encoded_args=encoded_args,
            hostname=os.environ.get("HOSTNAME", ""),  # k8s sets this
            target_time=Timestamp(seconds=task.target_time),
        )
        if current_namespace:
            task_proto_obj.namespace = current_namespace

        return remote_pb2.CreateTaskRequest(
            task=task_proto_obj, sdk_version=__version__
        )

    @staticmethod
    def _transform_response_exception(
        response: remote_pb2.WaitForResultResponse,
    ) -> Any:
        if response.result.HasField("error") and response.result.error.encoded_error:
            e = jsonpickle.decode(response.result.error.encoded_error)
            raise e
        elif response.result.HasField("value"):
            val = jsonpickle.decode(response.result.value.encoded_value)
            return val
        else:
            raise RuntimeException(
                f"Either 'value' or 'error' should be specified in response. Got: {response}"
            )
