# pylint: skip-file
import os

import uvicorn

from unimatrix.ext import webapi


os.environ.setdefault('UNIMATRIX_SETTINGS_MODULE', __name__)

OAUTH2_UPSTREAM = "https://chevron.webidentity.id"

OAUTH2_TRUSTED_STS = "https://sts.unimatrixapis.com"

app = webapi.Service(
    allowed_hosts="*"
)


class Protected(webapi.EndpointSet):
    trust_policy = webapi.policy(['oauth2.sts'])

    async def index(self):
        pass


Protected.add_to_router(app, '/')

if __name__ == '__main__':
    uvicorn.run(app,
        host="127.0.0.1",
        port=5000,
        log_level="info"
    )
