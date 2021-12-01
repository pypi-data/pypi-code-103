from pydantic import (
    BaseModel, validator, AnyUrl
)

from typing import Optional, Dict


class Image(BaseModel):
    id: str
    uri: AnyUrl
    data: Optional[Dict]

    @validator('uri')
    def check_valid_uri(cls, uri):
        legal_schemes = ['gs', 'http', 'https']
        if uri.scheme not in legal_schemes:
            raise ValueError(
                f'{uri} scheme must be one of {" ".join(legal_schemes)}'
            )

        return uri
