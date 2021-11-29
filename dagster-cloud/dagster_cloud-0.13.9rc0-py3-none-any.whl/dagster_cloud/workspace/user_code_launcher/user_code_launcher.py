import os
import sys
import tempfile
import threading
import time
import zlib
from abc import abstractmethod, abstractproperty
from typing import Dict, Generic, Iterable, Iterator, List, Optional, Set, TypeVar, Union

from dagster import check
from dagster.api.get_server_id import sync_get_server_id
from dagster.api.list_repositories import sync_list_repositories_grpc
from dagster.core.executor.step_delegating import StepHandler
from dagster.core.host_representation import ExternalRepositoryOrigin
from dagster.core.host_representation.grpc_server_registry import (
    GrpcServerEndpoint,
    GrpcServerRegistry,
)
from dagster.core.host_representation.origin import (
    RegisteredRepositoryLocationOrigin,
    RepositoryLocationOrigin,
)
from dagster.core.instance import MayHaveInstanceWeakref
from dagster.daemon.daemon import get_default_daemon_logger
from dagster.grpc.client import DagsterGrpcClient
from dagster.grpc.types import GetCurrentImageResult
from dagster.serdes import deserialize_as, serialize_dagster_namedtuple
from dagster.utils.error import SerializableErrorInfo, serializable_error_info_from_exc_info
from dagster_cloud.api.dagster_cloud_api import (
    DagsterCloudUploadLocationData,
    DagsterCloudUploadRepositoryData,
    DagsterCloudUploadWorkspaceEntry,
)
from dagster_cloud.errors import raise_http_error
from dagster_cloud.execution.watchful_run_launcher.base import WatchfulRunLauncher
from dagster_cloud.util import diff_serializable_namedtuple_map
from dagster_cloud.workspace.origin import CodeDeploymentMetadata

USER_CODE_LAUNCHER_RECONCILE_INTERVAL = 1

ServerHandle = TypeVar("ServerHandle")


