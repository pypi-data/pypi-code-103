# Note: Don't import anything from aporia.training here, it won't work without extra dependencies
import aporia.experimental  # noqa: F401
from .core.core_api import create_model, create_model_version, delete_model, init, shutdown
from .core.model_tags import add_model_tags, delete_model_tag, get_model_tags
from .core.types.model import ModelColor, ModelIcon
from .model import Model

__all__ = [
    # Core
    "create_model",
    "create_model_version",
    "delete_model",
    "init",
    "shutdown",
    "add_model_tags",
    "delete_model_tag",
    "get_model_tags",
    "ModelColor",
    "ModelIcon",
    # Inference
    "Model",
]
