import logging
import subprocess

from docker.errors import ImageNotFound, APIError  # type: ignore

from biolib import utils
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.compute_node.cloud_utils import CloudUtils
from biolib.compute_node.job_worker.cache_state import DockerImageCacheState, DockerCacheStateError
from biolib.compute_node.job_worker.cache_types import DockerImageInfo, DockerImageCacheStateDict, DockerAuthConfig


class DockerImageCache:
    def __init__(self):
        config = CloudUtils.get_webserver_config()
        self._max_cache_size = config['max_docker_image_cache_size_bytes']  # pylint: disable=unsubscriptable-object
        self._docker_client = BiolibDockerClient().get_docker_client()
        self._docker_data_dir = self._docker_client.info()['DockerRootDir']

    @property
    def _current_cache_size_on_disk(self):
        disk_usage_command = ['/bin/bash', '-c', f'du -sb {self._docker_data_dir} | cut -f1']
        if not utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            # Need to use sudo outside of enclave
            disk_usage_command.insert(0, 'sudo')

        du_output = subprocess.run(
            disk_usage_command,
            capture_output=True,
            check=True
        ).stdout
        return int(du_output.decode().strip())

    def _clear_space_for_image(self, estimated_image_size_bytes: int, cache_state: DockerImageCacheStateDict):
        while not self._has_space_to_pull_image(estimated_image_size_bytes, cache_state):
            self._remove_least_recently_used_image(cache_state)

    def get(self, image_uri: str, estimated_image_size_bytes: int, pull_auth_config: DockerAuthConfig):
        try:
            with DockerImageCacheState() as cache_state:
                self._docker_client.images.get(image_uri)
                cache_state[image_uri]['last_used_at'] = DockerImageCacheState.get_timestamp_now()

        except ImageNotFound:
            if estimated_image_size_bytes > self._max_cache_size:
                CloudUtils.log(
                    f'Image {image_uri} with size: {estimated_image_size_bytes} is bigger than the max cache size',
                    logging.ERROR,
                )
                raise DockerCacheStateError(  # pylint: disable=raise-missing-from
                    'Image is bigger than the max cache size'
                )

            with DockerImageCacheState() as cache_state:
                if not self._has_space_to_pull_image(estimated_image_size_bytes, cache_state):
                    self._clear_space_for_image(estimated_image_size_bytes, cache_state)

                cache_state[image_uri] = DockerImageInfo(
                    last_used_at=DockerImageCacheState.get_timestamp_now(),
                    uri=image_uri,
                    state='pulling',
                    estimated_image_size_bytes=estimated_image_size_bytes
                )

            CloudUtils.log(f'Image {image_uri} not found in cache. Pulling...', logging.DEBUG)
            self._docker_client.images.pull(image_uri, auth_config=pull_auth_config)
            with DockerImageCacheState() as cache_state:
                cache_state[image_uri]['state'] = 'ready'

    def _remove_least_recently_used_image(self, cache_state: DockerImageCacheStateDict) -> None:
        cached_images = [image for image in cache_state.values() if image['state'] == 'ready']
        images_sorted_by_least_recently_used = sorted(cached_images, key=lambda image: image['last_used_at'])

        for image in images_sorted_by_least_recently_used:
            CloudUtils.log(f"Removing image: {image['uri']}", logging.DEBUG)
            try:
                self._docker_client.api.remove_image(image=image['uri'])
            except APIError as error:
                CloudUtils.log(
                    f'Could not remove image due to {error}... Skipping removal of this image.',
                    logging.ERROR
                )
                continue  # Image is in use or cannot be removed at this time

            cache_state.pop(image['uri'])
            break

    def _has_space_to_pull_image(self, estimated_image_size_bytes: int, cache_state: DockerImageCacheStateDict) -> bool:
        size_of_images_being_pulled = sum([image['estimated_image_size_bytes'] for image in cache_state.values()
                                           if image['state'] == 'pulling'])
        current_cache_size = self._current_cache_size_on_disk + size_of_images_being_pulled

        cache_space_remaining = self._max_cache_size - current_cache_size
        CloudUtils.log(f'Cache space remaining: {cache_space_remaining}', logging.DEBUG)

        return bool(cache_space_remaining > estimated_image_size_bytes)
