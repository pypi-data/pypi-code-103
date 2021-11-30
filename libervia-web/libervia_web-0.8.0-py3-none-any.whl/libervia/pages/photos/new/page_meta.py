#!/usr/bin/env python3

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.log import getLogger
from sat.core.i18n import D_
from sat.core import exceptions
from sat_frontends.bridge.bridge_frontend import BridgeException

"""creation of new events"""

name = "photos_new"
access = C.PAGES_ACCESS_PROFILE
template = "photo/create.html"
log = getLogger(__name__)


async def on_data_post(self, request):
    request_data = self.getRData(request)
    profile = self.getProfile(request)
    name = self.getPostedData(request, "name").replace('/', '_')
    albums_path = "/albums"
    album_path = f"{albums_path}/{name}"
    if profile is None:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    fis_ns = self.host.ns_map["fis"]
    http_upload_ns = self.host.ns_map["http_upload"]
    entities_services, __, __ = await self.host.bridgeCall(
        "discoFindByFeatures",
        [fis_ns, http_upload_ns],
        [],
        False,
        True,
        False,
        False,
        False,
        profile
    )
    try:
        fis_service = next(iter(entities_services))
    except StopIteration:
        raise exceptions.DataError(D_(
           "You server has no service to create a photo album, please ask your server "
           "administrator to add one"))

    try:
        await self.host.bridgeCall(
            "FISCreateDir",
            fis_service,
            "",
            albums_path,
            {"access_model": "open"},
            profile
        )
    except BridgeException as e:
        if e.condition == 'conflict':
            pass
        else:
            log.error(f"Can't create {albums_path} path: {e}")
            raise e

    try:
        await self.host.bridgeCall(
            "FISCreateDir",
            fis_service,
            "",
            album_path,
            {"access_model": "whitelist"},
            profile
        )
    except BridgeException as e:
        if e.condition == 'conflict':
            pass
        else:
            log.error(f"Can't create {album_path} path: {e}")
            raise e

    await self.host.bridgeCall(
        "interestsRegisterFileSharing",
        fis_service,
        "photos",
        "",
        album_path,
        name,
        "",
        profile
    )
    log.info(f"album {name} created")
    request_data["post_redirect_page"] = self.getPageByName("photos")
    defer.returnValue(C.POST_NO_CONFIRM)
