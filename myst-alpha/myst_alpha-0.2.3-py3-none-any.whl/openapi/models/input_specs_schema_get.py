from typing import Any

from myst.models import base_model


class InputSpecsSchemaGet(base_model.BaseModel):
    """Schema for node input spec schema responses."""

    input_specs_schema: Any
