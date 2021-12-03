from pydantic import (
    BaseModel,
    HttpUrl, root_validator
)

from typing import Optional, List

from ..generics import Image


class BatchPredictionPreRunRequest_MetaField(BaseModel):
    webhooks: Optional[HttpUrl]


class BatchPredictionPreRunRequest(BaseModel):
    request_id: str
    meta: Optional[BatchPredictionPreRunRequest_MetaField]
    images: Optional[List[Image]]
    imagesfile: Optional[str]
    model_name: str
    model_id: str
    labels_source: Optional[str]

    @root_validator
    def check_images_or_imagefile_has_data(cls, values):
        if not values.get('images') and not values.get('imagesfile'):
            raise ValueError(
                "At least one of 'images' and 'imagesfile' must be set."
            )

        return values

    # @classmethod
    # def from_gateway_request(gateway_request: MLGatewayRequest):
    #     # ...
    #     return cls(

    #     )