class DagsterCloudUserCodeLauncher(GrpcServerRegistry, MayHaveInstanceWeakref):
    def __init__(self):
        self._logger = get_default_daemon_logger("DagsterUserCodeLauncher")
        self._started: bool = False

    def start(self):
        check.invariant(
            not self._started,
            "Called start() on a DagsterCloudUserCodeLauncher that was already started",
        )
        # Begin spinning user code up and down
        self._started = True

    @abstractmethod
    def update_grpc_metadata(
        self, desired_metadata: Dict[str, CodeDeploymentMetadata], force_update_locations: Set[str]
    ):
        pass

    def supports_origin(self, repository_location_origin: RepositoryLocationOrigin) -> bool:
        return isinstance(repository_location_origin, RegisteredRepositoryLocationOrigin)

    @property
    def supports_reload(self) -> bool:
        return False

    def reload_grpc_endpoint(self, repository_location_origin: RepositoryLocationOrigin):
        raise NotImplementedError("Call update_grpc_metadata to update gRPC endpoints")

    @abstractmethod
    def _get_repository_location_origin(self, location_name: str) -> RepositoryLocationOrigin:
        pass

    def _update_workspace_entry(self, workspace_entry: DagsterCloudUploadWorkspaceEntry):
        with tempfile.TemporaryDirectory() as temp_dir:
            dst = os.path.join(temp_dir, "workspace_entry.tmp")
            with open(dst, "wb") as f:
                f.write(
                    zlib.compress(serialize_dagster_namedtuple(workspace_entry).encode("utf-8"))
                )

            with open(dst, "rb") as f:
                self._logger.info(
                    "Uploading workspace entry for {location_name} ({size} bytes)".format(
                        location_name=workspace_entry.location_name, size=os.path.getsize(dst)
                    )
                )

                resp = self._instance.requests_session.post(
                    self._instance.dagster_cloud_upload_workspace_entry_url,
                    headers=self._instance.dagster_cloud_api_headers,
                    files={"workspace_entry.tmp": f},
                    timeout=self._instance.dagster_cloud_api_timeout,
                )
                raise_http_error(resp)

                self._logger.info(
                    "Successfully uploaded workspace entry for {location_name}".format(
                        location_name=workspace_entry.location_name
                    )
                )

    def _get_upload_location_data(self, location_name: str) -> DagsterCloudUploadLocationData:
        location_origin = self._get_repository_location_origin(location_name)
        client = self.get_grpc_endpoint(location_origin).create_client()

        list_repositories_response = sync_list_repositories_grpc(client)

        upload_repo_datas: List[DagsterCloudUploadRepositoryData] = []

        for (
            repository_name,
            code_pointer,
        ) in list_repositories_response.repository_code_pointer_dict.items():
            external_repository_chunks = list(
                client.streaming_external_repository(
                    external_repository_origin=ExternalRepositoryOrigin(
                        location_origin,
                        repository_name,
                    )
                )
            )

            serialized_repository_data = "".join(
                [
                    chunk["serialized_external_repository_chunk"]
                    for chunk in external_repository_chunks
                ]
            )
            # Don't deserialize in case there are breaking changes - let the server do it
            upload_repo_datas.append(
                DagsterCloudUploadRepositoryData(
                    repository_name=repository_name,
                    code_pointer=code_pointer,
                    serialized_repository_data=serialized_repository_data,
                )
            )

        return DagsterCloudUploadLocationData(
            upload_repository_datas=upload_repo_datas,
            container_image=deserialize_as(
                client.get_current_image(), GetCurrentImageResult
            ).current_image,
            executable_path=list_repositories_response.executable_path,
        )

    def _update_location_error(
        self,
        location_name: str,
        error_info: SerializableErrorInfo,
        metadata: CodeDeploymentMetadata,
    ):
        self._logger.error(
            "Unable to load location {location_name}. Updating location with error data: {error_info}.".format(
                location_name=location_name,
                error_info=str(error_info),
            )
        )

        # Update serialized error
        errored_workspace_entry = DagsterCloudUploadWorkspaceEntry(
            location_name=location_name,
            deployment_metadata=metadata,
            upload_location_data=None,
            serialized_error_info=error_info,
        )

        self._update_workspace_entry(errored_workspace_entry)

    def _update_location_data(self, location_name: str, endpoint, metadata: CodeDeploymentMetadata):
        self._logger.info(
            "Updating data for location {location_name}".format(location_name=location_name)
        )

        if isinstance(endpoint, SerializableErrorInfo):
            self._update_location_error(location_name, error_info=endpoint, metadata=metadata)
            return

        try:
            loaded_workspace_entry = DagsterCloudUploadWorkspaceEntry(
                location_name=location_name,
                deployment_metadata=metadata,
                upload_location_data=self._get_upload_location_data(location_name),
                serialized_error_info=None,
            )
        except Exception:
            self._update_location_error(
                location_name,
                error_info=serializable_error_info_from_exc_info(sys.exc_info()),
                metadata=metadata,
            )
            return

        self._logger.info(
            "Updating location {location_name} with repository load data".format(
                location_name=location_name,
            )
        )
        self._update_workspace_entry(loaded_workspace_entry)


