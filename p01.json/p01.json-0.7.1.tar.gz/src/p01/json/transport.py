##############################################################################
#
# Copyright (c) 2015 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import string
import urllib
import urlparse
import httplib
import base64
import types

import p01.json.exceptions

import p01.json.api


###############################################################################
#
# response parser

def getparser(jsonReader):
    un = Unmarshaller(jsonReader)
    par = Parser(un)
    return par,un


class Unmarshaller(object):

    def __init__(self, jsonReader):
        self.jsonReader = jsonReader
        self.data = None

    def feed(self, data):
        if self.data is None:
            self.data = data
        else:
            self.data = self.data + data

    def close(self):
        # convert to json, reader raises ResponseError on read error
        try:
            return self.jsonReader(self.data)
        except ValueError, e:
            raise p01.json.exceptions.ResponseError(e)


class Parser(object):
    def __init__(self, unmarshaller):
        self._target = unmarshaller
        self.data = None

    def feed(self, data):
        if self.data is None:
            self.data = data
        else:
            self.data = self.data + data

    def close(self):
        self._target.feed(self.data)


###############################################################################
#
# transport implementations

class Transport(object):
    """Handles an HTTP transaction to an JSON-RPC server.

    Standard transport class for JSON-RPC over HTTP.
    You can create custom transports by subclassing this method, and
    overriding selected methods.

    Send a complete request, and parse the response.

    """

    user_agent = "p01.json/0.5.0"
    contentType = "application/json-rpc"

    def __init__(self, contentType="application/json-rpc", jsonReader=None,
        verbose=0):
        if contentType is not None:
            self.contentType = contentType
        if jsonReader is None:
            jsonReader = p01.json.api.jsonReader
        self.jsonReader = jsonReader
        if verbose is None:
            verbose = 0
        self.verbose = verbose

    def request(self, host, handler, request_body, verbose=0):
        # issue JSON-RPC request
        verbose = verbose or self.verbose
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)
        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise p01.json.exceptions.ProtocolError(host + handler, errcode,
                errmsg, headers)

        self.verbose = verbose

        self.parse_response_headers(headers)

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        return self._parse_response(h.getfile(), sock)

    def getparser(self):
        """Get parser and unmarshaller."""
        return getparser(self.jsonReader)

    def get_host_info(self, host):
        """Get authorization info from host parameter

        Host may be a string, or a (host, x509-dict) tuple; if a string,
        it is checked for a "user:pw@host" format, and a "Basic
        Authentication" header is added if appropriate.

        @param host Host descriptor (URL or (URL, x509 info) tuple).
        @return A 3-tuple containing (actual host, extra headers,
        x509 info).  The header and x509 fields may be None.

        """
        x509 = {}
        if isinstance(host, types.TupleType):
            host, x509 = host

        auth, host = urllib.splituser(host)

        if auth:
            auth = base64.encodestring(urllib.unquote(auth))
            auth = string.join(string.split(auth), "") # get rid of whitespace
            extra_headers = [
                ("Authorization", "Basic " + auth)
                ]
        else:
            extra_headers = None

        return host, extra_headers, x509

    def make_connection(self, host):
        # create a HTTP connection object from a host descriptor
        host, extra_headers, x509 = self.get_host_info(host)
        return httplib.HTTP(host)

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", handler)

    def send_host(self, connection, host):
        host, extra_headers, x509 = self.get_host_info(host)
        connection.putheader("Host", host)
        if extra_headers:
            if isinstance(extra_headers, dict):
                extra_headers = extra_headers.items()
            for key, value in extra_headers:
                connection.putheader(key, value)

    def send_user_agent(self, connection):
        connection.putheader("User-Agent", self.user_agent)

    def send_content(self, connection, request_body):
        connection.putheader("Content-Type", self.contentType)
        connection.putheader("Content-Length", str(len(request_body)))
        connection.endheaders()
        if request_body:
            connection.send(request_body)

    def parse_response_headers(self, headers):
        pass

    def parse_response(self, file):
        # compatibility interface
        return self._parse_response(file, None)

    def _parse_response(self, file, sock):
        # read response from input file/socket, and parse it

        p, u = self.getparser()

        while 1:
            if sock:
                response = sock.recv(1024)
            else:
                response = file.read(1024)
            if not response:
                break
            if self.verbose:
                print "body:", repr(response)
            p.feed(response)

        file.close()
        p.close()

        return u.close()


