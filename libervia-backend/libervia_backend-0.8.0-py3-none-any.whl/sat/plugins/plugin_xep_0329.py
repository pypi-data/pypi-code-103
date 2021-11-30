#!/usr/bin/env python3

# SAT plugin for File Information Sharing (XEP-0329)
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

import mimetypes
import json
import os
from pathlib import Path
from typing import Optional, Dict
from zope.interface import implementer
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jabber_error
from twisted.internet import defer
from wokkel import disco, iwokkel, data_form
from sat.core.i18n import _
from sat.core.xmpp import SatXMPPEntity
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.tools import stream
from sat.tools.common import regex


log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "File Information Sharing",
    C.PI_IMPORT_NAME: "XEP-0329",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0329"],
    C.PI_DEPENDENCIES: ["XEP-0231", "XEP-0234", "XEP-0300", "XEP-0106"],
    C.PI_MAIN: "XEP_0329",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of File Information Sharing"""),
}

NS_FIS = "urn:xmpp:fis:0"
NS_FIS_AFFILIATION = "org.salut-a-toi.fis-affiliation"
NS_FIS_CONFIGURATION = "org.salut-a-toi.fis-configuration"
NS_FIS_CREATE = "org.salut-a-toi.fis-create"

IQ_FIS_REQUEST = f'{C.IQ_GET}/query[@xmlns="{NS_FIS}"]'
# not in the standard, but needed, and it's handy to keep it here
IQ_FIS_AFFILIATION_GET = f'{C.IQ_GET}/affiliations[@xmlns="{NS_FIS_AFFILIATION}"]'
IQ_FIS_AFFILIATION_SET = f'{C.IQ_SET}/affiliations[@xmlns="{NS_FIS_AFFILIATION}"]'
IQ_FIS_CONFIGURATION_GET = f'{C.IQ_GET}/configuration[@xmlns="{NS_FIS_CONFIGURATION}"]'
IQ_FIS_CONFIGURATION_SET = f'{C.IQ_SET}/configuration[@xmlns="{NS_FIS_CONFIGURATION}"]'
IQ_FIS_CREATE_DIR = f'{C.IQ_SET}/dir[@xmlns="{NS_FIS_CREATE}"]'
SINGLE_FILES_DIR = "files"
TYPE_VIRTUAL = "virtual"
TYPE_PATH = "path"
SHARE_TYPES = (TYPE_PATH, TYPE_VIRTUAL)
KEY_TYPE = "type"


class RootPathException(Exception):
    """Root path is requested"""


class ShareNode(object):
    """Node containing directory or files to share, virtual or real"""

    host = None

    def __init__(self, name, parent, type_, access, path=None):
        assert type_ in SHARE_TYPES
        if name is not None:
            if name == ".." or "/" in name or "\\" in name:
                log.warning(
                    _("path change chars found in name [{name}], hack attempt?").format(
                        name=name
                    )
                )
                if name == "..":
                    name = "--"
                else:
                    name = regex.pathEscape(name)
        self.name = name
        self.children = {}
        self.type = type_
        self.access = {} if access is None else access
        assert isinstance(self.access, dict)
        self.parent = None
        if parent is not None:
            assert name
            parent.addChild(self)
        else:
            assert name is None
        if path is not None:
            if type_ != TYPE_PATH:
                raise exceptions.InternalError(_("path can only be set on path nodes"))
            self._path = path

    @property
    def path(self):
        return self._path

    def __getitem__(self, key):
        return self.children[key]

    def __contains__(self, item):
        return self.children.__contains__(item)

    def __iter__(self):
        return self.children.__iter__()

    def items(self):
        return self.children.items()

    def values(self):
        return self.children.values()

    def getOrCreate(self, name, type_=TYPE_VIRTUAL, access=None):
        """Get a node or create a virtual node and return it"""
        if access is None:
            access = {C.ACCESS_PERM_READ: {KEY_TYPE: C.ACCESS_TYPE_PUBLIC}}
        try:
            return self.children[name]
        except KeyError:
            node = ShareNode(name, self, type_=type_, access=access)
            return node

    def addChild(self, node):
        if node.parent is not None:
            raise exceptions.ConflictError(_("a node can't have several parents"))
        node.parent = self
        self.children[node.name] = node

    def removeFromParent(self):
        try:
            del self.parent.children[self.name]
        except TypeError:
            raise exceptions.InternalError(
                "trying to remove a node from inexisting parent"
            )
        except KeyError:
            raise exceptions.InternalError("node not found in parent's children")
        self.parent = None

    def _checkNodePermission(self, client, node, perms, peer_jid):
        """Check access to this node for peer_jid

        @param node(SharedNode): node to check access
        @param perms(unicode): permissions to check, iterable of C.ACCESS_PERM_*
        @param peer_jid(jid.JID): entity which try to access the node
        @return (bool): True if entity can access
        """
        file_data = {"access": self.access, "owner": client.jid.userhostJID()}
        try:
            self.host.memory.checkFilePermission(file_data, peer_jid, perms)
        except exceptions.PermissionError:
            return False
        else:
            return True

    def checkPermissions(
        self, client, peer_jid, perms=(C.ACCESS_PERM_READ,), check_parents=True
    ):
        """Check that peer_jid can access this node and all its parents

        @param peer_jid(jid.JID): entrity trying to access the node
        @param perms(unicode): permissions to check, iterable of C.ACCESS_PERM_*
        @param check_parents(bool): if True, access of all parents of this node will be
            checked too
        @return (bool): True if entity can access this node
        """
        peer_jid = peer_jid.userhostJID()
        if peer_jid == client.jid.userhostJID():
            return True

        parent = self
        while parent != None:
            if not self._checkNodePermission(client, parent, perms, peer_jid):
                return False
            parent = parent.parent

        return True

    @staticmethod
    def find(client, path, peer_jid, perms=(C.ACCESS_PERM_READ,)):
        """find node corresponding to a path

        @param path(unicode): path to the requested file or directory
        @param peer_jid(jid.JID): entity trying to find the node
            used to check permission
        @return (dict, unicode): shared data, remaining path
        @raise exceptions.PermissionError: user can't access this file
        @raise exceptions.DataError: path is invalid
        @raise NotFound: path lead to a non existing file/directory
        """
        path_elts = [_f for _f in path.split("/") if _f]

        if ".." in path_elts:
            log.warning(_(
                'parent dir ("..") found in path, hack attempt? path is {path} '
                '[{profile}]').format(path=path, profile=client.profile))
            raise exceptions.PermissionError("illegal path elements")

        node = client._XEP_0329_root_node

        while path_elts:
            if node.type == TYPE_VIRTUAL:
                try:
                    node = node[path_elts.pop(0)]
                except KeyError:
                    raise exceptions.NotFound
            elif node.type == TYPE_PATH:
                break

        if not node.checkPermissions(client, peer_jid, perms=perms):
            raise exceptions.PermissionError("permission denied")

        return node, "/".join(path_elts)

    def findByLocalPath(self, path):
        """retrieve nodes linking to local path

        @return (list[ShareNode]): found nodes associated to path
        @raise exceptions.NotFound: no node has been found with this path
        """
        shared_paths = self.getSharedPaths()
        try:
            return shared_paths[path]
        except KeyError:
            raise exceptions.NotFound

    def _getSharedPaths(self, node, paths):
        if node.type == TYPE_VIRTUAL:
            for node in node.values():
                self._getSharedPaths(node, paths)
        elif node.type == TYPE_PATH:
            paths.setdefault(node.path, []).append(node)
        else:
            raise exceptions.InternalError(
                "unknown node type: {type}".format(type=node.type)
            )

    def getSharedPaths(self):
        """retrieve nodes by shared path

        this method will retrieve recursively shared path in children of this node
        @return (dict): map from shared path to list of nodes
        """
        if self.type == TYPE_PATH:
            raise exceptions.InternalError(
                "getSharedPaths must be used on a virtual node"
            )
        paths = {}
        self._getSharedPaths(self, paths)
        return paths


class XEP_0329(object):
    def __init__(self, host):
        log.info(_("File Information Sharing initialization"))
        self.host = host
        ShareNode.host = host
        self._b = host.plugins["XEP-0231"]
        self._h = host.plugins["XEP-0300"]
        self._jf = host.plugins["XEP-0234"]
        host.bridge.addMethod(
            "FISList",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="aa{ss}",
            method=self._listFiles,
            async_=True,
        )
        host.bridge.addMethod(
            "FISLocalSharesGet",
            ".plugin",
            in_sign="s",
            out_sign="as",
            method=self._localSharesGet,
        )
        host.bridge.addMethod(
            "FISSharePath",
            ".plugin",
            in_sign="ssss",
            out_sign="s",
            method=self._sharePath,
        )
        host.bridge.addMethod(
            "FISUnsharePath",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._unsharePath,
        )
        host.bridge.addMethod(
            "FISAffiliationsGet",
            ".plugin",
            in_sign="ssss",
            out_sign="a{ss}",
            method=self._affiliationsGet,
            async_=True,
        )
        host.bridge.addMethod(
            "FISAffiliationsSet",
            ".plugin",
            in_sign="sssa{ss}s",
            out_sign="",
            method=self._affiliationsSet,
            async_=True,
        )
        host.bridge.addMethod(
            "FISConfigurationGet",
            ".plugin",
            in_sign="ssss",
            out_sign="a{ss}",
            method=self._configurationGet,
            async_=True,
        )
        host.bridge.addMethod(
            "FISConfigurationSet",
            ".plugin",
            in_sign="sssa{ss}s",
            out_sign="",
            method=self._configurationSet,
            async_=True,
        )
        host.bridge.addMethod(
            "FISCreateDir",
            ".plugin",
            in_sign="sssa{ss}s",
            out_sign="",
            method=self._createDir,
            async_=True,
        )
        host.bridge.addSignal("FISSharedPathNew", ".plugin", signature="sss")
        host.bridge.addSignal("FISSharedPathRemoved", ".plugin", signature="ss")
        host.trigger.add("XEP-0234_fileSendingRequest", self._fileSendingRequestTrigger)
        host.registerNamespace("fis", NS_FIS)

    def getHandler(self, client):
        return XEP_0329_handler(self)

    def profileConnected(self, client):
        if client.is_component:
            client._file_sharing_allowed_hosts = self.host.memory.getConfig(
                'component file_sharing',
                'http_upload_allowed_hosts_list') or [client.host]
        else:
            client._XEP_0329_root_node = ShareNode(
                None,
                None,
                TYPE_VIRTUAL,
                {C.ACCESS_PERM_READ: {KEY_TYPE: C.ACCESS_TYPE_PUBLIC}},
            )
            client._XEP_0329_names_data = {}  #  name to share map

    def _fileSendingRequestTrigger(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        """This trigger check that a requested file is available, and fill suitable data

        Path and name are used to retrieve the file. If path is missing, we try our luck
        with known names
        """
        if client.is_component:
            return True, None

        try:
            name = file_data["name"]
        except KeyError:
            return True, None
        assert "/" not in name

        path = file_data.get("path")
        if path is not None:
            # we have a path, we can follow it to find node
            try:
                node, rem_path = ShareNode.find(client, path, session["peer_jid"])
            except (exceptions.PermissionError, exceptions.NotFound):
                #  no file, or file not allowed, we continue normal workflow
                return True, None
            except exceptions.DataError:
                log.warning(_("invalid path: {path}").format(path=path))
                return True, None

            if node.type == TYPE_VIRTUAL:
                # we have a virtual node, so name must link to a path node
                try:
                    path = node[name].path
                except KeyError:
                    return True, None
            elif node.type == TYPE_PATH:
                # we have a path node, so we can retrieve the full path now
                path = os.path.join(node.path, rem_path, name)
            else:
                raise exceptions.InternalError(
                    "unknown type: {type}".format(type=node.type)
                )
            if not os.path.exists(path):
                return True, None
            size = os.path.getsize(path)
        else:
            # we don't have the path, we try to find the file by its name
            try:
                name_data = client._XEP_0329_names_data[name]
            except KeyError:
                return True, None

            for path, shared_file in name_data.items():
                if True:  #  FIXME: filters are here
                    break
            else:
                return True, None
            parent_node = shared_file["parent"]
            if not parent_node.checkPermissions(client, session["peer_jid"]):
                log.warning(
                    _(
                        "{peer_jid} requested a file (s)he can't access [{profile}]"
                    ).format(peer_jid=session["peer_jid"], profile=client.profile)
                )
                return True, None
            size = shared_file["size"]

        file_data["size"] = size
        file_elt.addElement("size", content=str(size))
        hash_algo = file_data["hash_algo"] = self._h.getDefaultAlgo()
        hasher = file_data["hash_hasher"] = self._h.getHasher(hash_algo)
        file_elt.addChild(self._h.buildHashUsedElt(hash_algo))
        content_data["stream_object"] = stream.FileStreamObject(
            self.host,
            client,
            path,
            uid=self._jf.getProgressId(session, content_name),
            size=size,
            data_cb=lambda data: hasher.update(data),
        )
        return False, defer.succeed(True)

    # common methods

    def _requestHandler(self, client, iq_elt, root_nodes_cb, files_from_node_cb):
        iq_elt.handled = True
        node = iq_elt.query.getAttribute("node")
        if not node:
            d = defer.maybeDeferred(root_nodes_cb, client, iq_elt)
        else:
            d = defer.maybeDeferred(files_from_node_cb, client, iq_elt, node)
        d.addErrback(
            lambda failure_: log.error(
                _("error while retrieving files: {msg}").format(msg=failure_)
            )
        )

    def _iqError(self, client, iq_elt, condition="item-not-found"):
        error_elt = jabber_error.StanzaError(condition).toResponse(iq_elt)
        client.send(error_elt)

    #  client

    def _addPathData(self, client, query_elt, path, parent_node):
        """Fill query_elt with files/directories found in path"""
        name = os.path.basename(path)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            mime_type = mimetypes.guess_type(path, strict=False)[0]
            file_elt = self._jf.buildFileElement(
                client=client, name=name, size=size, mime_type=mime_type,
                modified=os.path.getmtime(path)
            )

            query_elt.addChild(file_elt)
            # we don't specify hash as it would be too resource intensive to calculate
            # it for all files.
            # we add file to name_data, so users can request it later
            name_data = client._XEP_0329_names_data.setdefault(name, {})
            if path not in name_data:
                name_data[path] = {
                    "size": size,
                    "mime_type": mime_type,
                    "parent": parent_node,
                }
        else:
            # we have a directory
            directory_elt = query_elt.addElement("directory")
            directory_elt["name"] = name

    def _pathNodeHandler(self, client, iq_elt, query_elt, node, path):
        """Fill query_elt for path nodes, i.e. physical directories"""
        path = os.path.join(node.path, path)

        if not os.path.exists(path):
            # path may have been moved since it has been shared
            return self._iqError(client, iq_elt)
        elif os.path.isfile(path):
            self._addPathData(client, query_elt, path, node)
        else:
            for name in sorted(os.listdir(path.encode("utf-8")), key=lambda n: n.lower()):
                try:
                    name = name.decode("utf-8", "strict")
                except UnicodeDecodeError as e:
                    log.warning(
                        _("ignoring invalid unicode name ({name}): {msg}").format(
                            name=name.decode("utf-8", "replace"), msg=e
                        )
                    )
                    continue
                full_path = os.path.join(path, name)
                self._addPathData(client, query_elt, full_path, node)

    def _virtualNodeHandler(self, client, peer_jid, iq_elt, query_elt, node):
        """Fill query_elt for virtual nodes"""
        for name, child_node in node.items():
            if not child_node.checkPermissions(client, peer_jid, check_parents=False):
                continue
            node_type = child_node.type
            if node_type == TYPE_VIRTUAL:
                directory_elt = query_elt.addElement("directory")
                directory_elt["name"] = name
            elif node_type == TYPE_PATH:
                self._addPathData(client, query_elt, child_node.path, child_node)
            else:
                raise exceptions.InternalError(
                    _("unexpected type: {type}").format(type=node_type)
                )

    def _getRootNodesCb(self, client, iq_elt):
        peer_jid = jid.JID(iq_elt["from"])
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        for name, node in client._XEP_0329_root_node.items():
            if not node.checkPermissions(client, peer_jid, check_parents=False):
                continue
            directory_elt = query_elt.addElement("directory")
            directory_elt["name"] = name
        client.send(iq_result_elt)

    def _getFilesFromNodeCb(self, client, iq_elt, node_path):
        """Main method to retrieve files/directories from a node_path"""
        peer_jid = jid.JID(iq_elt["from"])
        try:
            node, path = ShareNode.find(client, node_path, peer_jid)
        except (exceptions.PermissionError, exceptions.NotFound):
            return self._iqError(client, iq_elt)
        except exceptions.DataError:
            return self._iqError(client, iq_elt, condition="not-acceptable")

        node_type = node.type
        peer_jid = jid.JID(iq_elt["from"])
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        query_elt["node"] = node_path

        # we now fill query_elt according to node_type
        if node_type == TYPE_PATH:
            #  it's a physical path
            self._pathNodeHandler(client, iq_elt, query_elt, node, path)
        elif node_type == TYPE_VIRTUAL:
            assert not path
            self._virtualNodeHandler(client, peer_jid, iq_elt, query_elt, node)
        else:
            raise exceptions.InternalError(
                _("unknown node type: {type}").format(type=node_type)
            )

        client.send(iq_result_elt)

    def onRequest(self, iq_elt, client):
        return self._requestHandler(
            client, iq_elt, self._getRootNodesCb, self._getFilesFromNodeCb
        )

    # Component

    def _compParseJids(self, client, iq_elt):
        """Retrieve peer_jid and owner to use from IQ stanza

        @param iq_elt(domish.Element): IQ stanza of the FIS request
        @return (tuple[jid.JID, jid.JID]): peer_jid and owner
        """

    @defer.inlineCallbacks
    def _compGetRootNodesCb(self, client, iq_elt):
        peer_jid, owner = client.getOwnerAndPeer(iq_elt)
        files_data = yield self.host.memory.getFiles(
            client,
            peer_jid=peer_jid,
            parent="",
            type_=C.FILE_TYPE_DIRECTORY,
            owner=owner,
        )
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        for file_data in files_data:
            name = file_data["name"]
            directory_elt = query_elt.addElement("directory")
            directory_elt["name"] = name
        client.send(iq_result_elt)

    @defer.inlineCallbacks
    def _compGetFilesFromNodeCb(self, client, iq_elt, node_path):
        """Retrieve files from local files repository according to permissions

        result stanza is then built and sent to requestor
        @trigger XEP-0329_compGetFilesFromNode(client, iq_elt, owner, node_path,
                                               files_data):
            can be used to add data/elements
        """
        peer_jid, owner = client.getOwnerAndPeer(iq_elt)
        try:
            files_data = yield self.host.memory.getFiles(
                client, peer_jid=peer_jid, path=node_path, owner=owner
            )
        except exceptions.NotFound:
            self._iqError(client, iq_elt)
            return
        except exceptions.PermissionError:
            self._iqError(client, iq_elt, condition='not-allowed')
            return
        except Exception as e:
            log.error("internal server error: {e}".format(e=e))
            self._iqError(client, iq_elt, condition='internal-server-error')
            return
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        query_elt["node"] = node_path
        if not self.host.trigger.point(
            "XEP-0329_compGetFilesFromNode",
            client,
            iq_elt,
            iq_result_elt,
            owner,
            node_path,
            files_data
        ):
            return
        for file_data in files_data:
            if file_data['type'] == C.FILE_TYPE_DIRECTORY:
                directory_elt = query_elt.addElement("directory")
                directory_elt['name'] = file_data['name']
                self.host.trigger.point(
                    "XEP-0329_compGetFilesFromNode_build_directory",
                    client,
                    file_data,
                    directory_elt,
                    owner,
                    node_path,
                )
            else:
                file_elt = self._jf.buildFileElementFromDict(
                    client,
                    file_data,
                    modified=file_data.get("modified", file_data["created"])
                )
                query_elt.addChild(file_elt)
        client.send(iq_result_elt)

    def onComponentRequest(self, iq_elt, client):
        return self._requestHandler(
            client, iq_elt, self._compGetRootNodesCb, self._compGetFilesFromNodeCb
        )

    async def _parseResult(self, client, peer_jid, iq_elt):
        query_elt = next(iq_elt.elements(NS_FIS, "query"))
        files = []

        for elt in query_elt.elements():
            if elt.name == "file":
                # we have a file
                try:
                    file_data = await self._jf.parseFileElement(client, elt)
                except exceptions.DataError:
                    continue
                file_data["type"] = C.FILE_TYPE_FILE
                try:
                    thumbs = file_data['extra'][C.KEY_THUMBNAILS]
                except KeyError:
                    log.debug(f"No thumbnail found for {file_data}")
                else:
                    for thumb in thumbs:
                        if 'url' not in thumb and "id" in thumb:
                            try:
                                file_path = await self._b.getFile(client, peer_jid, thumb['id'])
                            except Exception as e:
                                log.warning(f"Can't get thumbnail {thumb['id']!r} for {file_data}: {e}")
                            else:
                                thumb['filename'] = file_path.name

            elif elt.name == "directory" and elt.uri == NS_FIS:
                # we have a directory

                file_data = {"name": elt["name"], "type": C.FILE_TYPE_DIRECTORY}
                self.host.trigger.point(
                    "XEP-0329_parseResult_directory",
                    client,
                    elt,
                    file_data,
                )
            else:
                log.warning(
                    _("unexpected element, ignoring: {elt}")
                    .format(elt=elt.toXml())
                )
                continue
            files.append(file_data)
        return files

    # affiliations #

    async def _parseElement(self, client, iq_elt, element, namespace):
        peer_jid, owner = client.getOwnerAndPeer(iq_elt)
        elt = next(iq_elt.elements(namespace, element))
        path = Path("/", elt['path'])
        if len(path.parts) < 2:
            raise RootPathException
        namespace = elt.getAttribute('namespace')
        files_data = await self.host.memory.getFiles(
            client,
            peer_jid=peer_jid,
            path=str(path.parent),
            name=path.name,
            namespace=namespace,
            owner=owner,
        )
        if len(files_data) != 1:
            client.sendError(iq_elt, 'item-not-found')
            raise exceptions.CancelError
        file_data = files_data[0]
        return peer_jid, elt, path, namespace, file_data

    def _affiliationsGet(self, service_jid_s, namespace, path, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service_jid_s)
        d = defer.ensureDeferred(self.affiliationsGet(
            client, service, namespace or None, path))
        d.addCallback(
            lambda affiliations: {
                str(entity): affiliation for entity, affiliation in affiliations.items()
            }
        )
        return d

    async def affiliationsGet(
        self,
        client: SatXMPPEntity,
        service: jid.JID,
        namespace: Optional[str],
        path: str
    ) -> Dict[jid.JID, str]:
        if not path:
            raise ValueError(f"invalid path: {path!r}")
        iq_elt = client.IQ("get")
        iq_elt['to'] = service.full()
        affiliations_elt = iq_elt.addElement((NS_FIS_AFFILIATION, "affiliations"))
        if namespace:
            affiliations_elt["namespace"] = namespace
        affiliations_elt["path"] = path
        iq_result_elt = await iq_elt.send()
        try:
            affiliations_elt = next(iq_result_elt.elements(NS_FIS_AFFILIATION, "affiliations"))
        except StopIteration:
            raise exceptions.DataError(f"Invalid result to affiliations request: {iq_result_elt.toXml()}")

        affiliations = {}
        for affiliation_elt in affiliations_elt.elements(NS_FIS_AFFILIATION, 'affiliation'):
            try:
                affiliations[jid.JID(affiliation_elt['jid'])] = affiliation_elt['affiliation']
            except (KeyError, RuntimeError):
                raise exceptions.DataError(
                    f"invalid affiliation element: {affiliation_elt.toXml()}")

        return affiliations

    def _affiliationsSet(self, service_jid_s, namespace, path, affiliations, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service_jid_s)
        affiliations = {jid.JID(e): a for e, a in affiliations.items()}
        return defer.ensureDeferred(self.affiliationsSet(
            client, service, namespace or None, path, affiliations))

    async def affiliationsSet(
        self,
        client: SatXMPPEntity,
        service: jid.JID,
        namespace: Optional[str],
        path: str,
        affiliations: Dict[jid.JID, str],
    ):
        if not path:
            raise ValueError(f"invalid path: {path!r}")
        iq_elt = client.IQ("set")
        iq_elt['to'] = service.full()
        affiliations_elt = iq_elt.addElement((NS_FIS_AFFILIATION, "affiliations"))
        if namespace:
            affiliations_elt["namespace"] = namespace
        affiliations_elt["path"] = path
        for entity_jid, affiliation in affiliations.items():
            affiliation_elt = affiliations_elt.addElement('affiliation')
            affiliation_elt['jid'] = entity_jid.full()
            affiliation_elt['affiliation'] = affiliation
        await iq_elt.send()

    def _onComponentAffiliationsGet(self, iq_elt, client):
        iq_elt.handled = True
        defer.ensureDeferred(self.onComponentAffiliationsGet(client, iq_elt))

    async def onComponentAffiliationsGet(self, client, iq_elt):
        try:
            (
                from_jid, affiliations_elt, path, namespace, file_data
            ) = await self._parseElement(client, iq_elt, "affiliations", NS_FIS_AFFILIATION)
        except exceptions.CancelError:
            return
        except RootPathException:
            # if root path is requested, we only get owner affiliation
            peer_jid, owner = client.getOwnerAndPeer(iq_elt)
            is_owner = peer_jid.userhostJID() == owner
            affiliations = {owner: 'owner'}
        except exceptions.NotFound:
            client.sendError(iq_elt, "item-not-found")
            return
        except Exception as e:
            client.sendError(iq_elt, "internal-server-error", str(e))
            return
        else:
            from_jid_bare = from_jid.userhostJID()
            is_owner = from_jid_bare == file_data.get('owner')
            affiliations = self.host.memory.getFileAffiliations(file_data)
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        affiliations_elt = iq_result_elt.addElement((NS_FIS_AFFILIATION, 'affiliations'))
        for entity_jid, affiliation in affiliations.items():
            if not is_owner and entity_jid.userhostJID() != from_jid_bare:
                # only onwer can get all affiliations
                continue
            affiliation_elt = affiliations_elt.addElement('affiliation')
            affiliation_elt['jid'] = entity_jid.userhost()
            affiliation_elt['affiliation'] = affiliation
        client.send(iq_result_elt)

    def _onComponentAffiliationsSet(self, iq_elt, client):
        iq_elt.handled = True
        defer.ensureDeferred(self.onComponentAffiliationsSet(client, iq_elt))

    async def onComponentAffiliationsSet(self, client, iq_elt):
        try:
            (
                from_jid, affiliations_elt, path, namespace, file_data
            ) = await self._parseElement(client, iq_elt, "affiliations", NS_FIS_AFFILIATION)
        except exceptions.CancelError:
            return
        except RootPathException:
            client.sendError(iq_elt, 'bad-request', "Root path can't be used")
            return

        if from_jid.userhostJID() != file_data['owner']:
            log.warning(
                f"{from_jid} tried to modify {path} affiliations while the owner is "
                f"{file_data['owner']}"
            )
            client.sendError(iq_elt, 'forbidden')
            return

        try:
            affiliations = {
                jid.JID(e['jid']): e['affiliation']
                for e in affiliations_elt.elements(NS_FIS_AFFILIATION, 'affiliation')
            }
        except (KeyError, RuntimeError):
                log.warning(
                    f"invalid affiliation element: {affiliations_elt.toXml()}"
                )
                client.sendError(iq_elt, 'bad-request', "invalid affiliation element")
                return
        except Exception as e:
                log.error(
                    f"unexepected exception while setting affiliation element: {e}\n"
                    f"{affiliations_elt.toXml()}"
                )
                client.sendError(iq_elt, 'internal-server-error', f"{e}")
                return

        await self.host.memory.setFileAffiliations(client, file_data, affiliations)

        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        client.send(iq_result_elt)

    # configuration

    def _configurationGet(self, service_jid_s, namespace, path, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service_jid_s)
        d = defer.ensureDeferred(self.configurationGet(
            client, service, namespace or None, path))
        d.addCallback(
            lambda configuration: {
                str(entity): affiliation for entity, affiliation in configuration.items()
            }
        )
        return d

    async def configurationGet(
        self,
        client: SatXMPPEntity,
        service: jid.JID,
        namespace: Optional[str],
        path: str
    ) -> Dict[str, str]:
        if not path:
            raise ValueError(f"invalid path: {path!r}")
        iq_elt = client.IQ("get")
        iq_elt['to'] = service.full()
        configuration_elt = iq_elt.addElement((NS_FIS_CONFIGURATION, "configuration"))
        if namespace:
            configuration_elt["namespace"] = namespace
        configuration_elt["path"] = path
        iq_result_elt = await iq_elt.send()
        try:
            configuration_elt = next(iq_result_elt.elements(NS_FIS_CONFIGURATION, "configuration"))
        except StopIteration:
            raise exceptions.DataError(f"Invalid result to configuration request: {iq_result_elt.toXml()}")

        form = data_form.findForm(configuration_elt, NS_FIS_CONFIGURATION)
        configuration = {f.var: f.value for f in form.fields.values()}

        return configuration

    def _configurationSet(self, service_jid_s, namespace, path, configuration, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service_jid_s)
        return defer.ensureDeferred(self.configurationSet(
            client, service, namespace or None, path, configuration))

    async def configurationSet(
        self,
        client: SatXMPPEntity,
        service: jid.JID,
        namespace: Optional[str],
        path: str,
        configuration: Dict[str, str],
    ):
        if not path:
            raise ValueError(f"invalid path: {path!r}")
        iq_elt = client.IQ("set")
        iq_elt['to'] = service.full()
        configuration_elt = iq_elt.addElement((NS_FIS_CONFIGURATION, "configuration"))
        if namespace:
            configuration_elt["namespace"] = namespace
        configuration_elt["path"] = path
        form = data_form.Form(formType="submit", formNamespace=NS_FIS_CONFIGURATION)
        form.makeFields(configuration)
        configuration_elt.addChild(form.toElement())
        await iq_elt.send()

    def _onComponentConfigurationGet(self, iq_elt, client):
        iq_elt.handled = True
        defer.ensureDeferred(self.onComponentConfigurationGet(client, iq_elt))

    async def onComponentConfigurationGet(self, client, iq_elt):
        try:
            (
                from_jid, configuration_elt, path, namespace, file_data
            ) = await self._parseElement(client, iq_elt, "configuration", NS_FIS_CONFIGURATION)
        except exceptions.CancelError:
            return
        except RootPathException:
            client.sendError(iq_elt, 'bad-request', "Root path can't be used")
            return
        try:
            access_type = file_data['access'][C.ACCESS_PERM_READ]['type']
        except KeyError:
            access_model = 'whitelist'
        else:
            access_model = 'open' if access_type == C.ACCESS_TYPE_PUBLIC else 'whitelist'

        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        configuration_elt = iq_result_elt.addElement((NS_FIS_CONFIGURATION, 'configuration'))
        form = data_form.Form(formType="form", formNamespace=NS_FIS_CONFIGURATION)
        form.makeFields({'access_model': access_model})
        configuration_elt.addChild(form.toElement())
        client.send(iq_result_elt)

    async def _setConfiguration(self, client, configuration_elt, file_data):
        form = data_form.findForm(configuration_elt, NS_FIS_CONFIGURATION)
        for name, value in form.items():
            if name == 'access_model':
                await self.host.memory.setFileAccessModel(client, file_data, value)
            else:
                # TODO: send a IQ error?
                log.warning(
                    f"Trying to set a not implemented configuration option: {name}")

    def _onComponentConfigurationSet(self, iq_elt, client):
        iq_elt.handled = True
        defer.ensureDeferred(self.onComponentConfigurationSet(client, iq_elt))

    async def onComponentConfigurationSet(self, client, iq_elt):
        try:
            (
                from_jid, configuration_elt, path, namespace, file_data
            ) = await self._parseElement(client, iq_elt, "configuration", NS_FIS_CONFIGURATION)
        except exceptions.CancelError:
            return
        except RootPathException:
            client.sendError(iq_elt, 'bad-request', "Root path can't be used")
            return

        from_jid_bare = from_jid.userhostJID()
        is_owner = from_jid_bare == file_data.get('owner')
        if not is_owner:
            log.warning(
                f"{from_jid} tried to modify {path} configuration while the owner is "
                f"{file_data['owner']}"
            )
            client.sendError(iq_elt, 'forbidden')
            return

        await self._setConfiguration(client, configuration_elt, file_data)

        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        client.send(iq_result_elt)

    # directory creation

    def _createDir(self, service_jid_s, namespace, path, configuration, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service_jid_s)
        return defer.ensureDeferred(self.createDir(
            client, service, namespace or None, path, configuration or None))

    async def createDir(
        self,
        client: SatXMPPEntity,
        service: jid.JID,
        namespace: Optional[str],
        path: str,
        configuration: Optional[Dict[str, str]],
    ):
        if not path:
            raise ValueError(f"invalid path: {path!r}")
        iq_elt = client.IQ("set")
        iq_elt['to'] = service.full()
        create_dir_elt = iq_elt.addElement((NS_FIS_CREATE, "dir"))
        if namespace:
            create_dir_elt["namespace"] = namespace
        create_dir_elt["path"] = path
        if configuration:
            configuration_elt = create_dir_elt.addElement((NS_FIS_CONFIGURATION, "configuration"))
            form = data_form.Form(formType="submit", formNamespace=NS_FIS_CONFIGURATION)
            form.makeFields(configuration)
            configuration_elt.addChild(form.toElement())
        await iq_elt.send()

    def _onComponentCreateDir(self, iq_elt, client):
        iq_elt.handled = True
        defer.ensureDeferred(self.onComponentCreateDir(client, iq_elt))

    async def onComponentCreateDir(self, client, iq_elt):
        peer_jid, owner = client.getOwnerAndPeer(iq_elt)
        if peer_jid.host not in client._file_sharing_allowed_hosts:
            client.sendError(iq_elt, 'forbidden')
            return
        create_dir_elt = next(iq_elt.elements(NS_FIS_CREATE, "dir"))
        namespace = create_dir_elt.getAttribute('namespace')
        path = Path("/", create_dir_elt['path'])
        if len(path.parts) < 2:
            client.sendError(iq_elt, 'bad-request', "Root path can't be used")
            return
        # for root directories, we check permission here
        if len(path.parts) == 2 and owner != peer_jid.userhostJID():
            log.warning(
                f"{peer_jid} is trying to create a dir at {owner}'s repository:\n"
                f"path: {path}\nnamespace: {namespace!r}"
            )
            client.sendError(iq_elt, 'forbidden', "You can't create a directory there")
            return
        # when going further into the path, the permissions will be checked by getFiles
        files_data = await self.host.memory.getFiles(
            client,
            peer_jid=peer_jid,
            path=path.parent,
            namespace=namespace,
            owner=owner,
        )
        if path.name in [d['name'] for d in files_data]:
            log.warning(
                f"Conflict when trying to create a directory (from: {peer_jid} "
                f"namespace: {namespace!r} path: {path!r})"
            )
            client.sendError(
                iq_elt, 'conflict', "there is already a file or dir at this path")
            return

        try:
            configuration_elt = next(
                create_dir_elt.elements(NS_FIS_CONFIGURATION, 'configuration'))
        except StopIteration:
            configuration_elt = None

        await self.host.memory.setFile(
            client,
            path.name,
            path=path.parent,
            type_=C.FILE_TYPE_DIRECTORY,
            namespace=namespace,
            owner=owner,
            peer_jid=peer_jid
        )

        if configuration_elt is not None:
            file_data = (await self.host.memory.getFiles(
                client,
                peer_jid=peer_jid,
                path=path.parent,
                name=path.name,
                namespace=namespace,
                owner=owner,
            ))[0]

            await self._setConfiguration(client, configuration_elt, file_data)

        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        client.send(iq_result_elt)

    # file methods #

    def _serializeData(self, files_data):
        for file_data in files_data:
            for key, value in file_data.items():
                file_data[key] = (
                    json.dumps(value) if key in ("extra",) else str(value)
                )
        return files_data

    def _listFiles(self, target_jid, path, extra, profile):
        client = self.host.getClient(profile)
        target_jid = client.jid if not target_jid else jid.JID(target_jid)
        d = defer.ensureDeferred(self.listFiles(client, target_jid, path or None))
        d.addCallback(self._serializeData)
        return d

    async def listFiles(self, client, peer_jid, path=None, extra=None):
        """List file shared by an entity

        @param peer_jid(jid.JID): jid of the sharing entity
        @param path(unicode, None): path to the directory containing shared files
            None to get root directories
        @param extra(dict, None): extra data
        @return list(dict): shared files
        """
        iq_elt = client.IQ("get")
        iq_elt["to"] = peer_jid.full()
        query_elt = iq_elt.addElement((NS_FIS, "query"))
        if path:
            query_elt["node"] = path
        iq_result_elt = await iq_elt.send()
        return await self._parseResult(client, peer_jid, iq_result_elt)

    def _localSharesGet(self, profile):
        client = self.host.getClient(profile)
        return self.localSharesGet(client)

    def localSharesGet(self, client):
        return list(client._XEP_0329_root_node.getSharedPaths().keys())

    def _sharePath(self, name, path, access, profile):
        client = self.host.getClient(profile)
        access = json.loads(access)
        return self.sharePath(client, name or None, path, access)

    def sharePath(self, client, name, path, access):
        if client.is_component:
            raise exceptions.ClientTypeError
        if not os.path.exists(path):
            raise ValueError(_("This path doesn't exist!"))
        if not path or not path.strip(" /"):
            raise ValueError(_("A path need to be specified"))
        if not isinstance(access, dict):
            raise ValueError(_("access must be a dict"))

        node = client._XEP_0329_root_node
        node_type = TYPE_PATH
        if os.path.isfile(path):
            # we have a single file, the workflow is diferrent as we store all single
            # files in the same dir
            node = node.getOrCreate(SINGLE_FILES_DIR)

        if not name:
            name = os.path.basename(path.rstrip(" /"))
            if not name:
                raise exceptions.InternalError(_("Can't find a proper name"))

        if name in node or name == SINGLE_FILES_DIR:
            idx = 1
            new_name = name + "_" + str(idx)
            while new_name in node:
                idx += 1
                new_name = name + "_" + str(idx)
            name = new_name
            log.info(_(
                "A directory with this name is already shared, renamed to {new_name} "
                "[{profile}]".format( new_name=new_name, profile=client.profile)))

        ShareNode(name=name, parent=node, type_=node_type, access=access, path=path)
        self.host.bridge.FISSharedPathNew(path, name, client.profile)
        return name

    def _unsharePath(self, path, profile):
        client = self.host.getClient(profile)
        return self.unsharePath(client, path)

    def unsharePath(self, client, path):
        nodes = client._XEP_0329_root_node.findByLocalPath(path)
        for node in nodes:
            node.removeFromParent()
        self.host.bridge.FISSharedPathRemoved(path, client.profile)


@implementer(iwokkel.IDisco)
class XEP_0329_handler(xmlstream.XMPPHandler):

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        if self.parent.is_component:
            self.xmlstream.addObserver(
                IQ_FIS_REQUEST, self.plugin_parent.onComponentRequest, client=self.parent
            )
            self.xmlstream.addObserver(
                IQ_FIS_AFFILIATION_GET,
                self.plugin_parent._onComponentAffiliationsGet,
                client=self.parent
            )
            self.xmlstream.addObserver(
                IQ_FIS_AFFILIATION_SET,
                self.plugin_parent._onComponentAffiliationsSet,
                client=self.parent
            )
            self.xmlstream.addObserver(
                IQ_FIS_CONFIGURATION_GET,
                self.plugin_parent._onComponentConfigurationGet,
                client=self.parent
            )
            self.xmlstream.addObserver(
                IQ_FIS_CONFIGURATION_SET,
                self.plugin_parent._onComponentConfigurationSet,
                client=self.parent
            )
            self.xmlstream.addObserver(
                IQ_FIS_CREATE_DIR,
                self.plugin_parent._onComponentCreateDir,
                client=self.parent
            )
        else:
            self.xmlstream.addObserver(
                IQ_FIS_REQUEST, self.plugin_parent.onRequest, client=self.parent
            )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_FIS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
