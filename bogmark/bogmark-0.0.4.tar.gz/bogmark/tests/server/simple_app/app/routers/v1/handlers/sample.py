from fastapi import APIRouter, FastAPI, HTTPException

from monite.server.assebmly import set_allowed_responses
from monite.server.mixin import ConfigMixin
from monite.structures.context import get_current_request_id, set_current_request_id

app = FastAPI()
router = APIRouter()


class Response(ConfigMixin):
    result: str


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/test_context")
async def read_root():
    if "lala" != get_current_request_id():
        return {"error": True}
    new_rid = "new_lala"
    set_current_request_id(new_rid)
    if new_rid != get_current_request_id():
        return {"error": True}
    return {"error": False}


@router.get("/httpError", responses=set_allowed_responses([409]))
def raise_http_error():
    raise HTTPException(status_code=400, detail="simple error")


@router.get("/httpErrorValidation")
def raise_http_error():
    raise HTTPException(status_code=422, detail="simple error")
