from monite.server.assebmly import register_routers
from monite.server.configs import UVICORN_LOGGING_CONFIG

from .routers import apps

app = register_routers(routers=apps)
