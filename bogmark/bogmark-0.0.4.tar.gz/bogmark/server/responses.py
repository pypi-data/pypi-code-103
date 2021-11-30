from pydantic import BaseModel


class ErrorSchema(BaseModel):
    message: str


class ErrorSchemaResponse(BaseModel):
    error: ErrorSchema
