from typing import Optional

from pydantic import BaseModel, validator


class UserProperties(BaseModel):
    gender: Optional[str]

    @validator("gender")
    def gender_must_be_valid(cls, v) -> str:
        if not (v == "male" or v == "female"):
            raise ValueError("Must be of the two valid genders above")
        return v


class UserPropertyUpdate:
    def __init__(self, user_id, user_properties: UserProperties):
        self.user_id = user_id
        self.user_properties = user_properties
