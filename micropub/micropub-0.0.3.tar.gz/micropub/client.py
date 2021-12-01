"""Micropub clients (editors)."""

from understory import web
from understory.web import tx

__all__ = ["create_post"]


class PostNotCreated(Exception):
    """Post failed to be created."""


def create_post(properties, endpoint=None, h="entry", token=None):
    """Send a Micropub request to a Micropub server."""
    if endpoint is None:
        endpoint = tx.user.session["micropub_endpoint"]
    response = web.post(
        endpoint,
        headers={"Authorization": f"Bearer {token}"},
        json={"type": [f"h-{h}"], "properties": properties},
    )
    if response.status != 201:
        raise PostNotCreated()
    return response.location, response.links