class ReconcileUserCodeLauncher(DagsterCloudUserCodeLauncher, Generic[ServerHandle]):
    def __init__(self):
        self._grpc_endpoints: Dict[str, Union[GrpcServerEndpoint, SerializableErrorInfo]] = {}
        self._grpc_endpoints_lock = threading.Lock()
        self._logger = get_default_daemon_logger("ReconcileUserCodeLauncher")

        # periodically reconciles to make desired = actual
        self._desired_metadata: Dict[str, CodeDeploymentMetadata] = {}
        self._actual_metadata = {}
        self._force_update_keys: Set[str] = set()
        self._metadata_lock = threading.Lock()

        super().__init__()

        self._reconcile_count = 0
        self._reconcile_grpc_metadata_shutdown_event = threading.Event()
        self._reconcile_grpc_metadata_thread = None

    @abstractproperty
    def requires_images(self) -> bool:
        pass

    @abstractmethod
    def _get_server_handles_for_location(self, location_name: str) -> Iterable[ServerHandle]:
        """Return a list of 'handles' that represent all running servers for a given location.
        Typically this will be a single server (unless an error was previous raised during a
        reconciliation loop. ServerHandle can be any type that is sufficient for
        _remove_server_handle to remove the service."""

    @abstractmethod
    def _create_new_server_endpoint(
        self, location_name: str, metadata: CodeDeploymentMetadata
    ) -> GrpcServerEndpoint:
        """Create a new server for the given location using the given metadata as configuration
        and return a GrpcServerEndpoint indicating a hostname/port that can be used to access
        the server. Should result in an additional handle being returned from _get_server_handles_for_location."""

    @abstractmethod
    def _remove_server_handle(self, server_handle: ServerHandle) -> None:
        """Shut down any resources associated with the given handle. Called both during updates
        to spin down the old server once a new server has been spun up, and during removal."""

    @abstractmethod
    def _cleanup_servers(self):
        """Remove all servers, across all locations."""

    @abstractmethod
    def get_step_handler(self, execution_config: Optional[Dict]) -> StepHandler:
        pass

    @abstractmethod
    def run_launcher(self) -> WatchfulRunLauncher:
        pass

    def start(self):
        super().start()

        self._cleanup_servers()

        self._reconcile_grpc_metadata_thread = threading.Thread(
            target=self._reconcile_thread,
            args=(self._reconcile_grpc_metadata_shutdown_event,),
            name="grpc-reconcile-watch",
        )
        self._reconcile_grpc_metadata_thread.daemon = True
        self._reconcile_grpc_metadata_thread.start()

    def __exit__(self, exception_type, exception_value, traceback):
        if self._reconcile_grpc_metadata_thread:
            self._reconcile_grpc_metadata_shutdown_event.set()
            self._reconcile_grpc_metadata_thread.join()

        if self._started:
            self._cleanup_servers()

        super().__exit__(exception_value, exception_value, traceback)

    def update_grpc_metadata(
        self, desired_metadata: Dict[str, CodeDeploymentMetadata], force_update_locations: Set[str]
    ):
        check.dict_param(
            desired_metadata, "desired_metadata", key_type=str, value_type=CodeDeploymentMetadata
        )
        check.set_param(force_update_locations, "force_update_locations", str)
        with self._metadata_lock:
            self._desired_metadata = desired_metadata
            self._force_update_keys = force_update_locations

    def _get_repository_location_origin(
        self, location_name: str
    ) -> RegisteredRepositoryLocationOrigin:
        return RegisteredRepositoryLocationOrigin(location_name)

    def _reconcile_thread(self, shutdown_event):
        while True:
            shutdown_event.wait(USER_CODE_LAUNCHER_RECONCILE_INTERVAL)
            if shutdown_event.is_set():
                break

            try:
                self.reconcile()
            except Exception:
                self._logger.error(
                    "Failure updating user code servers: {exc_info}".format(
                        exc_info=sys.exc_info(),
                    )
                )

    def reconcile(self):
        with self._metadata_lock:
            self._reconcile()
            self._reconcile_count += 1

    def _check_for_image(self, metadata: CodeDeploymentMetadata):
        if self.requires_images and not metadata.image:
            raise Exception(
                "Your agent's configuration requires you to specify an image. "
                "Use the `--image` flag when specifying your location to tell the agent "
                "which image to use to load your code."
            )

        if (not self.requires_images) and metadata.image:
            raise Exception(
                "Your agent's configuration cannot load locations that specify a Docker "
                "image. Either update your location to not include an image, or change the `user_code_launcher` "
                "field in your agent's `dagster.yaml` file to a launcher that can load Docker images. "
            )

    def _reconcile(self):
        diff = diff_serializable_namedtuple_map(
            self._desired_metadata, self._actual_metadata, self._force_update_keys
        )

        to_update_keys = diff.to_add.union(diff.to_update)

        update_gens: Dict[str, Iterator[GrpcServerEndpoint]] = {}
        for to_update_key in to_update_keys:
            try:
                self._check_for_image(self._desired_metadata[to_update_key])
                update_gens[to_update_key] = self._gen_update_server(
                    to_update_key,
                    self._desired_metadata[to_update_key],
                )
                new_updated_endpoint: GrpcServerEndpoint = next(update_gens[to_update_key])
            except Exception:
                error_info = serializable_error_info_from_exc_info(sys.exc_info())
                self._logger.error(
                    "Error while updating server for {to_update_key}: {error_info}".format(
                        to_update_key=to_update_key,
                        error_info=error_info,
                    )
                )
                new_updated_endpoint: SerializableErrorInfo = error_info

            with self._grpc_endpoints_lock:
                self._grpc_endpoints[to_update_key] = new_updated_endpoint

            try:
                self._update_location_data(
                    to_update_key, new_updated_endpoint, self._desired_metadata[to_update_key]
                )
            except Exception:
                # Don't let a failure uploading the serialized data keep other locations
                # from being updated or continue reconciling in a loop
                error_info = serializable_error_info_from_exc_info(sys.exc_info())
                self._logger.error(
                    "Error while writing location data for updated server {to_update_key}: {error_info}".format(
                        to_update_key=to_update_key,
                        error_info=error_info,
                    )
                )

        for to_update_key in to_update_keys:
            update_gen = update_gens.get(to_update_key)
            if update_gen:
                # Finish any remaining cleanup
                try:
                    list(update_gen)
                except Exception:
                    self._logger.error(
                        "Error while cleaning up after updating server for {to_update_key}: {error_info}".format(
                            to_update_key=to_update_key,
                            error_info=serializable_error_info_from_exc_info(sys.exc_info()),
                        )
                    )

            self._actual_metadata[to_update_key] = self._desired_metadata[to_update_key]
            if to_update_key in self._force_update_keys:
                self._force_update_keys.remove(to_update_key)

        for to_remove_key in diff.to_remove:
            try:
                self._remove_server(to_remove_key)
            except Exception:
                self._logger.error(
                    "Error while removing server for {to_remove_key}: {error_info}".format(
                        to_remove_key=to_remove_key,
                        error_info=serializable_error_info_from_exc_info(sys.exc_info()),
                    )
                )

            with self._grpc_endpoints_lock:
                del self._grpc_endpoints[to_remove_key]
            del self._actual_metadata[to_remove_key]

    def get_grpc_endpoint(
        self, repository_location_origin: RepositoryLocationOrigin
    ) -> GrpcServerEndpoint:
        with self._grpc_endpoints_lock:
            location_name = repository_location_origin.location_name
            endpoint = self._grpc_endpoints.get(location_name)

        if not endpoint:
            raise Exception(f"No server endpoint exists for location {location_name}")

        if isinstance(endpoint, SerializableErrorInfo):
            # Consider raising the original exception here instead of a wrapped one
            raise Exception(
                f"Failure loading server endpoint for location {location_name}: {endpoint}"
            )

        return endpoint

    def get_grpc_endpoints(
        self,
    ) -> Dict[str, Union[GrpcServerEndpoint, SerializableErrorInfo]]:
        with self._grpc_endpoints_lock:
            return self._grpc_endpoints.copy()

    def _gen_update_server(
        self, location_name: str, new_metadata: CodeDeploymentMetadata
    ) -> Iterator[GrpcServerEndpoint]:
        # Update the server for the given location. Is a generator - should yield the new
        # GrpcServerEndpoint, then clean up any no longer needed resources
        existing_server_handles = self._get_server_handles_for_location(location_name)
        updated_server = self._create_new_server_endpoint(location_name, new_metadata)

        yield updated_server

        for server_handle in existing_server_handles:
            self._remove_server_handle(server_handle)

    def _remove_server(self, location_name: str):
        existing_server_handles = self._get_server_handles_for_location(location_name)
        for server_handle in existing_server_handles:
            self._remove_server_handle(server_handle)

    def _wait_for_server(
        self, host: str, port: int, timeout=15, socket: Optional[str] = None
    ) -> str:
        # Wait for the server to be ready (while also loading the server ID)
        server_id = None
        start_time = time.time()
        while True:
            client = DagsterGrpcClient(port=port, host=host, socket=socket)
            try:
                server_id = sync_get_server_id(client)
                break
            except Exception:
                pass

            if time.time() - start_time > timeout:
                raise Exception(f"Timed out waiting for server {host}:{port}")

            time.sleep(1)
        return server_id
