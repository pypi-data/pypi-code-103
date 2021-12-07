from datetime import datetime

from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest
from django.views import View

from .settings import PARAM, TIMEOUT, USE_PUBLIC_NAMESPACE, PUBLIC_NAMESPACE
from .storage import TitofistoStorage


class TitofistoMediaView(View):
    def get(self, request: HttpRequest, name: str) -> FileResponse:
        # Get storage
        storage = TitofistoStorage()

        if USE_PUBLIC_NAMESPACE:
            # Public files are directly served without needing a token
            if name.startswith(PUBLIC_NAMESPACE):
                return FileResponse(storage._open(name))

        # Inspect URL parameter for completeness and extract timestamp
        token = request.GET.get(PARAM, None)
        if token is None:
            raise Http404()
        try:
            ts = int(token[64:], 16)
        except ValueError:
            raise Http404()

        # Compute expected token for filename
        try:
            expected_token = storage.get_token(name, ts)
        except FileNotFoundError:
            raise Http404()

        # Compare tokens and raise 404 if they do not match
        if expected_token != token:
            raise Http404()

        # Calculate time difference if timeout is set
        now = int(datetime.now().strftime("%s"))
        if TIMEOUT is not None and now - ts > TIMEOUT:
            raise Http404()

        # Finally, serve file from disk if all checks passed
        return FileResponse(storage._open(name))
