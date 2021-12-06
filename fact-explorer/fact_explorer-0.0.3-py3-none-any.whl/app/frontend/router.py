from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(
    prefix="/fe",
    responses={404: {"description": "Not Found!"}},
    include_in_schema=False,
)

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.joinpath("templates"))
)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    context = {"title": "Home", "request": request}
    response = templates.TemplateResponse(
        "home.jinja2",
        context=context,
    )
    return response
