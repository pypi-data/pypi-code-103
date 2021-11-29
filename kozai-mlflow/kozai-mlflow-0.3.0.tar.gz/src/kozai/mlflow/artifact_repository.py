import os
import posixpath

from azure.storage.blob import BlobPrefix, ContainerClient

from mlflow.entities import FileInfo
from mlflow.exceptions import MlflowException
from mlflow.store.artifact.artifact_repo import ArtifactRepository

# import re
# import urllib.parse


class KozaiArtifactRepository(ArtifactRepository):
    def __init__(self, artifact_uri):
        super().__init__(artifact_uri)

        if not artifact_uri.startswith("kozai://"):
            raise MlflowException(
                f"Unknown kozai artifact repository uri: {artifact_uri}"
            )

        self.client = ContainerClient.from_container_url(
            container_url=os.environ["MLFLOW_ARTIFACTS_AZURE_STORAGE_SAS_URI"],
        )

    @staticmethod
    def parse_kozai_uri(artifact_uri: str):
        split = artifact_uri.split("/")
        container_name = split[2]
        artifact_path = "/".join(split[3:])
        return container_name, artifact_path

    # @staticmethod
    # def parse_wasbs_uri(uri):
    #     """Parse a wasbs:// URI, returning (container, storage_account, path)."""
    #     parsed = urllib.parse.urlparse(uri)
    #     if parsed.scheme != "wasbs":
    #         raise Exception("Not a WASBS URI: %s" % uri)
    #     match = re.match("([^@]+)@([^.]+)\\.blob\\.core\\.windows\\.net", parsed.netloc)
    #     if match is None:
    #         raise Exception(
    #             "WASBS URI must be of the form "
    #             "<container>@<account>.blob.core.windows.net"
    #         )
    #     container = match.group(1)
    #     storage_account = match.group(2)
    #     path = parsed.path
    #     if path.startswith("/"):
    #         path = path[1:]
    #     return container, storage_account, path

    def log_artifact(self, local_file, artifact_path=None):
        """
        Log a local file as an artifact, optionally taking an ``artifact_path`` to place it in
        within the run's artifacts. Run artifacts can be organized into directories, so you can
        place the artifact in a directory this way.
        :param local_file: Path to artifact to log
        :param artifact_path: Directory within the run's artifact directory in which to log the
                              artifact.
        """
        _, dest_path = self.parse_kozai_uri(self.artifact_uri)
        # (container, _, dest_path) = self.parse_wasbs_uri(self.artifact_uri)
        # container_client = self.client.get_container_client(container)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        dest_path = posixpath.join(dest_path, os.path.basename(local_file))
        with open(local_file, "rb") as file:
            self.client.upload_blob(dest_path, file)

    def log_artifacts(self, local_dir, artifact_path=None):
        """
        Log the files in the specified local directory as artifacts, optionally taking
        an ``artifact_path`` to place them in within the run's artifacts.
        :param local_dir: Directory of local artifacts to log
        :param artifact_path: Directory within the run's artifact directory in which to log the
                              artifacts
        """
        _, dest_path = self.parse_kozai_uri(self.artifact_uri)
        # (container, _, dest_path) = self.parse_wasbs_uri(self.artifact_uri)
        # container_client = self.client.get_container_client(container)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        local_dir = os.path.abspath(local_dir)
        for (root, _, filenames) in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                upload_path = posixpath.join(dest_path, rel_path)
            for f in filenames:
                remote_file_path = posixpath.join(upload_path, f)
                local_file_path = os.path.join(root, f)
                with open(local_file_path, "rb") as file:
                    self.client.upload_blob(remote_file_path, file)

    def list_artifacts(self, path=None):
        """
        Return all the artifacts for this run_id directly under path. If path is a file, returns
        an empty list. Will error if path is neither a file nor directory.
        :param path: Relative source path that contains desired artifacts
        :return: List of artifacts as FileInfo listed directly under path.
        """
        _, artifact_path = self.parse_kozai_uri(self.artifact_uri)
        # (container, _, artifact_path) = self.parse_wasbs_uri(self.artifact_uri)
        # container_client = self.client.get_container_client(container)
        dest_path = artifact_path
        if path:
            dest_path = posixpath.join(dest_path, path)
        infos = []
        prefix = dest_path if dest_path.endswith("/") else dest_path + "/"
        results = self.client.walk_blobs(name_starts_with=prefix)
        for r in results:
            if not r.name.startswith(artifact_path):
                raise MlflowException(
                    "The name of the listed Azure blob does not begin with the specified"
                    " artifact path. Artifact path: {artifact_path}. Blob name:"
                    " {blob_name}".format(artifact_path=artifact_path, blob_name=r.name)
                )
            if isinstance(r, BlobPrefix):  # This is a prefix for items in a subdirectory
                subdir = posixpath.relpath(path=r.name, start=artifact_path)
                if subdir.endswith("/"):
                    subdir = subdir[:-1]
                infos.append(FileInfo(subdir, True, None))
            else:  # Just a plain old blob
                file_name = posixpath.relpath(path=r.name, start=artifact_path)
                infos.append(FileInfo(file_name, False, r.size))
        # The list_artifacts API expects us to return an empty list if the
        # the path references a single file.
        rel_path = dest_path[len(artifact_path) + 1 :]
        if (len(infos) == 1) and not infos[0].is_dir and (infos[0].path == rel_path):
            return []
        return sorted(infos, key=lambda f: f.path)

    def _download_file(self, remote_file_path, local_path):
        """
        Download the file at the specified relative remote path and saves
        it at the specified local path.
        :param remote_file_path: Source path to the remote file, relative to the root
                                 directory of the artifact repository.
        :param local_path: The path to which to save the downloaded file.
        """
        _, remote_root_path = self.parse_kozai_uri(self.artifact_uri)
        # (container, _, remote_root_path) = self.parse_wasbs_uri(self.artifact_uri)
        # container_client = self.client.get_container_client(container)
        remote_full_path = posixpath.join(remote_root_path, remote_file_path)
        with open(local_path, "wb") as file:
            self.client.download_blob(remote_full_path).readinto(file)

    def delete_artifacts(self, artifact_path=None):
        """
        Delete the artifacts at the specified location.
        Supports the deletion of a single file or of a directory. Deletion of a directory
        is recursive.
        :param artifact_path: Path of the artifact to delete
        """
        raise MlflowException("Not implemented yet")
