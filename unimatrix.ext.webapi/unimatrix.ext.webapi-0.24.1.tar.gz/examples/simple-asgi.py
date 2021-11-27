"""Run a rudimentary ASGI server with a function-based
response handler.
"""
import uvicorn

from unimatrix.ext import webapi

from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials


app = webapi.Application(
    allowed_hosts=['*'],
    dependencies=[Depends(HTTPBearer(auto_error=False))]
)


from fastapi import Depends
from fastapi.security import OpenIdConnect


scheme = OpenIdConnect(
    openIdConnectUrl="https://accounts.google.com/.well-known/openid-configuration"
)

@app.get("/items/")
async def handler():
    pass


if __name__ == '__main__':
    uvicorn.run(app,
        host="127.0.0.1",
        port=5000,
        log_level="info"
    )
