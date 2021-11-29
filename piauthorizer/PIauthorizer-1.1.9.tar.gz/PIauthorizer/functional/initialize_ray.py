import os
import sys

import ray
from fastapi import FastAPI
from ray import serve

from .ray_router import ray_router
import GPUtil


def initialize_ray(
    app: FastAPI,
    namespace: str,
    packages: bool = False,
    dashboard: bool = False,
    init: bool = False,
) -> None:
    """
    Initialize ray and ray serve on a local cluster or by connecting to a long running Ray cluster.
    Also, adds the Ray Router to the app.


    Args:
        app (FastAPI): a FastAPI app to which to include the default Ray deployment router
        namespace (str): an internal namespace to connect to within the cluster
        packages (bool, optional): a relative path to the local requirements file. Defaults to [].
        init (bool, optional): choose to use init or util.connect. Defaults to False.
    """
    head_service_ip = os.environ.get(f"NLP_CLUSTER_RAY_HEAD_SERVICE_HOST")
    client_port = os.environ.get("NLP_CLUSTER_RAY_HEAD_SERVICE_PORT_CLIENT")
    runtime_env = {
        "env_vars": dict(os.environ),
    }
    if packages:
        runtime_env["working_dir"] = "."
        runtime_env["pip"] = "requirements.txt"
        runtime_env["excludes"] = ["*/models"]

    if not head_service_ip:
        try:
            num_gpus = len(GPUtil.getGPUs())
        except:
            num_gpus = 0
        ray.init(
            num_cpus=os.cpu_count(),
            num_gpus=num_gpus,
            namespace=namespace,
            include_dashboard=dashboard,
        )
        detached = False
    else:
        if init:
            ray.init(
                f"ray://{head_service_ip}:{client_port}",
                runtime_env=runtime_env,
                namespace=namespace,
            )
        else:
            ray.util.connect(
                f"{head_service_ip}:{client_port}",
                ray_init_kwargs={"runtime_env": runtime_env,
                                 "namespace": namespace},
            )
        detached = True

    assert ray.is_initialized()
    serve.start(detached=detached)
    app.include_router(ray_router)
