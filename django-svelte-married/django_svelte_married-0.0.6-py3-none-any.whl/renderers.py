import json

import requests
from django.utils.log import request_logger
from requests.exceptions import ConnectionError

from .settings import (SVELTE_RENDERER_HOSTNAME, SVELTE_RENDERER_PORT, SVELTE_RENDERER_ENABLED)


def local_renderer(component: str, props: any = None) -> str:
    if not SVELTE_RENDERER_ENABLED:
        return ""
    try:
        if not isinstance(props, str):
            props = json.dumps(props)
        resp = requests.post(f"http://{SVELTE_RENDERER_HOSTNAME}:{SVELTE_RENDERER_PORT}/", json=dict(component=component, props=props))
        if resp.status_code >= 300:
            request_logger.warn("Renderer backend responded with incorrect status code.")
            return ""
        try:
            return resp.json()['html']
        except Exception as e:
            request_logger.error("Renderer backend returned malformed, likely non-json response.")
            request_logger.error(e)
    except ConnectionError:
        request_logger.warn("Error when connecting to renderer backend.")
    return ""
