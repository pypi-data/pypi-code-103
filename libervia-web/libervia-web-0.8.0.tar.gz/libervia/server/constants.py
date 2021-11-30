#!/usr/bin/env python3

# Libervia: a SàT frontend
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ..common import constants


class Const(constants.Const):

    APP_NAME = "Libervia Web"
    APP_COMPONENT = "web"
    APP_NAME_ALT = APP_NAME
    APP_NAME_FILE = "libervia_web"
    CONFIG_SECTION = APP_COMPONENT.lower()
    # the Libervia profile that is used for public operations (when nobody is connected)
    SERVICE_PROFILE = "libervia"

    SESSION_TIMEOUT = 7200  # Session's timeout, after that the user will be disconnected
    HTML_DIR = "html/"
    THEMES_DIR = "themes/"
    THEMES_URL = "themes"
    MEDIA_DIR = "media/"
    CARDS_DIR = "games/cards/tarot"
    PAGES_DIR = "pages"
    TASKS_DIR = "tasks"
    LIBERVIA_CACHE = "libervia"
    SITE_NAME_DEFAULT = "default"
    # generated files will be accessible there
    BUILD_DIR = "__b"
    BUILD_DIR_DYN = "dyn"
    # directory where build files are served to the client
    PRODUCTION_BUILD_DIR = "sites"
    # directory used for files needed temporarily (e.g. for compiling other files)
    DEV_BUILD_DIR = "dev_build"

    TPL_RESOURCE = '_t'

    ERRNUM_BRIDGE_ERRBACK = 0  # FIXME
    ERRNUM_LIBERVIA = 0  # FIXME

    # Security limit for Libervia (get/set params)
    SECURITY_LIMIT = 5

    # Security limit for Libervia server_side
    SERVER_SECURITY_LIMIT = constants.Const.NO_SECURITY_LIMIT

    # keys for cache values we can get from browser
    ALLOWED_ENTITY_DATA = {"avatar", "nick"}

    STATIC_RSM_MAX_LIMIT = 100
    STATIC_RSM_MAX_DEFAULT = 10
    STATIC_RSM_MAX_COMMENTS_DEFAULT = 10

    ## Libervia pages ##
    PAGES_META_FILE = "page_meta.py"
    PAGES_BROWSER_DIR = "_browser"
    PAGES_BROWSER_META_FILE = "browser_meta.json"
    PAGES_ACCESS_NONE = (
        "none"
    )  #  no access to this page (using its path will return a 404 error)
    PAGES_ACCESS_PUBLIC = "public"
    PAGES_ACCESS_PROFILE = (
        "profile"
    )  # a session with an existing profile must be started
    PAGES_ACCESS_ADMIN = "admin"  #  only profiles set in admins_list can access the page
    PAGES_ACCESS_ALL = (
        PAGES_ACCESS_NONE,
        PAGES_ACCESS_PUBLIC,
        PAGES_ACCESS_PROFILE,
        PAGES_ACCESS_ADMIN,
    )
    # names of the page to use for menu
    DEFAULT_MENU = [
        "login",
        "chat",
        "blog",
        "forums",
        "photos",
        "files",
        "events",
        "lists",
        "merge-requests",
        # XXX: app is not available anymore since removal of pyjamas code with Python 3
        #    port. It should come back at a later point with an alternative (Brython
        #    probably).
    ]

    ## Session flags ##
    FLAG_CONFIRM = "CONFIRM"

    ## Data post ##
    POST_NO_CONFIRM = "POST_NO_CONFIRM"

    ## HTTP methods ##
    HTTP_METHOD_GET = b"GET"
    HTTP_METHOD_POST = b"POST"

    ## HTTP codes ##
    HTTP_SEE_OTHER = 303
    HTTP_NOT_MODIFIED = 304
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_INTERNAL_ERROR = 500
    HTTP_PROXY_ERROR = 502
    HTTP_SERVICE_UNAVAILABLE = 503

    ## HTTP HEADERS ##
    H_FORWARDED = "Forwarded"
    H_X_FORWARDED_FOR = "X-Forwarded-For"
    H_X_FORWARDED_HOST = "X-Forwarded-Host"
    H_X_FORWARDED_PROTO = "X-Forwarded-Proto"


    ## Cache ##
    CACHE_PUBSUB = 0

    ## Date/Time ##
    HTTP_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    HTTP_MONTH = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                  "Nov", "Dec")
