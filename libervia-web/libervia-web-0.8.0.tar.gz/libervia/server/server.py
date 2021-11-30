#!/usr/bin/env python3

# Libervia Web
# Copyright (C) 2011-2021 Jérôme Poisson <goffi@goffi.org>

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

import re
import os.path
import sys
import urllib.parse
import urllib.request, urllib.error
import time
import copy
from typing import Optional
from pathlib import Path
from twisted.application import service
from twisted.internet import reactor, defer, inotify
from twisted.web import server
from twisted.web import static
from twisted.web import resource as web_resource
from twisted.web import util as web_util
from twisted.web import vhost
from . import proxy
from twisted.python.components import registerAdapter
from twisted.python import failure
from twisted.python import filepath
from twisted.words.protocols.jabber import jid

from sat.core.log import getLogger

from sat_frontends.bridge.dbus_bridge import (
    Bridge,
    BridgeExceptionNoService,
    const_TIMEOUT as BRIDGE_TIMEOUT,
)
from sat.core.i18n import _, D_
from sat.core import exceptions
from sat.tools import utils
from sat.tools import config
from sat.tools.common import regex
from sat.tools.common import template
from sat.tools.common import uri as common_uri
from sat.tools.common.utils import recursive_update, OrderedSet
from sat.tools.common import data_format
from sat.tools.common import tls
from sat_frontends.bridge.bridge_frontend import BridgeException
import libervia
from libervia.server import websockets
from libervia.server.pages import LiberviaPage
from libervia.server.utils import quote, ProgressHandler
from libervia.server.tasks.manager import TasksManager
from functools import partial

from libervia.server.constants import Const as C
from libervia.server import session_iface
from .restricted_bridge import RestrictedBridge

log = getLogger(__name__)


DEFAULT_MASK = (inotify.IN_CREATE | inotify.IN_MODIFY | inotify.IN_MOVE_SELF
                | inotify.IN_MOVED_TO)


class SysExit(Exception):

    def __init__(self, exit_code, message=""):
        self.exit_code = exit_code
        self.message = message

    def __str__(self):
        return f"System Exit({self.exit_code}): {self.message}"


class FilesWatcher(object):
    """Class to check files modifications using iNotify"""
    _notifier = None

    def __init__(self, host):
        self.host = host

    @property
    def notifier(self):
        if self._notifier == None:
            notifier = self.__class__._notifier = inotify.INotify()
            notifier.startReading()
        return self._notifier

    def _checkCallback(self, dir_path, callback, recursive):
        # Twisted doesn't add callback if a watcher was already set on a path
        # but in dev mode Libervia watches whole sites + internal path can be watched
        # by tasks, so several callbacks must be called on some paths.
        # This method check that the new callback is indeed present in the desired path
        # and add it otherwise.
        # FIXME: this should probably be fixed upstream
        if recursive:
            for child in dir_path.walk():
                if child.isdir():
                    self._checkCallback(child, callback, recursive=False)
        else:
            watch_id = self.notifier._isWatched(dir_path)
            if watch_id is None:
                log.warning(
                    f"There is no watch ID for path {dir_path}, this should not happen"
                )
            else:
                watch_point = self.notifier._watchpoints[watch_id]
                if callback not in watch_point.callbacks:
                    watch_point.callbacks.append(callback)

    def watchDir(self, dir_path, callback, mask=DEFAULT_MASK, auto_add=False,
                 recursive=False, **kwargs):
        dir_path = str(dir_path)
        log.info(_("Watching directory {dir_path}").format(dir_path=dir_path))
        wrapped_callback = lambda __, filepath, mask: callback(
            self.host, filepath, inotify.humanReadableMask(mask), **kwargs)
        callbacks = [wrapped_callback]
        dir_path = filepath.FilePath(dir_path)
        self.notifier.watch(
            dir_path, mask=mask, autoAdd=auto_add, recursive=recursive,
            callbacks=callbacks)
        self._checkCallback(dir_path, wrapped_callback, recursive)


class LiberviaSession(server.Session):
    sessionTimeout = C.SESSION_TIMEOUT

    def __init__(self, *args, **kwargs):
        self.__lock = False
        server.Session.__init__(self, *args, **kwargs)

    def lock(self):
        """Prevent session from expiring"""
        self.__lock = True
        self._expireCall.reset(sys.maxsize)

    def unlock(self):
        """Allow session to expire again, and touch it"""
        self.__lock = False
        self.touch()

    def touch(self):
        if not self.__lock:
            server.Session.touch(self)


class ProtectedFile(static.File):
    """A static.File class which doesn't show directory listing"""

    def __init__(self, path, *args, **kwargs):
        if "defaultType" not in kwargs and len(args) < 2:
            # defaultType is second positional argument, and Twisted uses it
            # in File.createSimilarFile, so we set kwargs only if it is missing
            # in kwargs and it is not in a positional argument
            kwargs["defaultType"] = "application/octet-stream"
        super(ProtectedFile, self).__init__(str(path), *args, **kwargs)

    def directoryListing(self):
        return web_resource.NoResource()


    def getChild(self, path, request):
        return super().getChild(path, request)

    def getChildWithDefault(self, path, request):
        return super().getChildWithDefault(path, request)

    def getChildForRequest(self, request):
        return super().getChildForRequest(request)


