from typing import List

from pydantic import BaseModel

from .StatusMessage import StatusMessage
from .utils import to_camel


class Failure(BaseModel):
    """
    Details of a failed task
    """

    errors: List[StatusMessage]
    """*(required)* List of status messages describing the failure"""

    class Config:
        alias_generator = to_camel
