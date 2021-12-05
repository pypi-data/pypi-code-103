# pylint: skip-file
import os

import uvicorn

from unimatrix.ext import webapi


app = webapi.Service(
    allowed_hosts="*"
)


class PathSlashes(webapi.PublicEndpointSet):
    path_parameter      = 'parent'
    path_allows_slashes = True

    async def retrieve(self, parent: str):
        return parent


PathSlashes.add_to_router(app, '/foo')
PathSlashes.add_to_router(app, '/')

if __name__ == '__main__':
    uvicorn.run(app,
        host="127.0.0.1",
        port=5000,
        log_level="info"
    )

