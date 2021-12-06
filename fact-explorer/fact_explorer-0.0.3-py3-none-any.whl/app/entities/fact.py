from pydantic import BaseModel, Json


class FactOut(BaseModel):
    header: Json
    payload: Json


# TODO find a better way to do decrypt stuff
