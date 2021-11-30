#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _
from libervia.server import session_iface
from sat.core.log import getLogger

log = getLogger(__name__)

access = C.PAGES_ACCESS_PUBLIC
template = "invitation/welcome.html"


async def parse_url(self, request):
    """check invitation id in URL and start session if needed

    if a session already exists for an other guest/profile, it will be purged
    """
    try:
        invitation_id = self.nextPath(request)
    except IndexError:
        self.pageError(request)

    sat_session, guest_session = self.host.getSessionData(
        request, session_iface.ISATSession, session_iface.ISATGuestSession
    )
    current_id = guest_session.id

    if current_id is not None and current_id != invitation_id:
        log.info(
            _(
                "killing guest session [{old_id}] because it is connecting with an other ID [{new_id}]"
            ).format(old_id=current_id, new_id=invitation_id)
        )
        self.host.purgeSession(request)
        sat_session, guest_session = self.host.getSessionData(
            request, session_iface.ISATSession, session_iface.ISATGuestSession
        )
        current_id = None  # FIXME: id not reset here
        profile = None

    profile = sat_session.profile
    if profile is not None and current_id is None:
        log.info(
            _(
                "killing current profile session [{profile}] because a guest id is used"
            ).format(profile=profile)
        )
        self.host.purgeSession(request)
        sat_session, guest_session = self.host.getSessionData(
            request, session_iface.ISATSession, session_iface.ISATGuestSession
        )
        profile = None

    if current_id is None:
        log.debug(_("checking invitation [{id}]").format(id=invitation_id))
        try:
            data = await self.host.bridgeCall("invitationGet", invitation_id)
        except Exception:
            self.pageError(request, C.HTTP_FORBIDDEN)
        else:
            guest_session.id = invitation_id
            guest_session.data = data
    else:
        data = guest_session.data

    if profile is None:
        log.debug(_("connecting profile [{}]").format(profile))
        # we need to connect the profile
        profile = data["guest_profile"]
        password = data["password"]
        try:
            await self.host.connect(request, profile, password)
        except Exception as e:
            log.warning(_("Can't connect profile: {msg}").format(msg=e))
            # FIXME: no good error code correspond
            #        maybe use a custom one?
            self.pageError(request, code=C.HTTP_SERVICE_UNAVAILABLE)

        log.info(
            _(
                "guest session started, connected with profile [{profile}]".format(
                    profile=profile
                )
            )
        )

    # we copy data useful in templates
    template_data = request.template_data
    template_data["norobots"] = True
    if "name" in data:
        template_data["name"] = data["name"]
    if "language" in data:
        template_data["locale"] = data["language"]

def handleEventInterest(self, interest):
    if C.bool(interest.get("creator", C.BOOL_FALSE)):
        page_name = "event_admin"
    else:
        page_name = "event_rsvp"

    interest["url"] = self.getPageByName(page_name).getURL(
        interest.get("service", ""),
        interest.get("node", ""),
        interest.get("item"),
        )

    if "thumb_url" not in interest and "image" in interest:
        interest["thumb_url"] = interest["image"]

def handleFISInterest(self, interest):
    path = interest.get('path', '')
    path_args = [p for p in path.split('/') if p]
    subtype = interest.get('subtype')

    if subtype == 'files':
        page_name = "files_view"
    elif interest.get('subtype') == 'photos':
        page_name = "photos_album"
    else:
        log.warning("unknown interest subtype: {subtype}".format(subtype=subtype))
        return False

    interest["url"] = self.getPageByName(page_name).getURL(
        interest['service'], *path_args)

async def prepare_render(self, request):
    template_data = request.template_data
    profile = self.getProfile(request)

    # interests
    template_data['interests_map'] = interests_map = {}
    try:
        interests = await self.host.bridgeCall(
            "interestsList", "", "", "", profile)
    except Exception:
        log.warning(_("Can't get interests list for {profile}").format(
            profile=profile))
    else:
        # we only want known interests (photos and events for now)
        # this dict map namespaces of interest to a callback which can manipulate
        # the data. If it returns False, the interest is skipped
        ns_data = {}

        for short_name, cb in (('event', handleEventInterest),
                               ('fis', handleFISInterest),
                              ):
            try:
                namespace = self.host.ns_map[short_name]
            except KeyError:
                pass
            else:
                ns_data[namespace] = (cb, short_name)

        for interest in interests:
            namespace = interest.get('namespace')
            if namespace not in ns_data:
                continue
            cb, short_name = ns_data[namespace]
            if cb(self, interest) == False:
                continue
            key = interest.get('subtype', short_name)
            interests_map.setdefault(key, []).append(interest)

    # main URI
    guest_session = self.host.getSessionData(request, session_iface.ISATGuestSession)
    main_uri = guest_session.data.get("event_uri")
    if main_uri:
        include_url = self.getPagePathFromURI(main_uri)
        if include_url is not None:
            template_data["include_url"] = include_url
