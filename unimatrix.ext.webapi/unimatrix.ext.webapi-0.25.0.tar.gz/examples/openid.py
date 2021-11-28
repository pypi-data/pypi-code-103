# pylint: skip-file
import uvicorn

from unimatrix.ext import webapi




OPENID_PROVIDERS = {
    "https://molano.webidentity.id": {
        "audience": "https://molano.webidentity.id",
        "tags": ["webid:molano"]
    }
}

app = webapi.Application(
    allowed_hosts='*',
    debug=True,
    openid_providers=OPENID_PROVIDERS
)


if __name__ == '__main__':
    uvicorn.run('__main__:app', reload=True)
