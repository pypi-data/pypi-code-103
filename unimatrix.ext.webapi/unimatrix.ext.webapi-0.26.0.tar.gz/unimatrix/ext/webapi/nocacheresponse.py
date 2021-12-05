"""Declares :class:`NoCacheResponse`."""
from fastapi.responses import JSONResponse


class NoCacheResponse(JSONResponse):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
        self.headers['Pragma'] = "no-cache"
        self.headers['Expires'] = "0"
