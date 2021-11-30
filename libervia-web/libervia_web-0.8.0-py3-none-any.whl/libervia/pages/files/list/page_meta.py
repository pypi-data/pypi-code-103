#!/usr/bin/env python3

import json
import os
from pathlib import Path
from sat.core.log import getLogger
from sat.tools.common import uri
from sat_frontends.bridge.bridge_frontend import BridgeException
from libervia.server.constants import Const as C
from libervia.server import session_iface
from libervia.server import pages_tools

log = getLogger(__name__)
"""files handling pages"""

name = "files_list"
access = C.PAGES_ACCESS_PROFILE
template = "file/overview.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "*path"], min_args=1, service="jid", path="")


def add_breadcrumb(self, request, breadcrumbs):
    data = self.getRData(request)
    breadcrumbs.append({
        "label": data["service"],
        "url": self.getURL(data["service"].full()),
        "icon": "server",
    })
    for idx, p in enumerate(data["path"]):
        breadcrumbs.append({
            "label": p,
            "url": self.getURL(data["service"].full(), *data["path"][:idx+1]),
            "icon": "folder-open-empty",
        })


async def prepare_render(self, request):
    data = self.getRData(request)
    thumb_limit = data.get("thumb_limit", 400)
    template_data = request.template_data
    service, path_elts = data["service"], data["path"]
    path = Path('/', *path_elts)
    profile = self.getProfile(request) or C.SERVICE_PROFILE
    session_data = self.host.getSessionData(
        request, session_iface.ISATSession
    )

    try:
        files_data = await self.host.bridgeCall(
            "FISList", service.full(), str(path), {}, profile)
    except BridgeException as e:
        if e.condition == 'item-not-found':
            log.debug(
                f'"item-not-found" received for {path} at {service}, this may indicate '
                f'that the location is new')
            files_data = []
        else:
            raise e
    for file_data in files_data:
        try:
            extra_raw = file_data["extra"]
        except KeyError:
            pass
        else:
            file_data["extra"] = json.loads(extra_raw) if extra_raw else {}
        dir_path = path_elts + [file_data["name"]]
        if file_data["type"] == C.FILE_TYPE_DIRECTORY:
            page = self
        elif file_data["type"] == C.FILE_TYPE_FILE:
            page = self.getPageByName("files_view")

            # we set URL for the last thumbnail which has a size below thumb_limit
            try:
                thumbnails = file_data["extra"]["thumbnails"]
                thumb = thumbnails[0]
                for thumb_data in thumbnails:
                    if thumb_data["size"][0] > thumb_limit:
                        break
                    thumb = thumb_data
                file_data["thumb_url"] = (
                    thumb.get("url")
                    or os.path.join(session_data.cache_dir, thumb["filename"])
                )
            except (KeyError, IndexError):
                pass
        else:
            raise ValueError(
                "unexpected file type: {file_type}".format(file_type=file_data["type"])
            )
        file_data["url"] = page.getURL(service.full(), *dir_path)

        ## comments ##
        comments_url = file_data.get("comments_url")
        if comments_url:
            parsed_url = uri.parseXMPPUri(comments_url)
            comments_service = file_data["comments_service"] = parsed_url["path"]
            comments_node = file_data["comments_node"] = parsed_url["node"]
            try:
                comments_count = file_data["comments_count"] = int(
                    file_data["comments_count"]
                )
            except KeyError:
                comments_count = None
            if comments_count and data.get("retrieve_comments", False):
                file_data["comments"] = await pages_tools.retrieveComments(
                    self, comments_service, comments_node, profile=profile
                )

    # parent dir affiliation
    # TODO: some caching? What if affiliation changes?

    try:
        affiliations = await self.host.bridgeCall(
            "FISAffiliationsGet", service.full(), "", str(path), profile
        )
    except BridgeException as e:
        if e.condition == 'item-not-found':
            log.debug(
                f'"item-not-found" received for {path} at {service}, this may indicate '
                f'that the location is new')
            # FIXME: Q&D handling of empty dir (e.g. new directory/photos album)
            affiliations = {
                session_data.jid.userhost(): "owner"
            }
        if e.condition == "service-unavailable":
            affiliations = {}
        else:
            raise e

    directory_affiliation = affiliations.get(session_data.jid.userhost())
    if directory_affiliation == "owner":
        # we need to transtype dict items to str because with some bridges (D-Bus)
        # we have a specific type which can't be exposed
        self.exposeToScripts(
            request,
            affiliations={str(e): str(a) for e, a in affiliations.items()}
        )

    template_data["directory_affiliation"] = directory_affiliation
    template_data["files_data"] = files_data
    template_data["path"] = path
    self.exposeToScripts(
        request,
        directory_affiliation=str(directory_affiliation),
        files_service=service.full(),
        files_path=str(path),
    )
    if path_elts:
        template_data["parent_url"] = self.getURL(service.full(), *path_elts[:-1])