class LiberviaRootResource(ProtectedFile):
    """Specialized resource for Libervia root

    handle redirections declared in sat.conf
    """

    def __init__(self, host, host_name, site_name, site_path, *args, **kwargs):
        ProtectedFile.__init__(self, *args, **kwargs)
        self.host = host
        self.host_name = host_name
        self.site_name = site_name
        self.site_path = Path(site_path)
        self.default_theme = self.getConfig('theme')
        if self.default_theme is None:
            if not host_name:
                # FIXME: we use bulma theme by default for main site for now
                #   as the development is focusing on this one, and default theme may
                #   be broken
                self.default_theme = 'bulma'
            else:
                self.default_theme =  C.TEMPLATE_THEME_DEFAULT
        self.site_themes = set()
        self.named_pages = {}
        self.browser_modules = {}
        # template dynamic data used in all pages
        self.dyn_data_common = {"scripts": OrderedSet()}
        for theme, data in host.renderer.getThemesData(site_name).items():
            # we check themes for browser metadata, and merge them here if found
            self.site_themes.add(theme)
            browser_meta = data.get('browser_meta')
            if browser_meta is not None:
                log.debug(f"merging browser metadata from theme {theme}: {browser_meta}")
                recursive_update(self.browser_modules, browser_meta)
            browser_path = data.get('browser_path')
            if browser_path is not None:
                self.browser_modules.setdefault('themes_browser_paths', set()).add(
                    browser_path)
                try:
                    next(browser_path.glob("*.py"))
                except StopIteration:
                    pass
                else:
                    log.debug(f"found brython script(s) for theme {theme}")
                    self.browser_modules.setdefault('brython', []).append(
                        {
                            "path": browser_path,
                            "url_hash": None,
                            "url_prefix": f"__t_{theme}"
                        }
                    )

        self.uri_callbacks = {}
        self.pages_redirects = {}
        self.cached_urls = {}
        self.main_menu = None
        # map Libervia application names => data
        self.libervia_apps = {}
        self.build_path = host.getBuildPath(site_name)
        self.build_path.mkdir(parents=True, exist_ok=True)
        self.dev_build_path = host.getBuildPath(site_name, dev=True)
        self.dev_build_path.mkdir(parents=True, exist_ok=True)
        self.putChild(
            C.BUILD_DIR.encode(),
            ProtectedFile(
                self.build_path,
                defaultType="application/octet-stream"),
        )

    def __str__(self):
        return (
            f"Root resource for {self.host_name or 'default host'} using "
            f"{self.site_name or 'default site'} at {self.site_path} and deserving "
            f"files at {self.path}"
        )

    def getConfig(self, key, default=None, value_type=None):
        """Retrieve configuration for this site

        params are the same as for [Libervia.getConfig]
        """
        return self.host.getConfig(self, key, default, value_type)

    def getFrontURL(self, theme):
        return Path(
            '/',
            C.TPL_RESOURCE,
            self.site_name or C.SITE_NAME_DEFAULT,
            C.TEMPLATE_TPL_DIR,
            theme)

    def addResourceToPath(self, path: str, resource: web_resource.Resource) -> None:
        """Add a resource to the given path

        A "NoResource" will be used for all intermediate segments
        """
        segments, __, last_segment = path.rpartition("/")
        url_segments = segments.split("/") if segments else []
        current = self
        for segment in url_segments:
            resource = web_resource.NoResource()
            current.putChild(segment, resource)
            current = resource

        current.putChild(
            last_segment.encode('utf-8'),
            resource
        )

    async def _startApp(self, app_name, extra=None):
        if extra is None:
            extra = {}
        log.info(_(
            "starting application {app_name}").format(app_name=app_name))
        await self.host.bridgeCall(
            "applicationStart", app_name, data_format.serialise(extra)
        )
        app_data = self.libervia_apps[app_name] = data_format.deserialise(
            await self.host.bridgeCall(
                "applicationExposedGet", app_name, "", ""))

        try:
            web_port = int(app_data['ports']['web'].split(':')[1])
        except (KeyError, ValueError):
            log.warning(_(
                "no web port found for application {app_name!r}, can't use it "
                ).format(app_name=app_name))
            raise exceptions.DataError("no web port found")

        try:
            url_prefix = app_data['url_prefix'].strip().rstrip('/')
        except (KeyError, AttributeError) as e:
            log.warning(_(
                "no URL prefix specified for this application, we can't embed it: {msg}")
                .format(msg=e))
            raise exceptions.DataError("no URL prefix")

        if not url_prefix.startswith('/'):
            raise exceptions.DataError(
                f"invalid URL prefix, it must start with '/': {url_prefix!r}")

        res = proxy.SatReverseProxyResource(
            "localhost",
            web_port,
            url_prefix.encode()
        )
        self.addResourceToPath(url_prefix, res)

        return app_data

    async def _initRedirections(self, options):
        url_redirections = options["url_redirections_dict"]

        url_redirections = url_redirections.get(self.site_name, {})

        ## redirections
        self.redirections = {}
        self.inv_redirections = {}  # new URL to old URL map

        for old, new_data_list in url_redirections.items():
            # several redirections can be used for one path by using a list.
            # The redirection will be done using first item of the list, and all items
            # will be used for inverse redirection.
            # e.g. if a => [b, c], a will redirect to c, and b and c will both be
            # equivalent to a
            if not isinstance(new_data_list, list):
                new_data_list = [new_data_list]
            for new_data in new_data_list:
                # new_data can be a dictionary or a unicode url
                if isinstance(new_data, dict):
                    # new_data dict must contain either "url", "page" or "path" key
                    # (exclusive)
                    # if "path" is used, a file url is constructed with it
                    if ((
                        len(
                            {"path", "url", "page"}.intersection(list(new_data.keys()))
                        ) != 1
                    )):
                        raise ValueError(
                            'You must have one and only one of "url", "page" or "path" '
                            'key in your url_redirections_dict data'
                        )
                    if "url" in new_data:
                        new = new_data["url"]
                    elif "page" in new_data:
                        new = new_data
                        new["type"] = "page"
                        new.setdefault("path_args", [])
                        if not isinstance(new["path_args"], list):
                            log.error(
                                _('"path_args" in redirection of {old} must be a list. '
                                  'Ignoring the redirection'.format(old=old)))
                            continue
                        new.setdefault("query_args", {})
                        if not isinstance(new["query_args"], dict):
                            log.error(
                                _(
                                    '"query_args" in redirection of {old} must be a '
                                    'dictionary. Ignoring the redirection'
                                ).format(old=old)
                            )
                            continue
                        new["path_args"] = [quote(a) for a in new["path_args"]]
                        # we keep an inversed dict of page redirection
                        # (page/path_args => redirecting URL)
                        # so getURL can return the redirecting URL if the same arguments
                        # are used # making the URL consistent
                        args_hash = tuple(new["path_args"])
                        self.pages_redirects.setdefault(new_data["page"], {}).setdefault(
                            args_hash,
                            old
                        )

                        # we need lists in query_args because it will be used
                        # as it in request.path_args
                        for k, v in new["query_args"].items():
                            if isinstance(v, str):
                                new["query_args"][k] = [v]
                    elif "path" in new_data:
                        new = "file:{}".format(urllib.parse.quote(new_data["path"]))
                elif isinstance(new_data, str):
                    new = new_data
                    new_data = {}
                else:
                    log.error(
                        _("ignoring invalid redirection value: {new_data}").format(
                            new_data=new_data
                        )
                    )
                    continue

                # some normalization
                if not old.strip():
                    # root URL special case
                    old = ""
                elif not old.startswith("/"):
                    log.error(
                        _("redirected url must start with '/', got {value}. Ignoring")
                        .format(value=old)
                    )
                    continue
                else:
                    old = self._normalizeURL(old)

                if isinstance(new, dict):
                    # dict are handled differently, they contain data
                    # which ared use dynamically when the request is done
                    self.redirections.setdefault(old, new)
                    if not old:
                        if new["type"] == "page":
                            log.info(
                                _("Root URL redirected to page {name}").format(
                                    name=new["page"]
                                )
                            )
                    else:
                        if new["type"] == "page":
                            page = self.getPageByName(new["page"])
                            url = page.getURL(*new.get("path_args", []))
                            self.inv_redirections[url] = old
                    continue

                # at this point we have a redirection URL in new, we can parse it
                new_url = urllib.parse.urlsplit(new)

                # we handle the known URL schemes
                if new_url.scheme == "xmpp":
                    location = self.getPagePathFromURI(new)
                    if location is None:
                        log.warning(
                            _("ignoring redirection, no page found to handle this URI: "
                              "{uri}").format(uri=new))
                        continue
                    request_data = self._getRequestData(location)
                    self.inv_redirections[location] = old

                elif new_url.scheme in ("", "http", "https"):
                    # direct redirection
                    if new_url.netloc:
                        raise NotImplementedError(
                            "netloc ({netloc}) is not implemented yet for "
                            "url_redirections_dict, it is not possible to redirect to an "
                            "external website".format(netloc=new_url.netloc))
                    location = urllib.parse.urlunsplit(
                        ("", "", new_url.path, new_url.query, new_url.fragment)
                    )
                    request_data = self._getRequestData(location)
                    self.inv_redirections[location] = old

                elif new_url.scheme == "file":
                    # file or directory
                    if new_url.netloc:
                        raise NotImplementedError(
                            "netloc ({netloc}) is not implemented for url redirection to "
                            "file system, it is not possible to redirect to an external "
                            "host".format(
                                netloc=new_url.netloc))
                    path = urllib.parse.unquote(new_url.path)
                    if not os.path.isabs(path):
                        raise ValueError(
                            "file redirection must have an absolute path: e.g. "
                            "file:/path/to/my/file")
                    # for file redirection, we directly put child here
                    resource_class = (
                        ProtectedFile if new_data.get("protected", True) else static.File
                    )
                    res = resource_class(path, defaultType="application/octet-stream")
                    self.addResourceToPath(old, res)
                    log.info("[{host_name}] Added redirection from /{old} to file system "
                             "path {path}".format(host_name=self.host_name,
                                                   old=old,
                                                   path=path))

                    # we don't want to use redirection system, so we continue here
                    continue

                elif new_url.scheme == "libervia-app":
                    # a Libervia application

                    app_name = urllib.parse.unquote(new_url.path).lower().strip()
                    extra = {"url_prefix": f"/{old}"}
                    try:
                        await self._startApp(app_name, extra)
                    except Exception as e:
                        log.warning(_(
                            "Can't launch {app_name!r} for path /{old}: {e}").format(
                            app_name=app_name, old=old, e=e))
                        continue

                    log.info("[{host_name}] Added redirection from /{old} to application "
                             "{app_name}".format(
                                 host_name=self.host_name,
                                 old=old,
                                 app_name=app_name))

                    # normal redirection system is not used here
                    continue
                else:
                    raise NotImplementedError(
                        "{scheme}: scheme is not managed for url_redirections_dict".format(
                            scheme=new_url.scheme
                        )
                    )

                self.redirections.setdefault(old, request_data)
                if not old:
                    log.info(_("[{host_name}] Root URL redirected to {uri}")
                        .format(host_name=self.host_name,
                                uri=request_data[1]))

        # the default root URL, if not redirected
        if not "" in self.redirections:
            self.redirections[""] = self._getRequestData(C.LIBERVIA_PAGE_START)

    async def _setMenu(self, menus):
        menus = menus.get(self.site_name, [])
        main_menu = []
        for menu in menus:
            if not menu:
                msg = _("menu item can't be empty")
                log.error(msg)
                raise ValueError(msg)
            elif isinstance(menu, list):
                if len(menu) != 2:
                    msg = _(
                        "menu item as list must be in the form [page_name, absolue URL]"
                    )
                    log.error(msg)
                    raise ValueError(msg)
                page_name, url = menu
            elif menu.startswith("libervia-app:"):
                app_name = menu[13:].strip().lower()
                app_data = await self._startApp(app_name)
                front_url = app_data['front_url']
                options = self.host.options
                url_redirections = options["url_redirections_dict"].setdefault(
                    self.site_name, {})
                if front_url in url_redirections:
                    raise exceptions.ConflictError(
                        f"There is already a redirection from {front_url!r}, can't add "
                        f"{app_name!r}")

                url_redirections[front_url] = {
                    "page": 'embed_app',
                    "path_args": [app_name]
                }

                page_name = app_data.get('web_label', app_name).title()
                url = front_url

                log.debug(
                    f"Application {app_name} added to menu of {self.site_name}"
                )
            else:
                page_name = menu
                try:
                    url = self.getPageByName(page_name).url
                except KeyError as e:
                    log_msg = _("Can'find a named page ({msg}), please check "
                                "menu_json in configuration.").format(msg=e.args[0])
                    log.error(log_msg)
                    raise exceptions.ConfigError(log_msg)
            main_menu.append((page_name, url))
        self.main_menu = main_menu

    def _normalizeURL(self, url, lower=True):
        """Return URL normalized for self.redirections dict

        @param url(unicode): URL to normalize
        @param lower(bool): lower case of url if True
        @return (str): normalized URL
        """
        if lower:
            url = url.lower()
        return "/".join((p for p in url.split("/") if p))

    def _getRequestData(self, uri):
        """Return data needed to redirect request

        @param url(unicode): destination url
        @return (tuple(list[str], str, str, dict): tuple with
            splitted path as in Request.postpath
            uri as in Request.uri
            path as in Request.path
            args as in Request.args
        """
        uri = uri
        # XXX: we reuse code from twisted.web.http.py here
        #      as we need to have the same behaviour
        x = uri.split("?", 1)

        if len(x) == 1:
            path = uri
            args = {}
        else:
            path, argstring = x
            args = urllib.parse.parse_qs(argstring, True)

        # XXX: splitted path case must not be changed, as it may be significant
        #      (e.g. for blog items)
        return (
            self._normalizeURL(path, lower=False).split("/"),
            uri,
            path,
            args,
        )

    def _redirect(self, request, request_data):
        """Redirect an URL by rewritting request

        this is *NOT* a HTTP redirection, but equivalent to URL rewritting
        @param request(web.http.request): original request
        @param request_data(tuple): data returned by self._getRequestData
        @return (web_resource.Resource): resource to use
        """
        # recursion check
        try:
            request._redirected
        except AttributeError:
            pass
        else:
            try:
                __, uri, __, __ = request_data
            except ValueError:
                uri = ""
            log.error(D_( "recursive redirection, please fix this URL:\n"
                          "{old} ==> {new}").format(
                          old=request.uri.decode("utf-8"), new=uri))
            return web_resource.NoResource()

        request._redirected = True  # here to avoid recursive redirections

        if isinstance(request_data, dict):
            if request_data["type"] == "page":
                try:
                    page = self.getPageByName(request_data["page"])
                except KeyError:
                    log.error(
                        _(
                            'Can\'t find page named "{name}" requested in redirection'
                        ).format(name=request_data["page"])
                    )
                    return web_resource.NoResource()
                path_args = [pa.encode('utf-8') for pa in request_data["path_args"]]
                request.postpath = path_args + request.postpath

                try:
                    request.args.update(request_data["query_args"])
                except (TypeError, ValueError):
                    log.error(
                        _("Invalid args in redirection: {query_args}").format(
                            query_args=request_data["query_args"]
                        )
                    )
                    return web_resource.NoResource()
                return page
            else:
                raise exceptions.InternalError("unknown request_data type")
        else:
            path_list, uri, path, args = request_data
            path_list = [p.encode('utf-8') for p in path_list]
            log.debug(
                "Redirecting URL {old} to {new}".format(
                    old=request.uri.decode('utf-8'), new=uri
                )
            )
            # we change the request to reflect the new url
            request.postpath = path_list[1:] + request.postpath
            request.args.update(args)

        # we start again to look for a child with the new url
        return self.getChildWithDefault(path_list[0], request)

    def getPageByName(self, name):
        """Retrieve page instance from its name

        @param name(unicode): name of the page
        @return (LiberviaPage): page instance
        @raise KeyError: the page doesn't exist
        """
        return self.named_pages[name]

    def getPagePathFromURI(self, uri):
        """Retrieve page URL from xmpp: URI

        @param uri(unicode): URI with a xmpp: scheme
        @return (unicode,None): absolute path (starting from root "/") to page handling
            the URI.
            None is returned if no page has been registered for this URI
        """
        uri_data = common_uri.parseXMPPUri(uri)
        try:
            page, cb = self.uri_callbacks[uri_data["type"], uri_data["sub_type"]]
        except KeyError:
            url = None
        else:
            url = cb(page, uri_data)
        if url is None:
            # no handler found
            # we try to find a more generic one
            try:
                page, cb = self.uri_callbacks[uri_data["type"], None]
            except KeyError:
                pass
            else:
                url = cb(page, uri_data)
        return url

    def getChildWithDefault(self, name, request):
        # XXX: this method is overriden only for root url
        #      which is the only ones who need to be handled before other children
        if name == b"" and not request.postpath:
            return self._redirect(request, self.redirections[""])
        return super(LiberviaRootResource, self).getChildWithDefault(name, request)

    def getChild(self, name, request):
        resource = super(LiberviaRootResource, self).getChild(name, request)

        if isinstance(resource, web_resource.NoResource):
            # if nothing was found, we try our luck with redirections
            # XXX: we want redirections to happen only if everything else failed
            path_elt = request.prepath + request.postpath
            for idx in range(len(path_elt), -1, -1):
                test_url = b"/".join(path_elt[:idx]).decode('utf-8').lower()
                if test_url in self.redirections:
                    request_data = self.redirections[test_url]
                    request.postpath = path_elt[idx:]
                    return self._redirect(request, request_data)

        return resource

    def putChild(self, path, resource):
        """Add a child to the root resource"""
        if not isinstance(path, bytes):
            raise ValueError("path must be specified in bytes")
        if not isinstance(resource, web_resource.EncodingResourceWrapper):
            # FIXME: check that no information is leaked (c.f. https://twistedmatrix.com/documents/current/web/howto/using-twistedweb.html#request-encoders)
            resource = web_resource.EncodingResourceWrapper(
                resource, [server.GzipEncoderFactory()])

        super(LiberviaRootResource, self).putChild(path, resource)

    def createSimilarFile(self, path):
        # XXX: this method need to be overriden to avoid recreating a LiberviaRootResource

        f = LiberviaRootResource.__base__(
            path, self.defaultType, self.ignoredExts, self.registry
        )
        # refactoring by steps, here - constructor should almost certainly take these
        f.processors = self.processors
        f.indexNames = self.indexNames[:]
        f.childNotFound = self.childNotFound
        return f


