from typing import List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ValidationError

from classification_model.config.core import config


def validate_inputs(*, input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    """Check model inputs for unprocessable values."""

    validated_data = input_data[config.model_config.features].copy()
    errors = None

    try:
        # replace numpy nans so that pydantic can validate
        MultipleDataInputs(inputs=validated_data.to_dict(orient="records"))
    except ValidationError as error:
        errors = error.json()

    return validated_data, errors


class DataInputSchema(BaseModel):
    age: Optional[float]
    anaemia: Optional[int]
    creatinine_phosphokinase: Optional[int]
    diabetes: Optional[int]
    ejection_fraction: Optional[int]
    high_blood_pressure: Optional[int]
    platelets: Optional[float]
    serum_creatinine: Optional[float]
    serum_sodium: Optional[float]
    sex: Optional[int]
    smoking: Optional[int]
    time: Optional[int]


class MultipleDataInputs(BaseModel):
    inputs: List[DataInputSchema]
