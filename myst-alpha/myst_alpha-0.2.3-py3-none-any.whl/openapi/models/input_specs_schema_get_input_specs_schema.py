from typing import Any, Dict

from myst.models import base_model


class InputSpecsSchemaGetInputSpecsSchema(base_model.BaseModel):
    """JSON input specs schema for the specified node."""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
