

from pathlib import Path
from typing import Union
from boltons.pathutils import expandpath
from logz import get_cls_logger

get_logger = get_cls_logger('dcode')
logger = get_logger()

def get_path(path: Union[str, Path], *paths, posix: bool = False) -> Path:
    if isinstance(path, str): 
        if '~' in path: path = expandpath(path)
        elif '.' in path: path = path.replace('.', Path.cwd().as_posix(), 1)
        path = Path(path)
    path = path.joinpath(*paths)
    if posix: path = path.as_posix()
    return path



