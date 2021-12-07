import enum
import os
from typing import Any, Awaitable, Dict, List, Optional, Tuple, Union, cast

import grpc

from jetpack import __version__
from jetpack.config import namespace
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc

# Instead of having individual clients per functionality (e.g. job), have a
# single client for our runtime.

# TODO(Landau): Move client functionality out of _job.client and centralize it
# here.


class Client:
    def __init__(self) -> None:
        host = os.environ.get(
            "JETPACK_RUNTIME_SERVICE_HOST",
            "remotesvc.jetpack-runtime.svc.cluster.local",
        )
        port = os.environ.get("JETPACK_RUNTIME_SERVICE_PORT", "80")
        self.address: str = f"{host.strip()}:{port.strip()}"
        self.stub: Optional[remote_pb2_grpc.RemoteExecutorStub] = None

    def dial(self) -> remote_pb2_grpc.RemoteExecutorStub:
        if self.stub is None:
            channel = grpc.insecure_channel(self.address)
            self.stub = remote_pb2_grpc.RemoteExecutorStub(channel)
        assert self.stub is not None
        return self.stub


client = Client()


def set_cron_jobs(
    cron_jobs: List[remote_pb2.CronJob],
) -> remote_pb2.SetCronJobsResponse:
    request = remote_pb2.SetCronJobsRequest(
        namespace=cast(str, namespace.get()),
        hostname=os.environ["HOSTNAME"],
        cron_jobs=cron_jobs,
    )
    stub = client.dial()
    return cast(remote_pb2.SetCronJobsResponse, stub.SetCronJobs(request))