class WaitingRequests(dict):
    def setRequest(self, request, profile, register_with_ext_jid=False):
        """Add the given profile to the waiting list.

        @param request (server.Request): the connection request
        @param profile (str): %(doc_profile)s
        @param register_with_ext_jid (bool): True if we will try to register the
            profile with an external XMPP account credentials
        """
        dc = reactor.callLater(BRIDGE_TIMEOUT, self.purgeRequest, profile)
        self[profile] = (request, dc, register_with_ext_jid)

    def purgeRequest(self, profile):
        """Remove the given profile from the waiting list.

        @param profile (str): %(doc_profile)s
        """
        try:
            dc = self[profile][1]
        except KeyError:
            return
        if dc.active():
            dc.cancel()
        del self[profile]

    def getRequest(self, profile):
        """Get the waiting request for the given profile.

        @param profile (str): %(doc_profile)s
        @return: the waiting request or None
        """
        return self[profile][0] if profile in self else None

    def getRegisterWithExtJid(self, profile):
        """Get the value of the register_with_ext_jid parameter.

        @param profile (str): %(doc_profile)s
        @return: bool or None
        """
        return self[profile][2] if profile in self else None


class Libervia(service.Service):
    debug = defer.Deferred.debug  # True if twistd/Libervia is launched in debug mode

    def __init__(self, options):
        self.options = options

    def _init(self):
        # we do init here and not in __init__ to avoid doule initialisation with twistd
        # this _init is called in startService
        self.initialised = defer.Deferred()
        self.waiting_profiles = WaitingRequests()  # FIXME: should be removed
        self._main_conf = None
        self.files_watcher = FilesWatcher(self)

        if self.options["base_url_ext"]:
            self.base_url_ext = self.options.pop("base_url_ext")
            if self.base_url_ext[-1] != "/":
                self.base_url_ext += "/"
            self.base_url_ext_data = urllib.parse.urlsplit(self.base_url_ext)
        else:
            self.base_url_ext = None
            # we split empty string anyway so we can do things like
            # scheme = self.base_url_ext_data.scheme or 'https'
            self.base_url_ext_data = urllib.parse.urlsplit("")

        if not self.options["port_https_ext"]:
            self.options["port_https_ext"] = self.options["port_https"]

        self._cleanup = []

        self.sessions = {}  # key = session value = user
        self.prof_connected = set()  # Profiles connected
        self.ns_map = {}  # map of short name to namespaces

        ## bridge ##
        self._bridge_retry = self.options['bridge-retries']
        self.bridge = Bridge()
        self.bridge.bridgeConnect(callback=self._bridgeCb, errback=self._bridgeEb)

    @property
    def roots(self):
        """Return available virtual host roots

        Root resources are only returned once, even if they are present for multiple
        named vhosts. Order is not relevant, except for default vhost which is always
        returned first.
        @return (list[web_resource.Resource]): all vhost root resources
        """
        roots = list(set(self.vhost_root.hosts.values()))
        default = self.vhost_root.default
        if default is not None and default not in roots:
            roots.insert(0, default)
        return roots

    @property
    def main_conf(self):
        """SafeConfigParser instance opened on configuration file (sat.conf)"""
        if self._main_conf is None:
            self._main_conf = config.parseMainConf(log_filenames=True)
        return self._main_conf

    def getConfig(self, site_root_res, key, default=None, value_type=None):
        """Retrieve configuration associated to a site

        Section is automatically set to site name
        @param site_root_res(LiberviaRootResource): resource of the site in use
        @param key(unicode): key to use
        @param default: value to use if not found (see [config.getConfig])
        @param value_type(unicode, None): filter to use on value
            Note that filters are already automatically used when the key finish
            by a well known suffix ("_path", "_list", "_dict", or "_json")
            None to use no filter, else can be:
                - "path": a path is expected, will be normalized and expanded

        """
        section = site_root_res.site_name.lower().strip() or C.CONFIG_SECTION
        value = config.getConfig(self.main_conf, section, key, default=default)
        if value_type is not None:
            if value_type == 'path':
                v_filter = lambda v: os.path.abspath(os.path.expanduser(v))
            else:
                raise ValueError("unknown value type {value_type}".format(
                    value_type = value_type))
            if isinstance(value, list):
                value = [v_filter(v) for v in value]
            elif isinstance(value, dict):
                value = {k:v_filter(v) for k,v in list(value.items())}
            elif value is not None:
                value = v_filter(value)
        return value

    def _namespacesGetCb(self, ns_map):
        self.ns_map = {str(k): str(v) for k,v in ns_map.items()}

    def _namespacesGetEb(self, failure_):
        log.error(_("Can't get namespaces map: {msg}").format(msg=failure_))

    @template.contextfilter
    def _front_url_filter(self, ctx, relative_url):
        template_data = ctx['template_data']
        return os.path.join(
            '/', C.TPL_RESOURCE, template_data.site or C.SITE_NAME_DEFAULT,
            C.TEMPLATE_TPL_DIR, template_data.theme, relative_url)

    def _moveFirstLevelToDict(self, options, key, keys_to_keep):
        """Read a config option and put value at first level into u'' dict

        This is useful to put values for Libervia official site directly in dictionary,
        and to use site_name as keys when external sites are used.
        options will be modified in place
        @param options(dict): options to modify
        @param key(unicode): setting key to modify
        @param keys_to_keep(list(unicode)): keys allowed in first level
        """
        try:
            conf = options[key]
        except KeyError:
            return
        if not isinstance(conf, dict):
            options[key] = {'': conf}
            return
        default_dict = conf.get('', {})
        to_delete = []
        for key, value in conf.items():
            if key not in keys_to_keep:
                default_dict[key] = value
                to_delete.append(key)
        for key in to_delete:
            del conf[key]
        if default_dict:
            conf[''] = default_dict

    async def checkAndConnectServiceProfile(self):
        passphrase = self.options["passphrase"]
        if not passphrase:
            raise SysExit(
                C.EXIT_BAD_ARG,
                _("No passphrase set for service profile, please check installation "
                  "documentation.")
            )
        try:
            s_prof_connected = await self.bridgeCall("isConnected", C.SERVICE_PROFILE)
        except BridgeException as e:
            if e.classname == "ProfileUnknownError":
                log.info("Service profile doesn't exist, creating it.")
                try:
                    xmpp_domain = await self.bridgeCall("getConfig", "", "xmpp_domain")
                    xmpp_domain = xmpp_domain.strip()
                    if not xmpp_domain:
                        raise SysExit(
                            C.EXIT_BAD_ARG,
                            _('"xmpp_domain" must be set to create new accounts, please '
                              'check documentation')
                        )
                    service_profile_jid_s = f"{C.SERVICE_PROFILE}@{xmpp_domain}"
                    await self.bridgeCall(
                        "inBandAccountNew",
                        service_profile_jid_s,
                        passphrase,
                        "",
                        xmpp_domain,
                        0,
                    )
                except BridgeException as e:
                    if e.condition == "conflict":
                        log.info(
                            _("Service's profile JID {profile_jid} already exists")
                            .format(profile_jid=service_profile_jid_s)
                        )
                    elif e.classname == "UnknownMethod":
                        raise SysExit(
                            C.EXIT_BRIDGE_ERROR,
                            _("Can't create service profile XMPP account, In-Band "
                              "Registration plugin is not activated, you'll have to "
                              "create the {profile!r} profile with {profile_jid!r} JID "
                              "manually.").format(
                                  profile=C.SERVICE_PROFILE,
                                  profile_jid=service_profile_jid_s)
                        )
                    elif e.condition == "service-unavailable":
                        raise SysExit(
                            C.EXIT_BRIDGE_ERROR,
                            _("Can't create service profile XMPP account, In-Band "
                              "Registration is not activated on your server, you'll have "
                              "to create the {profile!r} profile with {profile_jid!r} JID "
                              "manually.\nNote that you'll need to activate In-Band "
                              "Registation on your server if you want users to be able "
                              "to create new account from {app_name}, please check "
                              "documentation.").format(
                                  profile=C.SERVICE_PROFILE,
                                  profile_jid=service_profile_jid_s,
                                  app_name=C.APP_NAME)
                        )
                    elif e.condition == "not-acceptable":
                        raise SysExit(
                            C.EXIT_BRIDGE_ERROR,
                            _("Can't create service profile XMPP account, your XMPP "
                              "server doesn't allow us to create new accounts with "
                              "In-Band Registration please check XMPP server "
                              "configuration: {reason}"
                              ).format(
                                  profile=C.SERVICE_PROFILE,
                                  profile_jid=service_profile_jid_s,
                                  reason=e.message)
                        )

                    else:
                        raise SysExit(
                            C.EXIT_BRIDGE_ERROR,
                            _("Can't create service profile XMPP account, you'll have "
                              "do to it manually: {reason}").format(reason=e.message)
                        )
                try:
                    await self.bridgeCall("profileCreate", C.SERVICE_PROFILE, passphrase)
                    await self.bridgeCall(
                        "profileStartSession", passphrase, C.SERVICE_PROFILE)
                    await self.bridgeCall(
                        "setParam", "JabberID", service_profile_jid_s, "Connection", -1,
                        C.SERVICE_PROFILE)
                    await self.bridgeCall(
                        "setParam", "Password", passphrase, "Connection", -1,
                        C.SERVICE_PROFILE)
                except BridgeException as e:
                    raise SysExit(
                        C.EXIT_BRIDGE_ERROR,
                        _("Can't create service profile XMPP account, you'll have "
                          "do to it manually: {reason}").format(reason=e.message)
                    )
                log.info(_("Service profile has been successfully created"))
                s_prof_connected = False
            else:
                raise SysExit(C.EXIT_BRIDGE_ERROR, e.message)

        if not s_prof_connected:
            try:
                await self.bridgeCall(
                    "connect",
                    C.SERVICE_PROFILE,
                    passphrase,
                    {},
                )
            except BridgeException as e:
                raise SysExit(
                    C.EXIT_BRIDGE_ERROR,
                    _("Connection of service profile failed: {reason}").format(reason=e)
                )

    async def backendReady(self):
        log.info(f"Libervia Web v{self.full_version}")

        # settings
        if self.options['dev-mode']:
            log.info(_("Developer mode activated"))
        self.media_dir = await self.bridgeCall("getConfig", "", "media_dir")
        self.local_dir = await self.bridgeCall("getConfig", "", "local_dir")
        self.cache_root_dir = os.path.join(self.local_dir, C.CACHE_DIR)
        self.renderer = template.Renderer(self, self._front_url_filter)
        sites_names = list(self.renderer.sites_paths.keys())

        self._moveFirstLevelToDict(self.options, "url_redirections_dict", sites_names)
        self._moveFirstLevelToDict(self.options, "menu_json", sites_names)
        self._moveFirstLevelToDict(self.options, "menu_extra_json", sites_names)
        menu = self.options["menu_json"]
        if not '' in menu:
            menu[''] = C.DEFAULT_MENU
        for site, value in self.options["menu_extra_json"].items():
            menu[site].extend(value)

        # service profile
        if not self.options['build-only']:
            await self.checkAndConnectServiceProfile()

        # restricted bridge, the one used by browser code
        self.restricted_bridge = RestrictedBridge(self)

        # we create virtual hosts and import Libervia pages into them
        self.vhost_root = vhost.NameVirtualHost()
        default_site_path = Path(libervia.__file__).parent.resolve()
        # self.sat_root is official Libervia site
        root_path = default_site_path / C.TEMPLATE_STATIC_DIR
        self.sat_root = default_root = LiberviaRootResource(
            host=self, host_name='', site_name='',
            site_path=default_site_path, path=root_path)
        if self.options['dev-mode']:
            self.files_watcher.watchDir(
                default_site_path, auto_add=True, recursive=True,
                callback=LiberviaPage.onFileChange, site_root=self.sat_root,
                site_path=default_site_path)
        LiberviaPage.importPages(self, self.sat_root)
        tasks_manager = TasksManager(self, self.sat_root)
        await tasks_manager.parseTasks()
        await tasks_manager.runTasks()
        # FIXME: handle _setMenu in a more generic way, taking care of external sites
        await self.sat_root._setMenu(self.options["menu_json"])
        self.vhost_root.default = default_root
        existing_vhosts = {b'': default_root}

        for host_name, site_name in self.options["vhosts_dict"].items():
            if site_name == C.SITE_NAME_DEFAULT:
                raise ValueError(
                    f"{C.DEFAULT_SITE_NAME} is reserved and can't be used in vhosts_dict")
            encoded_site_name = site_name.encode('utf-8')
            try:
                site_path = self.renderer.sites_paths[site_name]
            except KeyError:
                log.warning(_(
                    "host {host_name} link to non existing site {site_name}, ignoring "
                    "it").format(host_name=host_name, site_name=site_name))
                continue
            if encoded_site_name in existing_vhosts:
                # we have an alias host, we re-use existing resource
                res = existing_vhosts[encoded_site_name]
            else:
                # for root path we first check if there is a global static dir
                # if not, we use default template's static dir
                root_path = os.path.join(site_path, C.TEMPLATE_STATIC_DIR)
                if not os.path.isdir(root_path):
                    root_path = os.path.join(
                        site_path, C.TEMPLATE_TPL_DIR, C.TEMPLATE_THEME_DEFAULT,
                        C.TEMPLATE_STATIC_DIR)
                res = LiberviaRootResource(
                    host=self,
                    host_name=host_name,
                    site_name=site_name,
                    site_path=site_path,
                    path=root_path)

                existing_vhosts[encoded_site_name] = res

                if self.options['dev-mode']:
                    self.files_watcher.watchDir(
                        site_path, auto_add=True, recursive=True,
                        callback=LiberviaPage.onFileChange, site_root=res,
                        site_path=site_path)

                LiberviaPage.importPages(self, res)
                # FIXME: default pages are accessible if not overriden by external website
                #        while necessary for login or re-using existing pages
                #        we may want to disable access to the page by direct URL
                #        (e.g. /blog disabled except if called by external site)
                LiberviaPage.importPages(self, res, root_path=default_site_path)
                tasks_manager = TasksManager(self, res)
                await tasks_manager.parseTasks()
                await tasks_manager.runTasks()
                await res._setMenu(self.options["menu_json"])

            self.vhost_root.addHost(host_name.encode('utf-8'), res)

        templates_res = web_resource.Resource()
        self.putChildAll(C.TPL_RESOURCE.encode('utf-8'), templates_res)
        for site_name, site_path in self.renderer.sites_paths.items():
            templates_res.putChild(site_name.encode() or C.SITE_NAME_DEFAULT.encode(),
                                   static.File(site_path))

        d = self.bridgeCall("namespacesGet")
        d.addCallback(self._namespacesGetCb)
        d.addErrback(self._namespacesGetEb)

        # websocket
        if self.options["connection_type"] in ("https", "both"):
            wss = websockets.LiberviaPageWSProtocol.getResource(self, secure=True)
            self.putChildAll(b'wss', wss)
        if self.options["connection_type"] in ("http", "both"):
            ws = websockets.LiberviaPageWSProtocol.getResource(self, secure=False)
            self.putChildAll(b'ws', ws)

        ## following signal is needed for cache handling in Libervia pages
        self.bridge.register_signal(
            "psEventRaw", partial(LiberviaPage.onNodeEvent, self), "plugin"
        )
        self.bridge.register_signal(
            "messageNew", partial(LiberviaPage.onSignal, self, "messageNew")
        )

        #  Progress handling
        self.bridge.register_signal(
            "progressStarted", partial(ProgressHandler._signal, "started")
        )
        self.bridge.register_signal(
            "progressFinished", partial(ProgressHandler._signal, "finished")
        )
        self.bridge.register_signal(
            "progressError", partial(ProgressHandler._signal, "error")
        )

        # media dirs
        # FIXME: get rid of dirname and "/" in C.XXX_DIR
        self.putChildAll(os.path.dirname(C.MEDIA_DIR).encode('utf-8'),
                         ProtectedFile(self.media_dir))

        self.cache_resource = web_resource.NoResource()
        self.putChildAll(C.CACHE_DIR.encode('utf-8'), self.cache_resource)
        self.cache_resource.putChild(
            b"common", ProtectedFile(str(self.cache_root_dir / Path("common"))))

        # redirections
        for root in self.roots:
            await root._initRedirections(self.options)

        # no need to keep url_redirections_dict, it will not be used anymore
        del self.options["url_redirections_dict"]

        server.Request.defaultContentType = "text/html; charset=utf-8"
        wrapped = web_resource.EncodingResourceWrapper(
            self.vhost_root, [server.GzipEncoderFactory()]
        )
        self.site = server.Site(wrapped)
        self.site.sessionFactory = LiberviaSession

    def _bridgeCb(self):
        del self._bridge_retry
        self.bridge.getReady(
            lambda: self.initialised.callback(None),
            lambda failure: self.initialised.errback(Exception(failure)),
        )
        self.initialised.addCallback(lambda __: defer.ensureDeferred(self.backendReady()))

    def _bridgeEb(self, failure_):
        if isinstance(failure_, BridgeExceptionNoService):
            if self._bridge_retry:
                if self._bridge_retry < 0:
                    print(_("Can't connect to bridge, will retry indefinitely. "
                            "Next try in 1s."))
                else:
                    self._bridge_retry -= 1
                    print(
                        _(
                            "Can't connect to bridge, will retry in 1 s ({retries_left} "
                            "trie(s) left)."
                        ).format(retries_left=self._bridge_retry)
                    )
                time.sleep(1)
                self.bridge.bridgeConnect(callback=self._bridgeCb, errback=self._bridgeEb)
                return

            print("Can't connect to SàT backend, are you sure it's launched ?")
        else:
            log.error("Can't connect to bridge: {}".format(failure))
        sys.exit(1)

    @property
    def version(self):
        """Return the short version of Libervia"""
        return C.APP_VERSION

    @property
    def full_version(self):
        """Return the full version of Libervia (with extra data when in dev mode)"""
        version = self.version
        if version[-1] == "D":
            # we are in debug version, we add extra data
            try:
                return self._version_cache
            except AttributeError:
                self._version_cache = "{} ({})".format(
                    version, utils.getRepositoryData(libervia)
                )
                return self._version_cache
        else:
            return version

    def bridgeCall(self, method_name, *args, **kwargs):
        """Call an asynchronous bridge method and return a deferred

        @param method_name: name of the method as a unicode
        @return: a deferred which trigger the result

        """
        d = defer.Deferred()

        def _callback(*args):
            if not args:
                d.callback(None)
            else:
                if len(args) != 1:
                    Exception("Multiple return arguments not supported")
                d.callback(args[0])

        def _errback(failure_):
            d.errback(failure.Failure(failure_))

        kwargs["callback"] = _callback
        kwargs["errback"] = _errback
        getattr(self.bridge, method_name)(*args, **kwargs)
        return d

    async def _logged(self, profile, request):
        """Set everything when a user just logged in

        @param profile
        @param request
        @return: a constant indicating the state:
            - C.PROFILE_LOGGED
            - C.PROFILE_LOGGED_EXT_JID
        @raise exceptions.ConflictError: session is already active
        """
        register_with_ext_jid = self.waiting_profiles.getRegisterWithExtJid(profile)
        self.waiting_profiles.purgeRequest(profile)
        session = request.getSession()
        sat_session = session_iface.ISATSession(session)
        if sat_session.profile:
            log.error(_("/!\\ Session has already a profile, this should NEVER happen!"))
            raise failure.Failure(exceptions.ConflictError("Already active"))

        # XXX: we force string because python D-Bus has its own string type (dbus.String)
        #   which may cause trouble when exposing it to scripts
        sat_session.profile = str(profile)
        self.prof_connected.add(profile)
        cache_dir = os.path.join(
            self.cache_root_dir, "profiles", regex.pathEscape(profile)
        )
        # FIXME: would be better to have a global /cache URL which redirect to
        #        profile's cache directory, without uuid
        self.cache_resource.putChild(sat_session.uuid.encode('utf-8'),
                                     ProtectedFile(cache_dir))
        log.debug(
            _("profile cache resource added from {uuid} to {path}").format(
                uuid=sat_session.uuid, path=cache_dir
            )
        )

        def onExpire():
            log.info("Session expired (profile={profile})".format(profile=profile))
            self.cache_resource.delEntity(sat_session.uuid.encode('utf-8'))
            log.debug(
                _("profile cache resource {uuid} deleted").format(uuid=sat_session.uuid)
            )
            # and now we disconnect the profile
            self.bridgeCall("disconnect", profile)

        session.notifyOnExpire(onExpire)

        # FIXME: those session infos should be returned by connect or isConnected
        infos = await self.bridgeCall("sessionInfosGet", profile)
        sat_session.jid = jid.JID(infos["jid"])
        own_bare_jid_s = sat_session.jid.userhost()
        own_id_raw = await self.bridgeCall(
            "identityGet", own_bare_jid_s, [], True, profile)
        sat_session.identities[own_bare_jid_s] = data_format.deserialise(own_id_raw)
        sat_session.backend_started = int(infos["started"])

        state = C.PROFILE_LOGGED_EXT_JID if register_with_ext_jid else C.PROFILE_LOGGED
        return state

    @defer.inlineCallbacks
    def connect(self, request, login, password):
        """log user in

        If an other user was already logged, it will be unlogged first
        @param request(server.Request): request linked to the session
        @param login(unicode): user login
            can be profile name
            can be profile@[libervia_domain.ext]
            can be a jid (a new profile will be created with this jid if needed)
        @param password(unicode): user password
        @return (unicode, None): C.SESSION_ACTIVE: if session was aleady active else
            self._logged value
        @raise exceptions.DataError: invalid login
        @raise exceptions.ProfileUnknownError: this login doesn't exist
        @raise exceptions.PermissionError: a login is not accepted (e.g. empty password
            not allowed)
        @raise exceptions.NotReady: a profile connection is already waiting
        @raise exceptions.TimeoutError: didn't received and answer from Bridge
        @raise exceptions.InternalError: unknown error
        @raise ValueError(C.PROFILE_AUTH_ERROR): invalid login and/or password
        @raise ValueError(C.XMPP_AUTH_ERROR): invalid XMPP account password
        """

        # XXX: all security checks must be done here, even if present in javascript
        if login.startswith("@"):
            raise failure.Failure(exceptions.DataError("No profile_key allowed"))

        if login.startswith("guest@@") and login.count("@") == 2:
            log.debug("logging a guest account")
        elif "@" in login:
            if login.count("@") != 1:
                raise failure.Failure(
                    exceptions.DataError("Invalid login: {login}".format(login=login))
                )
            try:
                login_jid = jid.JID(login)
            except (RuntimeError, jid.InvalidFormat, AttributeError):
                raise failure.Failure(exceptions.DataError("No profile_key allowed"))

            # FIXME: should it be cached?
            new_account_domain = yield self.bridgeCall("getNewAccountDomain")

            if login_jid.host == new_account_domain:
                # redirect "user@libervia.org" to the "user" profile
                login = login_jid.user
                login_jid = None
        else:
            login_jid = None

        try:
            profile = yield self.bridgeCall("profileNameGet", login)
        except Exception:  # XXX: ProfileUnknownError wouldn't work, it's encapsulated
            # FIXME: find a better way to handle bridge errors
            if (
                login_jid is not None and login_jid.user
            ):  # try to create a new sat profile using the XMPP credentials
                if not self.options["allow_registration"]:
                    log.warning(
                        "Trying to register JID account while registration is not "
                        "allowed")
                    raise failure.Failure(
                        exceptions.DataError(
                            "JID login while registration is not allowed"
                        )
                    )
                profile = login  # FIXME: what if there is a resource?
                connect_method = "asyncConnectWithXMPPCredentials"
                register_with_ext_jid = True
            else:  # non existing username
                raise failure.Failure(exceptions.ProfileUnknownError())
        else:
            if profile != login or (
                not password
                and profile
                not in self.options["empty_password_allowed_warning_dangerous_list"]
            ):
                # profiles with empty passwords are restricted to local frontends
                raise exceptions.PermissionError
            register_with_ext_jid = False

            connect_method = "connect"

        # we check if there is not already an active session
        sat_session = session_iface.ISATSession(request.getSession())
        if sat_session.profile:
            # yes, there is
            if sat_session.profile != profile:
                # it's a different profile, we need to disconnect it
                log.warning(_(
                    "{new_profile} requested login, but {old_profile} was already "
                    "connected, disconnecting {old_profile}").format(
                        old_profile=sat_session.profile, new_profile=profile))
                self.purgeSession(request)

        if self.waiting_profiles.getRequest(profile):
            #  FIXME: check if and when this can happen
            raise failure.Failure(exceptions.NotReady("Already waiting"))

        self.waiting_profiles.setRequest(request, profile, register_with_ext_jid)
        try:
            connected = yield self.bridgeCall(connect_method, profile, password)
        except Exception as failure_:
            fault = getattr(failure_, 'classname', None)
            self.waiting_profiles.purgeRequest(profile)
            if fault in ("PasswordError", "ProfileUnknownError"):
                log.info("Profile {profile} doesn't exist or the submitted password is "
                         "wrong".format( profile=profile))
                raise failure.Failure(ValueError(C.PROFILE_AUTH_ERROR))
            elif fault == "SASLAuthError":
                log.info("The XMPP password of profile {profile} is wrong"
                    .format(profile=profile))
                raise failure.Failure(ValueError(C.XMPP_AUTH_ERROR))
            elif fault == "NoReply":
                log.info(_("Did not receive a reply (the timeout expired or the "
                           "connection is broken)"))
                raise exceptions.TimeOutError
            elif fault is None:
                log.info(_("Unexepected failure: {failure_}").format(failure_=failure))
                raise failure_
            else:
                log.error('Unmanaged fault class "{fault}" in errback for the '
                          'connection of profile {profile}'.format(
                              fault=fault, profile=profile))
                raise failure.Failure(exceptions.InternalError(fault))

        if connected:
            #  profile is already connected in backend
            # do we have a corresponding session in Libervia?
            sat_session = session_iface.ISATSession(request.getSession())
            if sat_session.profile:
                # yes, session is active
                if sat_session.profile != profile:
                    # existing session should have been ended above
                    # so this line should never be reached
                    log.error(_(
                        "session profile [{session_profile}] differs from login "
                        "profile [{profile}], this should not happen!")
                            .format(session_profile=sat_session.profile, profile=profile))
                    raise exceptions.InternalError("profile mismatch")
                defer.returnValue(C.SESSION_ACTIVE)
            log.info(
                _(
                    "profile {profile} was already connected in backend".format(
                        profile=profile
                    )
                )
            )
            #  no, we have to create it

        state = yield defer.ensureDeferred(self._logged(profile, request))
        defer.returnValue(state)

    def registerNewAccount(self, request, login, password, email):
        """Create a new account, or return error
        @param request(server.Request): request linked to the session
        @param login(unicode): new account requested login
        @param email(unicode): new account email
        @param password(unicode): new account password
        @return(unicode): a constant indicating the state:
            - C.BAD_REQUEST: something is wrong in the request (bad arguments)
            - C.INVALID_INPUT: one of the data is not valid
            - C.REGISTRATION_SUCCEED: new account has been successfully registered
            - C.ALREADY_EXISTS: the given profile already exists
            - C.INTERNAL_ERROR or any unmanaged fault string
        @raise PermissionError: registration is now allowed in server configuration
        """
        if not self.options["allow_registration"]:
            log.warning(
                _("Registration received while it is not allowed, hack attempt?")
            )
            raise failure.Failure(
                exceptions.PermissionError("Registration is not allowed on this server")
            )

        if (
            not re.match(C.REG_LOGIN_RE, login)
            or not re.match(C.REG_EMAIL_RE, email, re.IGNORECASE)
            or len(password) < C.PASSWORD_MIN_LENGTH
        ):
            return C.INVALID_INPUT

        def registered(result):
            return C.REGISTRATION_SUCCEED

        def registeringError(failure_):
            # FIXME: better error handling for bridge error is needed
            status = failure_.value.fullname.split('.')[-1]
            if status == "ConflictError":
                return C.ALREADY_EXISTS
            elif status == "InvalidCertificate":
                return C.INVALID_CERTIFICATE
            elif status == "InternalError":
                return C.INTERNAL_ERROR
            else:
                log.error(
                    _("Unknown registering error status: {status}\n{traceback}").format(
                        status=status, traceback=failure_.value.message
                    )
                )
                return status

        d = self.bridgeCall("registerSatAccount", email, password, login)
        d.addCallback(registered)
        d.addErrback(registeringError)
        return d

    def addCleanup(self, callback, *args, **kwargs):
        """Add cleaning method to call when service is stopped

        cleaning method will be called in reverse order of they insertion
        @param callback: callable to call on service stop
        @param *args: list of arguments of the callback
        @param **kwargs: list of keyword arguments of the callback"""
        self._cleanup.insert(0, (callback, args, kwargs))

    def initEb(self, failure):
        from twisted.application import app
        if failure.check(SysExit):
            if failure.value.message:
                log.error(failure.value.message)
            app._exitCode = failure.value.exit_code
            reactor.stop()
        else:
            log.error(_("Init error: {msg}").format(msg=failure))
            app._exitCode = C.EXIT_INTERNAL_ERROR
            reactor.stop()
            return failure

    def _buildOnlyCb(self, __):
        log.info(_("Stopping here due to --build-only flag"))
        self.stop()

    def startService(self):
        """Connect the profile for Libervia and start the HTTP(S) server(s)"""
        self._init()
        if self.options['build-only']:
            self.initialised.addCallback(self._buildOnlyCb)
        else:
            self.initialised.addCallback(self._startService)
        self.initialised.addErrback(self.initEb)

    ## URLs ##

    def putChildSAT(self, path, resource):
        """Add a child to the sat resource"""
        if not isinstance(path, bytes):
            raise ValueError("path must be specified in bytes")
        self.sat_root.putChild(path, resource)

    def putChildAll(self, path, resource):
        """Add a child to all vhost root resources"""
        if not isinstance(path, bytes):
            raise ValueError("path must be specified in bytes")
        # we wrap before calling putChild, to avoid having useless multiple instances
        # of the resource
        # FIXME: check that no information is leaked (c.f. https://twistedmatrix.com/documents/current/web/howto/using-twistedweb.html#request-encoders)
        wrapped_res = web_resource.EncodingResourceWrapper(
            resource, [server.GzipEncoderFactory()])
        for root in self.roots:
            root.putChild(path, wrapped_res)

    def getBuildPath(self, site_name: str, dev: bool=False) -> Path:
        """Generate build path for a given site name

        @param site_name: name of the site
        @param dev: return dev build dir if True, production one otherwise
            dev build dir is used for installing dependencies needed temporarily (e.g.
            to compile files), while production build path is the one served by the
            HTTP server, where final files are downloaded.
        @return: path to the build directory
        """
        sub_dir = C.DEV_BUILD_DIR if dev else C.PRODUCTION_BUILD_DIR
        build_path_elts = [
            config.getConfig(self.main_conf, "", "local_dir"),
            C.CACHE_DIR,
            C.LIBERVIA_CACHE,
            sub_dir,
            regex.pathEscape(site_name or C.SITE_NAME_DEFAULT)]
        build_path = Path("/".join(build_path_elts))
        return build_path.expanduser().resolve()

    def getExtBaseURLData(self, request):
        """Retrieve external base URL Data

        this method try to retrieve the base URL found by external user
        It does by checking in this order:
            - base_url_ext option from configuration
            - proxy x-forwarder-host headers
            - URL of the request
        @return (urlparse.SplitResult): SplitResult instance with only scheme and
            netloc filled
        """
        ext_data = self.base_url_ext_data
        url_path = request.URLPath()

        try:
            forwarded = request.requestHeaders.getRawHeaders(
                "forwarded"
            )[0]
        except TypeError:
            # we try deprecated headers
            try:
                proxy_netloc = request.requestHeaders.getRawHeaders(
                    "x-forwarded-host"
                )[0]
            except TypeError:
                proxy_netloc = None
            try:
                proxy_scheme = request.requestHeaders.getRawHeaders(
                    "x-forwarded-proto"
                )[0]
            except TypeError:
                proxy_scheme = None
        else:
            fwd_data = {
                k.strip(): v.strip()
                for k,v in (d.split("=") for d in forwarded.split(";"))
            }
            proxy_netloc = fwd_data.get("host")
            proxy_scheme = fwd_data.get("proto")

        return urllib.parse.SplitResult(
            ext_data.scheme or proxy_scheme or url_path.scheme.decode(),
            ext_data.netloc or proxy_netloc or url_path.netloc.decode(),
            ext_data.path or "/",
            "",
            "",
        )

    def getExtBaseURL(
            self,
            request: server.Request,
            path: str = "",
            query: str = "",
            fragment: str = "",
            scheme: Optional[str] = None,
            ) -> str:
        """Get external URL according to given elements

        external URL is the URL seen by external user
        @param path: same as for urlsplit.urlsplit
            path will be prefixed to follow found external URL if suitable
        @param params: same as for urlsplit.urlsplit
        @param query: same as for urlsplit.urlsplit
        @param fragment: same as for urlsplit.urlsplit
        @param scheme: if not None, will override scheme from base URL
        @return: external URL
        """
        split_result = self.getExtBaseURLData(request)
        return urllib.parse.urlunsplit(
            (
                split_result.scheme if scheme is None else scheme,
                split_result.netloc,
                os.path.join(split_result.path, path),
                query,
                fragment,
            )
        )

    def checkRedirection(self, vhost_root: LiberviaRootResource, url_path: str) -> str:
        """check is a part of the URL prefix is redirected then replace it

        @param vhost_root: root of this virtual host
        @param url_path: path of the url to check
        @return: possibly redirected URL which should link to the same location
        """
        inv_redirections = vhost_root.inv_redirections
        url_parts = url_path.strip("/").split("/")
        for idx in range(len(url_parts), -1, -1):
            test_url = "/" + "/".join(url_parts[:idx])
            if test_url in inv_redirections:
                rem_url = url_parts[idx:]
                return os.path.join(
                    "/", "/".join([inv_redirections[test_url]] + rem_url)
                )
        return url_path

    ## Sessions ##

    def purgeSession(self, request):
        """helper method to purge a session during request handling"""
        session = request.session
        if session is not None:
            log.debug(_("session purge"))
            session.expire()
            # FIXME: not clean but it seems that it's the best way to reset
            #        session during request handling
            request._secureSession = request._insecureSession = None

    def getSessionData(self, request, *args):
        """helper method to retrieve session data

        @param request(server.Request): request linked to the session
        @param *args(zope.interface.Interface): interface of the session to get
        @return (iterator(data)): requested session data
        """
        session = request.getSession()
        if len(args) == 1:
            return args[0](session)
        else:
            return (iface(session) for iface in args)

    @defer.inlineCallbacks
    def getAffiliation(self, request, service, node):
        """retrieve pubsub node affiliation for current user

        use cache first, and request pubsub service if not cache is found
        @param request(server.Request): request linked to the session
        @param service(jid.JID): pubsub service
        @param node(unicode): pubsub node
        @return (unicode): affiliation
        """
        sat_session = self.getSessionData(request, session_iface.ISATSession)
        if sat_session.profile is None:
            raise exceptions.InternalError("profile must be set to use this method")
        affiliation = sat_session.getAffiliation(service, node)
        if affiliation is not None:
            defer.returnValue(affiliation)
        else:
            try:
                affiliations = yield self.bridgeCall(
                    "psAffiliationsGet", service.full(), node, sat_session.profile
                )
            except Exception as e:
                log.warning(
                    "Can't retrieve affiliation for {service}/{node}: {reason}".format(
                        service=service, node=node, reason=e
                    )
                )
                affiliation = ""
            else:
                try:
                    affiliation = affiliations[node]
                except KeyError:
                    affiliation = ""
            sat_session.setAffiliation(service, node, affiliation)
            defer.returnValue(affiliation)

    ## Websocket (dynamic pages) ##

    def getWebsocketURL(self, request):
        base_url_split = self.getExtBaseURLData(request)
        if base_url_split.scheme.endswith("s"):
            scheme = "wss"
        else:
            scheme = "ws"

        return self.getExtBaseURL(request, path=scheme, scheme=scheme)

    def registerWSToken(self, token, page, request):
        # we make a shallow copy of request to avoid losing request.channel when
        # connection is lost (which would result as request.isSecure() being always
        # False). See #327
        request._signal_id = id(request)
        websockets.LiberviaPageWSProtocol.registerToken(token, page, copy.copy(request))

    ## Various utils ##

    def getHTTPDate(self, timestamp=None):
        now = time.gmtime(timestamp)
        fmt_date = "{day_name}, %d {month_name} %Y %H:%M:%S GMT".format(
            day_name=C.HTTP_DAYS[now.tm_wday], month_name=C.HTTP_MONTH[now.tm_mon - 1]
        )
        return time.strftime(fmt_date, now)

    ## service management ##

    def _startService(self, __=None):
        """Actually start the HTTP(S) server(s) after the profile for Libervia is connected.

        @raise ImportError: OpenSSL is not available
        @raise IOError: the certificate file doesn't exist
        @raise OpenSSL.crypto.Error: the certificate file is invalid
        """
        # now that we have service profile connected, we add resource for its cache
        service_path = regex.pathEscape(C.SERVICE_PROFILE)
        cache_dir = os.path.join(self.cache_root_dir, "profiles", service_path)
        self.cache_resource.putChild(service_path.encode('utf-8'),
                                     ProtectedFile(cache_dir))
        self.service_cache_url = "/" + os.path.join(C.CACHE_DIR, service_path)
        session_iface.SATSession.service_cache_url = self.service_cache_url

        if self.options["connection_type"] in ("https", "both"):
            try:
                tls.TLSOptionsCheck(self.options)
                context_factory = tls.getTLSContextFactory(self.options)
            except exceptions.ConfigError as e:
                log.warning(
                    f"There is a problem in TLS settings in your configuration file: {e}")
                self.quit(2)
            except exceptions.DataError as e:
                log.warning(
                    f"Can't set TLS: {e}")
                self.quit(1)
            reactor.listenSSL(self.options["port_https"], self.site, context_factory)
        if self.options["connection_type"] in ("http", "both"):
            if (
                self.options["connection_type"] == "both"
                and self.options["redirect_to_https"]
            ):
                reactor.listenTCP(
                    self.options["port"],
                    server.Site(
                        RedirectToHTTPS(
                            self.options["port"], self.options["port_https_ext"]
                        )
                    ),
                )
            else:
                reactor.listenTCP(self.options["port"], self.site)

    @defer.inlineCallbacks
    def stopService(self):
        log.info(_("launching cleaning methods"))
        for callback, args, kwargs in self._cleanup:
            callback(*args, **kwargs)
        try:
            yield self.bridgeCall("disconnect", C.SERVICE_PROFILE)
        except Exception:
            log.warning("Can't disconnect service profile")

    def run(self):
        reactor.run()

    def stop(self):
        reactor.stop()

    def quit(self, exit_code=None):
        """Exit app when reactor is running

        @param exit_code(None, int): exit code
        """
        self.stop()
        sys.exit(exit_code or 0)


class RedirectToHTTPS(web_resource.Resource):
    def __init__(self, old_port, new_port):
        web_resource.Resource.__init__(self)
        self.isLeaf = True
        self.old_port = old_port
        self.new_port = new_port

    def render(self, request):
        netloc = request.URLPath().netloc.decode().replace(
            f":{self.old_port}", f":{self.new_port}"
        )
        url = f"https://{netloc}{request.uri.decode()}"
        return web_util.redirectTo(url.encode(), request)


registerAdapter(session_iface.SATSession, server.Session, session_iface.ISATSession)
registerAdapter(
    session_iface.SATGuestSession, server.Session, session_iface.ISATGuestSession
)
