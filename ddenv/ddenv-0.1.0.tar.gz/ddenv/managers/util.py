from hashlib import md5
from pathlib import Path
from shutil import copy

from docker import DockerClient
from docker.errors import ImageNotFound


def file_dir_file(file_path: str, file: str) -> Path:
    return Path(file_path).parent / file


def dockerfile_path(file_path: str) -> Path:
    return file_dir_file(file_path, "Dockerfile")


def copy_files(*srcs: Path | str, dst: str):
    for src in srcs:
        copy(src, dst)


def hash_str(s: str) -> str:
    return md5(s.encode()).hexdigest()


def hash_file(file: str | Path) -> str:
    block_size = 65536
    h = md5()
    with open(file, "rb") as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            h.update(buf)
            buf = f.read(block_size)
    return h.hexdigest()


def image_exists(docker_client: DockerClient, image_tag: str) -> bool:
    try:
        docker_client.images.get(image_tag)
        return True
    except ImageNotFound:
        return False
