from myst.client import Client

from ...models.user_create import UserCreate
from ...models.user_get import UserGet


def request_sync(client: Client, json_body: UserCreate) -> UserGet:
    """Creates a user."""

    return client.request(method="post", path=f"/users/", response_class=UserGet, request_model=json_body)
