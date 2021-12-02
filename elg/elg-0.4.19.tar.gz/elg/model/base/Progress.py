from pydantic import BaseModel

from .StatusMessage import StatusMessage
from .utils import to_camel


class Progress(BaseModel):
    """
    Details of an in progress task
    Some LT services can take a long time to process each request - likely useful to keep caller updated
    """

    percent: float
    """*(required)* completion percentage"""
    message: StatusMessage = None
    """*(optional)* message describing progress report"""

    class Config:
        alias_generator = to_camel
