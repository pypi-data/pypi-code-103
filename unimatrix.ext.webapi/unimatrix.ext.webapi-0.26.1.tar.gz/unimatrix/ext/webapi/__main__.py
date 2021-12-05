# pylint: skip-file
import argparse
import os

import ioc.loader
import uvicorn
import unimatrix.runtime
from unimatrix.conf import settings
from unimatrix.lib import environ

from .asgi import Application


parser = argparse.ArgumentParser()
parser.add_argument('app')
parser.add_argument('--host',
    default=os.getenv('HTTP_HOST') or "0.0.0.0", # nosec
    help="Bind socket to this host."
)
parser.add_argument('--port',
    type=int,
    default=os.getenv('HTTP_PORT') or 8000,
    help="Bind socket to this port."
)


if __name__ == '__main__':
    args = parser.parse_args()
    qualname = str.replace(args.app, ':', '.')
    os.environ.setdefault('UNIMATRIX_SETTINGS_MODULE',
        unimatrix.runtime.get_settings_module(qualname))
    application = ioc.loader.import_symbol(qualname)
    uvicorn.run(
        application,
        host=args.host,
        forwarded_allow_ips=os.getenv('FORWARDED_ALLOW_IPS'),
        port=args.port,
    )
