# pylint: skip-file
import os

import uvicorn

from unimatrix.ext import webapi


os.environ.setdefault('UNIMATRIX_SETTINGS_MODULE', __name__)

HTTP_CONSUMED_APIS = [
    'https://sts.unimatrixapis.com',
    'https://api.example.com',
    'https://api.molano.nl',
    'https://google.com:5000'
]

app = webapi.Service(
    allowed_hosts="*",
    ping_timeout=1
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

