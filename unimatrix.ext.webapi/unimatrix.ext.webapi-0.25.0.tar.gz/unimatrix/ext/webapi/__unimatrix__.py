# pylint: skip-file
import ioc

from .auth import HTTPAuthenticationService


async def on_setup(*args, **kwargs):
    if not ioc.is_satisfied('HTTPAuthenticationService'):
        ioc.provide(
            'HTTPAuthenticationService',
            HTTPAuthenticationService()
        )
