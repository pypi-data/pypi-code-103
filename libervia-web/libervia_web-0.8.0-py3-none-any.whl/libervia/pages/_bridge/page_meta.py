#!/usr/bin/env python3

import json
from sat.core.i18n import _
from sat.core.log import getLogger
from sat_frontends.bridge.bridge_frontend import BridgeException
from libervia.server.constants import Const as C


log = getLogger(__name__)
"""access to restricted bridge"""

name = "bridge"
on_data_post = "continue"

# bridge method allowed when no profile is connected
NO_SESSION_ALLOWED = ("getContacts", "identitiesBaseGet", "identitiesGet")


def parse_url(self, request):
    self.getPathArgs(request, ["method_name"], min_args=1)


async def render(self, request):
    if request.method != b'POST':
        log.warning(f"Bad method used with _bridge endpoint: {request.method.decode()}")
        return self.pageError(request, C.HTTP_BAD_REQUEST)
    data = self.getRData(request)
    profile = self.getProfile(request)
    self.checkCSRF(request)
    method_name = data["method_name"]
    if profile is None:
        if method_name in NO_SESSION_ALLOWED:
            # this method is allowed, we use the service profile
            profile = C.SERVICE_PROFILE
        else:
            log.warning("_bridge endpoint accessed without authorisation")
            return self.pageError(request, C.HTTP_UNAUTHORIZED)
    method_data = json.load(request.content)
    try:
        bridge_method = getattr(self.host.restricted_bridge, method_name)
    except AttributeError:
        log.warning(_(
            "{profile!r} is trying to access a bridge method not implemented in "
            "RestrictedBridge: {method_name}").format(
                profile=profile, method_name=method_name))
        return self.pageError(request, C.HTTP_BAD_REQUEST)

    try:
        args, kwargs = method_data['args'], method_data['kwargs']
    except KeyError:
        log.warning(_(
            "{profile!r} has sent a badly formatted method call: {method_data}"
        ).format(profile=profile, method_data=method_data))
        return self.pageError(request, C.HTTP_BAD_REQUEST)

    if "profile" in kwargs or "profile_key" in kwargs:
        log.warning(_(
            '"profile" key should not be in method kwargs, hack attempt? '
            "profile={profile}, method_data={method_data}"
        ).format(profile=profile, method_data=method_data))
        return self.pageError(request, C.HTTP_BAD_REQUEST)

    try:
        ret = await bridge_method(*args, **kwargs, profile=profile)
    except BridgeException as e:
        request.setResponseCode(C.HTTP_PROXY_ERROR)
        ret = {
            "fullname": e.fullname,
            "message": e.message,
            "condition": e.condition,
            "module": e.module,
            "classname": e.classname,
        }
    return json.dumps(ret)