class SecureTransportMixin(object):
    """Handles an HTTPS transaction to an JSON-RPC server."""

    def make_connection(self, host):
        """Create a HTTPS connection object from a host descriptor

        host may be a string, or a (host, x509-dict) tuple

        """
        host, extra_headers, x509 = self.get_host_info(host)
        try:
            HTTPS = httplib.HTTPS
        except AttributeError:
            raise NotImplementedError(
                "your version of httplib doesn't support HTTPS"
                )
        else:
            return HTTPS(host, None, **(x509 or {}))


class SecureTransport(SecureTransportMixin, Transport):
    """Handles an HTTPS transaction to an JSON-RPC server."""


class BasicAuthTransport(Transport):
    """Handles a transaction to an JSON-RPC server using HTTP basic auth."""

    def __init__(self, username=None, password=None, bearer=None,
        contentType="application/json-rpc", jsonReader=None, verbose=0):
        super(BasicAuthTransport, self).__init__(contentType=contentType,
            jsonReader=jsonReader, verbose=verbose)
        self.username=username
        self.password=password
        self.bearer = bearer

    def send_content(self, connection, request_body):
        # send basic auth
        if self.username is not None and self.password is not None:
            connection.putheader("AUTHORIZATION", "Basic %s" %
                base64.encodestring("%s:%s" % (self.username, self.password)
                    ).replace("\012", ""))
        elif self.bearer is not None:
            connection.putheader("Authorization: Bearer %s\n" % self.bearer)

        super(BasicAuthTransport, self).send_content(connection, request_body)


class SecureBasicAuthTransport(SecureTransportMixin, BasicAuthTransport):
    """Basic AUTH through HTTPS"""


# BBB
SafeTransportMixin = SecureTransportMixin
SafeTransport = SecureTransport
SafeBasicAuthTransport = SecureBasicAuthTransport


###############################################################################
#
# transport setup api

def getTransport(uri, username=None, password=None,
    contentType="application/json-rpc", jsonReader=None, verbose=0):
    """Returns the right transport for given uri and optional username, password

    Note: if no username and password is given we will check the uri for
    authentication credentials in form of http(s)://username:password@host:port

    Explicit given username and password will get used instead of auth
    credentials given in uri. But we allways strip auth credentials from uri.

    """
    utype, _ = urllib.splittype(uri)
    if utype == "https" and username is not None and password is not None:
        return SecureBasicAuthTransport(username=username, password=password,
            contentType=contentType, jsonReader=jsonReader, verbose=verbose)
    elif utype == "https":
        return SecureTransport(contentType=contentType, jsonReader=jsonReader,
            verbose=verbose)
    elif username is not None and password is not None:
        return BasicAuthTransport(username=username, password=password,
            contentType=contentType, jsonReader=jsonReader, verbose=verbose)
    else:
        return Transport(contentType=contentType, jsonReader=jsonReader,
            verbose=verbose)


def getAuthorization(uri, username=None, password=None):
    """Returns the clean uri and authorization credentials as 3 part tuple

    Allways remove any username, password from uri if given.

    NOTE: this method is not used in the getTransport method bcecause it whould
    force to only use the BasicAuthTransport or the SecureBasicAuthTransport if
    authentication credentials are given in url or explitcit as arguments.
    """
    parsed = urlparse.urlparse(uri)
    if parsed.username is not None and parsed.password is not None:
        # first remove user, password from netloc
        netloc = urllib.splituser(parsed.netloc)[1]
        uri = '%s://%s%s' % (parsed.scheme, netloc, parsed.path)
        if username is None and password is None:
            # set username and password not explicit given, don't override
            # existing username password credentials
            username = parsed.username
            password = parsed.password
    return uri, username, password
