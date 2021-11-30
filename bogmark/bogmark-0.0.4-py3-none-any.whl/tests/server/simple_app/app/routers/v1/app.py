from monite.server.assebmly import compile_routers

from .handlers import sample

routers = [
    {"router": sample.router, "tags": ["Simples"], "prefix": ""},
]

compiled_routers = compile_routers(routers=routers, root_prefix="/v1")
