from fastapi import status
from fastapi.exceptions import HTTPException, StarletteHTTPException
from fastapi.responses import ORJSONResponse


def http_exception(request, exc: HTTPException):  # noqa
    response_data = {
        "error": {
            "message": exc.detail,
        }
    }
    status_code = getattr(exc, "status_code", 500)
    if status_code == 422:
        return ORJSONResponse(content=exc.detail, status_code=status_code)
    return ORJSONResponse(content=response_data, status_code=status_code)


def application_exception(request, exc):  # noqa
    response_data = {
        "error": {
            "message": "Server Error",
        }
    }
    status_code = getattr(exc, "status_code", 500)

    # Invalid API headers
    if status_code == 415:
        response_data = {
            "error": {
                "message": exc.detail,
            }
        }
        return ORJSONResponse(content=response_data, status_code=status_code, headers=exc.headers)
    return ORJSONResponse(content=response_data, status_code=status_code)


def register_errors(app):
    app.add_exception_handler(StarletteHTTPException, http_exception)
    app.add_exception_handler(Exception, application_exception)
