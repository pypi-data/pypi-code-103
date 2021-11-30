#!/usr/bin/env python3


from libervia.server.constants import Const as C
from libervia.server import session_iface
from twisted.internet import defer
from sat.core.log import getLogger

log = getLogger(__name__)

"""SàT account registration page"""

name = "register"
access = C.PAGES_ACCESS_PUBLIC
template = "login/register.html"


def prepare_render(self, request):
    if not self.host.options["allow_registration"]:
        self.pageError(request, C.HTTP_FORBIDDEN)
    profile = self.getProfile(request)
    if profile is not None:
        self.pageRedirect("/login/logged", request)
    template_data = request.template_data
    template_data["login_url"] = self.getPageByName("login").url
    template_data["S_C"] = C  # we need server constants in template

    # login error message
    session_data = self.host.getSessionData(request, session_iface.ISATSession)
    login_error = session_data.popPageData(self, "login_error")
    if login_error is not None:
        template_data["login_error"] = login_error

    #  if fields were already filled, we reuse them
    for k in ("login", "email", "password"):
        template_data[k] = session_data.popPageData(self, k)


@defer.inlineCallbacks
def on_data_post(self, request):
    type_ = self.getPostedData(request, "type")
    if type_ == "register":
        login, email, password = self.getPostedData(
            request, ("login", "email", "password")
        )
        status = yield self.host.registerNewAccount(request, login, password, email)
        session_data = self.host.getSessionData(request, session_iface.ISATSession)
        if status == C.REGISTRATION_SUCCEED:
            # we prefill login field for login page
            session_data.setPageData(self.getPageByName("login"), "login", login)
            # if we have a redirect_url we follow it
            self.redirectOrContinue(request)
            # else we redirect to login page
            self.HTTPRedirect(request, self.getPageByName("login").url)
        else:
            session_data.setPageData(self, "login_error", status)
            l = locals()
            for k in ("login", "email", "password"):
                # we save fields so user doesn't have to enter them again
                session_data.setPageData(self, k, l[k])
            defer.returnValue(C.POST_NO_CONFIRM)
    else:
        self.pageError(request, C.HTTP_BAD_REQUEST)
