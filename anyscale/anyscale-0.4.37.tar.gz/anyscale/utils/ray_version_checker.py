import sys
from typing import Any, Tuple


def detect_ray_version(imported_ray: Any = None) -> Tuple[str, str]:
    """
    Returns Tuple of ray_version, ray_commit
    Raises RuntimeError if imported_ray is not provided and ray is not installed
    """
    if imported_ray is None:
        try:
            import ray
        except ModuleNotFoundError:
            raise RuntimeError(
                "Ray is not installed. Please install with: \n"
                "pip install -U --force-reinstall `python -m anyscale.connect required_ray_version`"
            )
        imported_ray = ray

    return imported_ray.__version__, imported_ray.__commit__


def detect_python_minor_version() -> str:
    return f"{sys.version_info[0]}.{sys.version_info[1]}"
