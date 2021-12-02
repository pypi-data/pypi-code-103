from typing import List

from pydantic import BaseModel

from .StatusMessage import StatusMessage
from .utils import to_camel


class ResponseObject(BaseModel):
    """
    Representation of a successful completion response.
    Abstract, subclasses must instantiate this with their own type

    **Subclasses**

    * :class:`elg.model.response.AnnotationsResponse`
    * :class:`elg.model.response.AudioResponse`
    * :class:`elg.model.response.ClassificationResponse`
    * :class:`elg.model.response.TextsResponse`
    """

    type: str
    """*(required in subclass)* the type of response"""

    warnings: List[StatusMessage] = None
    """*(optional)* messages describing any warnings on response"""

    class Config:
        alias_generator = to_camel
