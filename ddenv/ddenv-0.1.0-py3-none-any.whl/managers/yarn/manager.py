from tempfile import TemporaryDirectory
from typing import Final, Optional

from docker.models.containers import Container

import ddenv.managers.util as util
from ddenv.managers.core import BaseManager

DEFAULT_VERSION: Final[str] = "lts"


class Manager(BaseManager):
    @property
    def name(self) -> str:
        return "yarn"

    @property
    def version(self) -> str:
        if self._version is None:
            return DEFAULT_VERSION
        return self._version

    @property
    def image_name(self) -> str:
        prefix = super().image_name
        workdir_hash = util.hash_str(self.workdir)
        return f"{prefix}-{workdir_hash}"

    @property
    def image_tag(self) -> str:
        yarn_lock_hash = util.hash_file(self.workdir_file("yarn.lock"))
        return f"{self.image_name}:{self.version}-{yarn_lock_hash}"

    @property
    def image_exists(self) -> bool:
        return util.image_exists(self.docker_client, self.image_tag)

    def build_base_image(self):
        with TemporaryDirectory() as tempdir:
            util.copy_files(
                util.dockerfile_path(__file__),
                util.file_dir_file(__file__, "entrypoint.sh"),
                self.workdir_file("package.json"),
                self.workdir_file("yarn.lock"),
                dst=tempdir,
            )

            self.docker_client.images.build(
                path=tempdir,
                tag=self.image_tag,
                rm=True,
                buildargs={"VERSION": self.version},
            )

    def run_command(self, command: Optional[list[str]]) -> Container:
        return self.docker_client.containers.run(
            image=self.image_tag,
            command=command,
            remove=True,
            detach=True,
            volumes={self.workdir: {"bind": "/app", "mode": "rw"}},
        )
