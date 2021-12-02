from pydantic import BaseModel

from .utils import to_camel


class Request(BaseModel):
    """
    Representation of a service invocation request.
    Intended to be abstract, subclasses should be initiated with their specific type

    **Subclasses**

    * :class:`elg.model.request.AudioRequest`
    * :class:`elg.model.request.TextRequest`
    * :class:`elg.model.request.StructuredTextRequest`
    """

    type: str = None
    """*(required in subclass)* the type of request"""
    params: dict = None
    """*(optional)* vendor specific params, up to service implementor to decide how to interpret these """

    class Config:
        alias_generator = to_camel

    def __str__(self):
        """Override string to display dictionary"""
        return " - ".join([f"{k}: {v}" for k, v in self.dict().items() if v is not None])
