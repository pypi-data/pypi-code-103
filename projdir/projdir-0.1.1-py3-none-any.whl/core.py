from pathlib import Path
from typing import Union

StrOrPath = Union[str, Path]


class MarkerNotFound(FileNotFoundError):
    pass


def _find_recursive(start_dir: Path, marker_relpath: Path, dir_ok: bool, file_ok: bool):
    current_dir = start_dir

    def is_match(path: Path):
        return (path.is_file() and file_ok) or (path.is_dir() and dir_ok)

    while not is_match(current_dir / marker_relpath):
        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            raise MarkerNotFound(parent_dir / marker_relpath)
        current_dir = parent_dir
    return current_dir


def find(marker_relpath: StrOrPath, dir_ok=True, file_ok=True):
    start_dir = Path.cwd()
    return _find_recursive(start_dir, marker_relpath, dir_ok, file_ok)
