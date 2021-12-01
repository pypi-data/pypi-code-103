from uvicorn.workers import UvicornWorker


class ZygoatUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "auto", "http": "auto", "headers": [["server", ""]]}
