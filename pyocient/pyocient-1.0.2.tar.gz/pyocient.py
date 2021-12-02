#!/usr/bin/env python3
"""Python Database API for the Ocient Database

This python database API conforms to the Python Database API
Specification 2.0 and can be used to access the Ocient database.

This module can also be called as a main function, in which case
it acts as a primitive CLI for the database.

When called as main, it a connection string in DSN (data source name)
format, followed by zero or more query strings that will be executed.
Output is returned in JSON format.

The Ocient DSN is of the format:
   `ocient://user:password@[host][:port][/database][?param1=value1&...]`

`user` and `password` must be supplied.  `host` defaults to localhost,
port defaults to 4050, database defaults to `system` and `tls` defaults
to `off`.

Multiple hosts may be specified, separated by a comma, in which case the
hosts will be tried in order  Thus an example DSN might be
`ocient://someone:somepassword@host1,host2:4051/mydb`

Currently supported parameters are:

- tls: Which can have the values "off", "unverified", or "on"
- force: true or false to force the connection to stay on this server

Any warnings returned by the database are sent to the python warnings
module.  By default that module sends warnings to stdout, however
the behaviour can be changed by using that module.
"""
#pylint: disable=too-many-lines
import sys
import os
import socket
import ssl
import struct
import uuid
import datetime
import pathlib
import decimal
import ipaddress
import configparser
import re
import logging
from warnings import warn
from time import sleep, time_ns
from collections import namedtuple
from typing import Optional, NewType, Tuple, Callable, NamedTuple, Any, Type, List
from math import isinf
import dsnparse

from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger("pyocient")

# See PEP 249 for the values of these attributes
apilevel = "2.0"               # pylint: disable=invalid-name
threadsafety = 1               # pylint: disable=invalid-name
paramstyle = "pyformat"        # pylint: disable=invalid-name
DRIVER_ID = "pyocient"
PROTOCOL_VERSION = "7.0.1"
SESSION_EXPIRED_CODE = -733

here = pathlib.Path(__file__).parent.absolute()

version = {}
with open(os.path.join(here, 'version.py')) as version_file:
    exec(version_file.read(), version)
    version = version['__version__']
    parts = version.split('.')
    version_major = int(parts[0])
    version_minor = int(parts[1])


class SQLException(Exception):
    """Base exception for all Ocient exceptions.

    Attributes:

    - sql_state: The SQLSTATE defined in the SQL standard
    - reason: A string description of the exception
    - vendor_code: An Ocient specific error code
    """

    def __init__(self, reason="", sql_state="00000", vendor_code=0):
        super().__init__()
        self.sql_state = sql_state
        self.reason = reason
        self.vendor_code = vendor_code

    def __str__(self):
        return f"State: {self.sql_state} Code: {self.vendor_code} Reason: {self.reason}"

#########################################################################
# Database API 2.0 exceptions.  These are required by PEM 249
#########################################################################


class Error(SQLException):
    """Exception that is the base class of all other error exceptions."""

    def __init__(self, reason, sql_state="58005", vendor_code=-100):
        super().__init__(reason, sql_state=sql_state, vendor_code=vendor_code)


class Warning(SQLException):  # pylint: disable=redefined-builtin
    """Exception that is the base class of all other warning exceptions."""


class InterfaceError(Error):
    """Exception raised for errors that are related to the
    database interface rather than the database itself.
    """


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore
    """


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database's
    operation and not necessarily under the control of the programmer,
    e.g. an unexpected disconnect occurs, the data source name is not found.
    """


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors, e.g. table not found,
    syntax error in the SQL statement, wrong number of parameters
    specified, etc.
    """


class IntegrityError(DatabaseError):
    """Exception raised when the relational integrity of the database
    is affected, e.g. a foreign key check fails
    """


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the
    processed data like division by zero, numeric value out of range, etc.
    """


class NotSupportedError(DatabaseError):
    """Exception raised in case a method or database API was used which is not
    supported by the database
    """


class MalformedURL(DatabaseError):
    """Exception raised in case a malformed DSN is received"""

    def __init__(self, reason):
        super().__init__(sql_state="08001", vendor_code=-200, reason=reason)


class SyntaxError(ProgrammingError):
    """Exception raised in case a malformed DSN is received"""

    def __init__(self, reason):
        super().__init__(sql_state="42601", vendor_code=-500, reason=reason)


class TypeCodes:  # pylint: disable=too-few-public-methods
    """
    Database column type codes

    :meta private:
    """
    DEM = 0
    INT = 1
    LONG = 2
    FLOAT = 3
    DOUBLE = 4
    STRING = 5
    CHAR = 5
    TIMESTAMP = 6
    NULL = 7
    BOOLEAN = 8
    BINARY = 9
    BYTE = 10
    SHORT = 11
    TIME = 12
    DECIMAL = 13
    ARRAY = 14
    UUID = 15
    ST_POINT = 16
    IP = 17
    IPV4 = 18
    DATE = 19
    TIMESTAMP_NANOS = 20
    TIME_NANOS = 21
    TUPLE = 22
    ST_LINESTRING = 23
    ST_POLYGON = 24

    @classmethod
    def to_type(cls, typestr):
        """Given a string type, return its type code"""
        if hasattr(cls, typestr):
            return getattr(cls, typestr)
        raise Error(f"Unknown column type {str}")

    @classmethod
    def cls_to_type(cls, pclass):
        if pclass == str:
            return cls.STRING
        elif pclass == int:
            return cls.INT
        elif pclass == float:
            return cls.FLOAT
        elif pclass == uuid.UUID:
            return cls.UUID
        elif pclass == Optional[uuid.UUID]:
            return cls.UUID
        raise Error(f"Unknown column class {pclass}")


#########################################################################
# Database API 2.0 types.  These are required by PEM 249
#########################################################################
Binary = bytes  # : :meta private:
STRING = TypeCodes.STRING  # : :meta private:
BINARY = TypeCodes.BINARY  # : :meta private:
NUMBER = TypeCodes.INT  # : :meta private:
DATETIME = TypeCodes.TIMESTAMP  # : :meta private:
ROWID = TypeCodes.INT  # : :meta private:

#########################################################################
# Import our google protobuf message definitions
# We assume that the ClientWireProtocol_pb.py file is in the same directory
# as this file
#########################################################################
sys.path.append(os.path.abspath(os.path.dirname("__file__")))

# Try and import out protobuf definitions.
# While we transition to bazel we want to support both the makefile way and the new way (DB-13947)
try:
    import ClientWireProtocol_pb2 as proto  # pylint: disable=import-error,wrong-import-position
except ImportError as exc:
    from sharedMessages import clientWireProtocol_pb2 as proto  # pylint: disable=import-error,wrong-import-position

#########################################################################
# Build supported request/response type mappings
#########################################################################


class _OcientRequestFactory:
    def request(self, operation: str):
        """Generates a fully populated request protobuf"""
        raise NotImplementedError

    def response(self):
        """Generates a fully populated response protobuf"""
        raise NotImplementedError

    def process(self, rsp) -> Any:
        """Process the client response"""
        raise NotImplementedError


class _ExecuteQueryFactory(_OcientRequestFactory):
    def request(self, operation: str):
        """Generates a fully populated EXECUTE_QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('EXECUTE_QUERY')
        req.execute_query.sql = operation
        req.execute_query.force = False
        return req

    def response(self):
        """Generates a fully populated EXECUTE_QUERY response protobuf"""
        return proto.ExecuteQueryResponse()


class _ExecuteExplainFactory(_OcientRequestFactory):
    def request(self, operation: str):
        """Generates a fully populated EXECUTE_EXPLAIN request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('EXECUTE_EXPLAIN')
        req.execute_explain.format = proto.ExplainFormat.JSON
        splitted = operation.split(maxsplit=1)
        if len(splitted) == 2:
            req.execute_explain.sql = splitted[1]
        return req

    def response(self):
        """Generates a fully populated EXECUTE_EXPLAIN response protobuf"""
        return proto.ExplainResponseStringPlan()


class _ExecuteExportFactory(_OcientRequestFactory):
    def request(self, operation: str):
        """Generates a fully populated EXECUTE_EXPORT request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('EXECUTE_EXPORT')
        req.execute_export.sql = operation
        return req

    def response(self):
        """Generates a fully populated EXECUTE_EXPORT response protobuf"""
        return proto.ExecuteExportResponse()


class _ExplainPipelineFactory(_OcientRequestFactory):
    def request(self, operation: str):
        """Generates a fully populated EXPLAIN_PIPELINE request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('EXPLAIN_PIPELINE')
        req.explain_pipeline.sql = operation
        return req

    def response(self):
        """Generates a fully populated EXPLAIN_PIPELINE response protobuf"""
        return proto.ExplainPipelineResponse()


class _CheckDataFactory(_OcientRequestFactory):
    def request(self, operation: str):
        """Generates a fully populated CHECK_DATA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('CHECK_DATA')
        req.check_data.sql = operation
        return req

    def response(self):
        """Generates a fully populated CHECK_DATA response protobuf"""
        return proto.CheckDataResponse()


class _ForceExternalFactory(_OcientRequestFactory):
    def request(self, operation: str):
        """Generates a fully populated FORCE_EXTERNAL request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('FORCE_EXTERNAL')
        if operation.endswith("on"):
            req.force_external.force = True
        elif operation.endswith("off"):
            req.force_external.force = False
        else:
            raise SyntaxError("Format must be \"FORCE EXTERNAL (on|off)\"")
        return req

    def response(self):
        """Generates a fully populated FORCE_EXTERNAL response protobuf"""
        return proto.ConfirmationResponse()


class _SetSchemaFactory(_OcientRequestFactory):
    def request(self, schema: str):
        """Generates a fully populated SET SCHEMA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('SET_SCHEMA')
        req.set_schema.schema = schema
        return req

    def response(self):
        """Generates SET_SCHEMA response protobuf"""
        return proto.ConfirmationResponse()


class _GetSchemaFactory(_OcientRequestFactory):
    def request(self):
        """Generates a fully populated GET SCHEMA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('GET_SCHEMA')
        return req

    def response(self):
        """Generates SET_SCHEMA response protobuf"""
        return proto.GetSchemaResponse()


class _ClearCacheFactory(_OcientRequestFactory):
    def request(self):
        """Generates a fully populated CLEAR CACHE request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('CLEAR_CACHE')
        req.clear_cache.all_nodes = True
        return req

    def response(self):
        """Generates SET_SCHEMA response protobuf"""
        return proto.ConfirmationResponse()


class _SetParameterFactory(_OcientRequestFactory):
    def request(self, op: str, val: int):
        """Generates a fully populated SET PARAMETER request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('SET_PARAMETER')

        sp = req.set_parameter

        if op == 'MAXROWS':
            sp.row_limit.rowLimit = val
        elif op == 'MAXTIME':
            sp.time_limit.timeLimit = val
        elif op == 'MAXTEMPDISK':
            sp.temp_disk_limit.tempDiskLimit = val
        elif op == 'PRIORITY':
            sp.priority.priority = val
        elif op == 'PARALLELISM':
            sp.concurrency.concurrency = val
        else:
            raise ProgrammingError(reason=f"Syntax error. Invalid SET {op}")

        return req

    def response(self):
        """Generates a SET_PARAMETER response protobuf"""
        return proto.ConfirmationResponse()


class _CancelQueryFactory(_OcientRequestFactory):
    def request(self, id: str):
        """Generates a fully populated CANCEL QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('CANCEL_QUERY')
        req.cancel_query.sql = id
        return req

    def response(self):
        """Generates a CANCEL_QUERY response protobuf"""
        return proto.CancelQueryResponse()


class _KillQueryFactory(_OcientRequestFactory):
    def request(self, id: str):
        """Generates a fully populated KILL QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('KILL_QUERY')
        req.kill_query.sql = id
        return req

    def response(self):
        """Generates a KILL_QUERY response protobuf"""
        return proto.KillQueryResponse()


class _GetSystemMetadataFactory(_OcientRequestFactory):
    def request(self, op, schema, table, column, view):
        """Generates a fully populated GET_SYSTEM_METADATA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('FETCH_SYSTEM_METADATA')
        req.fetch_system_metadata.call = op

        if schema is not None:
            req.fetch_system_metadata.schema = schema
        if table is not None:
            req.fetch_system_metadata.table = table
        if column is not None:
            req.fetch_system_metadata.column = column
        if view is not None:
            req.fetch_system_metadata.view = view

        return req

    def response(self):
        """Generates a fully populated CHECK_DATA response protobuf"""
        return proto.FetchSystemMetadataResponse()


"""Mapping from query type to its request factory"""
_OCIENT_REQUEST_FACTORIES = {
    'SELECT': _ExecuteQueryFactory(),
    'WITH': _ExecuteQueryFactory(),
    'EXPLAIN PIPELINE': _ExplainPipelineFactory(),
    'EXPLAIN': _ExecuteExplainFactory(),
    'EXPORT': _ExecuteExportFactory(),
    'CHECK': _CheckDataFactory(),
    'FORCE': _ForceExternalFactory(),
    'SET SCHEMA': _SetSchemaFactory(),
    'GET SCHEMA': _GetSchemaFactory(),
    'CLEAR CACHE': _ClearCacheFactory(),
    'SET': _SetParameterFactory(),
    'CANCEL': _CancelQueryFactory(),
    'KILL': _KillQueryFactory(),
    'GET SYSTEM METADATA': _GetSystemMetadataFactory(),
}


def _convert_exception(msg):
    """Internal routine to convert the google protobuf ConfirmationResponse
    to an exception
    """
    if msg.vendor_code < 0:
        return Error(sql_state=msg.sql_state, reason=msg.reason, vendor_code=msg.vendor_code)

    return Warning(sql_state=msg.sql_state, reason=msg.reason, vendor_code=msg.vendor_code)


def _send_msg(conn, protobuf_msg):
    """Internal routine to send a protobuf message on a connection"""
    if not conn.sock:
        raise ProgrammingError("Connection not available")

    logger.debug(f"Sending message on socket {conn.sock}: {protobuf_msg}")

    try:
        conn.sock.sendall(struct.pack('!i', protobuf_msg.ByteSize()) + protobuf_msg.SerializeToString())
    except IOError:
        raise IOError("Network send error")


def _recv_all(conn, size):
    """Internal routine to receive `size` bytes of data from a connection"""
    if not conn.sock:
        raise Error("Connection not available")

    while len(conn._buffer) < size:
        received = conn.sock.recv(16777216)  # 16MB buffer
        if not received:
            raise IOError("Network receive error")
        conn._buffer += received

    ret = conn._buffer[:size]
    conn._buffer = conn._buffer[size:]

    return ret


def _recv_msg(conn, protobuf_msg):
    """Internal routine to receive a protobuf message on a connection"""
    hdr = _recv_all(conn, 4)
    msgsize = struct.unpack('!i', hdr)[0]

    msg = _recv_all(conn, msgsize)

    protobuf_msg.ParseFromString(msg)

    logger.debug(f"Received message on connection {conn.sock}: {protobuf_msg}")

    return protobuf_msg


def Date(year, month, day):  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct a
    Date object from year, month, day
    """
    return datetime.datetime(year, month, day)


def Time(hour, minute, second):  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct a
    Time object from hour, minute, second
    """
    return datetime.time(hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):  # pylint: disable=invalid-name,too-many-arguments
    """Type constructor required in PEP 249 to construct
    a Timestamp object from year, month, day, hour, minute, second
    """
    return datetime.datetime(year, month, day, hour, minute, second).timestamp()


def DateFromTicks(ticks):  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Date object from a timestamp of seconds since epoch
    """
    return datetime.datetime.utcfromtimestamp(ticks)


def TimeFromTicks(ticks):  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Time object from a timestamp of seconds since epoch
    """
    date_time = datetime.datetime.utcfromtimestamp(ticks)
    return datetime.time(date_time.hour, date_time.minute, date_time.second)


def TimestampFromTicks(ticks):  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Timestamp object from a timestamp of seconds since epoch
    """
    return ticks


def _hash_key(shared_key, salt):
    """Internal key hash function"""
    # No idea where this algorithm came from, but do a home grown key
    # deriviation function
    buffer = struct.pack('!i', len(shared_key))
    buffer = buffer + salt
    buffer = buffer + shared_key
    hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
    hasher.update(buffer)
    return hasher.finalize()

# Sessions code

# Used for representing a session created with a security token sign in


class SecurityToken:
    def __init__(self, tokenData: str, tokenSignature: str, issuerFingerprint: str):
        self.tokenData = tokenData
        self.tokenSignature = tokenSignature
        self.issuerFingerprint = issuerFingerprint

# Used for representing a session created with a user and password sign in.


class UserAndPassword:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password


class Session:

    def __init__(self, securityToken=None, userAndPassword=None):
        # Only one of these should be instantiated. The other MUST be none.
        self.securityToken = securityToken
        self.userAndPassword = userAndPassword


class Connection:
    """A connection to the Ocient database. Normally constructed by
    calling the module `connect()` call, but can be constructed
    directly
    """
    # pylint: disable=too-many-instance-attributes
    TLS_NONE = 1  # : :meta private:
    TLS_UNVERIFIED = 2  # : :meta private:
    TLS_ON = 3  # : :meta private:

    HANDSHAKE_CBC = 1
    HANDSHAKE_GCM = 2
    HANDSHAKE_SSO = 3

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 4050
    DEFAULT_DATABASE = 'system'

    hosts = []
    port = None
    database = None
    tls = None
    force = None
    handshake = None
    user = None
    password = None
    secondary_interfaces = None
    secondary_index = -1
    sock = None
    session_id = str(uuid.uuid1())

    session = None
    serverSessionId = None

    # Whether the next execute query run on this connection will be redirected. Does nothing if force is set to true
    force_next_redirect = False

    # Sessions code end

    # the PEP 249 standard recomments making the module level exceptions
    # also attributes on the Connection class
    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    InternalError = InternalError
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    IntegrityError = IntegrityError
    DataError = DataError
    NotSupportedError = NotSupportedError

    def _sslize_connection(self):
        """
        If SSL is specified, wrap the socket in an SSL connection
        """
        if self.tls != self.TLS_NONE:
            logger.debug("Creating TLS connection")
            context = ssl.create_default_context()
            context.check_hostname = False
            if self.tls != self.TLS_ON:
                context.verify_mode = ssl.CERT_NONE
            self.sock = context.wrap_socket(self.sock)

    def __init__(self, dsn=None, user=None, password=None, host=None, database=None, tls=None, handshake=None, force=None, configfile=None, session=None):
        # pylint: disable=too-many-arguments,no-member
        """Connection parameters can be specified as part of the dsn,
        using keyword arguments or both.  If both are specified, the keyword
        parameter overrides the value in the dsn.

        The Ocient DSN is of the format:
        `ocient://user:password@[host][:port][/database][?param1=value1&...]`

        `user` and `password` must be supplied.  `host` defaults to localhost,
        port defaults to 4050, database defaults to `system` and `tls` defaults
        to `off`.

        Multiple hosts may be specified, separated by a comma, in which case the
        hosts will be tried in order  Thus an example DSN might be
        `ocient://someone:somepassword@host1,host2:4051/mydb`

        configfile is the name of a configuration file in INI format, where each
        section is either default, or a pattern that matches the host and optionally
        database. sections are matched in order, so more specific sections should
        precede less specific sections::

            [DEFAULT]
            tls = unverified

            # This will match the specific host and database
            [foo.ocient.com/somedb]
            user = panther
            password = pink

            # This will match the specific host
            [foo.ocient.com]
            user = panther
            password = pink

            # This will match any host in the ocient.com domain
            [*.ocient.com]
            user = tom
            password = jerry
            database = mice

            # This will match any host in the ocient.com domain
            [*.ocient.com]
            user = tom
            password = jerry

        Currently supported parameters are:

        - tls: Which can have the values "off", "unverified", or "on" in the dsn,
            or Connection.TLS_NONE, Connection.TLS_UNVERIFIED, or
            Connection.TLS_ON as a keyword parameter.
        - force: True or False, whether to force the connection to remain on this
            server
        """
        # pylint: disable=no-member
        self._parse_args(dsn, user, password, host, database, tls, handshake, configfile)

        saved_exc = None
        for one_host in self.hosts:
            try:
                logger.info(f"Trying to connect to {one_host}:{self.port}")
                self.sock = socket.create_connection((one_host, self.port))
                logger.info(f"Connected to {one_host}:{self.port} on socket {self.sock}")
                saved_exc = None
                break
            except ConnectionError as exc:
                saved_exc = exc
            except Exception as exc:
                saved_exc = exc

        if saved_exc is not None:
            raise Error(f"Unable to connect to {','.join(self.hosts)}:{self.port}: {str(saved_gexc)}") from saved_exc

        self._sslize_connection()

        if force is not None:
            self.force = force

        self._buffer = b''
        self.session = session
        if self.handshake == self.HANDSHAKE_SSO:
            if self.user.lower() != "" or self.password.lower() != "":
                # If either are non-empty, use the CBC_GCM.
                self._client_handshake_CBC_GCM(is_explicit_sso=True, force=self.force)
            else:
                if self.session is not None:
                    self._client_handshake_security_token()
                else:
                    self._client_handshake_SSO()
        else:
            self._client_handshake_CBC_GCM(is_explicit_sso=False, force=self.force)

    def _initialize_client_connection(self, client_connection_message):
        """Initializes fields used in initial client handshake requests.
        1. database
        2. clientid (pyocient)
        3. protocol version 
        4. version_major
        5. version_minor
        6. session id

        Note, not all fields are initialized. Some fields are special to certain client handshakes.
        For example, the SSO handshake with token does not take user and instead takes a security token.

        Args:
            client_connection_message ([proto message]): the client handshake request to initialize
        """
        client_connection_message.database = self.database
        client_connection_message.clientid = DRIVER_ID
        client_connection_message.version = PROTOCOL_VERSION
        client_connection_message.majorClientVersion = version_major
        client_connection_message.minorClientVersion = version_minor
        client_connection_message.sessionID = self.session_id

    def _client_handshake_CBC_GCM(self, is_explicit_sso=False, force=False):
        while True:
            ##################################################################
            # Send the CLIENT_CONNECTION request
            ##################################################################
            req = proto.Request()
            if self.handshake == self.HANDSHAKE_CBC:
                req.type = req.CLIENT_CONNECTION
                client_connection = req.client_connection
            else:
                # Should be GCM
                req.type = req.CLIENT_CONNECTION_GCM
                client_connection = req.client_connection_gcm
                client_connection.explicitSSO = is_explicit_sso
            client_connection.userid = self.user
            self._initialize_client_connection(client_connection)

            _send_msg(self, req)

            ##################################################################
            # Get the CLIENT_CONNECTION response and process it
            ##################################################################
            if self.handshake == self.HANDSHAKE_CBC:
                # CBC
                rsp = _recv_msg(self, proto.ClientConnectionResponse())
            else:
                # GCM or explicit SSO
                rsp = _recv_msg(self, proto.ClientConnectionGCMResponse())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                raise _convert_exception(rsp.response)

            peer_key = load_pem_public_key(rsp.pubKey.encode(encoding='UTF-8', errors='strict'), backend=default_backend())
            (cipher, generated_hmac, public_key) = self._encryption_routine(rsp.iv, peer_key)

            ##################################################################
            # Send the CLIENT_CONNECTION2 request
            ##################################################################
            req = proto.Request()
            if self.handshake == self.HANDSHAKE_CBC:
                req.type = req.CLIENT_CONNECTION2
                req.client_connection2.cipher = cipher
                req.client_connection2.force = force
                req.client_connection2.hmac = generated_hmac
                req.client_connection2.pubKey = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo)
            else:
                req.type = req.CLIENT_CONNECTION_GCM2
                req.client_connection_gcm2.cipher = cipher
                req.client_connection_gcm2.force = force
                req.client_connection_gcm2.hmac = generated_hmac
                req.client_connection_gcm2.explicitSSO = is_explicit_sso
                req.client_connection_gcm2.pubKey = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo)

            _send_msg(self, req)

            ##################################################################
            # Get the CLIENT_CONNECTION response and process it
            ##################################################################
            if self.handshake == self.HANDSHAKE_CBC:
                # CBC
                rsp = _recv_msg(self, proto.ClientConnection2Response())
            else:
                # GCM or explicit SSO
                rsp = _recv_msg(self, proto.ClientConnectionGCM2Response())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                # Save the server session id
                self.serverSessionId = rsp.serverSessionId
                self.session = Session(userAndPassword=UserAndPassword(self.user, self.password))
                logger.info(f"Connected to server session Id: {self.serverSessionId}")
                # Save secondary interfaces.
                self._save_secondary_interfaces(rsp.secondary)

                # Redirect the connection
                if rsp.redirect:
                    self.sock.close()
                    self.sock = socket.create_connection((rsp.redirectHost, rsp.redirectPort))
                    self._sslize_connection()

                    return self._client_handshake_CBC_GCM(is_explicit_sso, True)

                break

            # there is something broken in our handshake...retry
            if rsp.response.vendor_code == -202:
                logger.debug("Handshake error...retrying")
                continue

            raise _convert_exception(rsp.response)

    def _client_handshake_SSO(self):
        """Internal routine for single sign on handshake (SSO).
        1. Driver requests to sign on via SSO.
        2. Server sends back an auththentication URL.
        3. Driver launches URL in default browser (or prints the url to std out if not possible)
        4. User authenticates in browser.
        5. Driver continuously polls the database until login completes. 
        6. Upon completetion, server sends back a security token with which the driver can connect. (Used for redirecting / reconnecting)
        """
        from webbrowser import open_new

        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_SSO
        client_connection = req.client_connection_sso

        self._initialize_client_connection(client_connection)
        # Send message
        _send_msg(self, req)
        # Receive response
        rsp = _recv_msg(self, proto.ClientConnectionSSOResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp.response)

        # Open browser for user to authenticate.
        if not open_new(rsp.authUrl):
            logger.info("[pyocient] Could not open default browser with webbrowser library. Please authenticate at: " + rsp.authUrl)
            print("[pyocient] Could not open default browser with webbrowser library. Please authenticate at: ", rsp.authUrl)

        # Poll the database
        self._poll_database(rsp.requestId)

    def _poll_database(self, requestId):
        """Polls the database until we either receive an error or a successful login message.

        Args:
            requestId (String): the request ID associated with this login attempt.
        """

        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_SSO2
        req.client_connection_sso2.force = self.force
        req.client_connection_sso2.requestId = requestId

        keepPolling = True
        waitFor = 0
        while keepPolling:
            sleep(waitFor)
            # Poll
            _send_msg(self, req)

            # Receive response
            rsp = _recv_msg(self, proto.ClientConnectionSSO2Response())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                raise _convert_exception(rsp.response)

            if(rsp.HasField("pollingIntervalSeconds")):
                # Continue polling
                waitFor = rsp.pollingIntervalSeconds
                continue
            else:
                # Success
                waitFor = 0
                keepPolling = False

        self.serverSessionId = rsp.sessionInfo.serverSessionId
        logger.debug(f"Connected to server session Id: {self.serverSessionId}")
        received_token = rsp.sessionInfo.securityToken
        self.session = Session(securityToken=SecurityToken(received_token.data, received_token.signature, received_token.issuerFingerprint))

        # Redirect the connection
        if rsp.redirect:
            self.sock.close()
            self.sock = socket.create_connection((rsp.redirectHost, rsp.redirectPort))
            self._sslize_connection()

            return self._client_handshake_security_token(True)

    def _client_handshake_security_token(self, force=False):
        """ Once a connection acquires a security token, it can use that to log in. This handshake only
        sends 1 message whereas the other handshakes send 2.
        """
        while True:
            req = proto.Request()
            req.type = req.CLIENT_CONNECTION_SECURITY_TOKEN
            client_connection = req.client_connection_security_token

            self._initialize_client_connection(client_connection)
            # Attach the security token used to log in
            client_connection.securityToken = self.session.securityToken.tokenData
            client_connection.tokenSignature = self.session.securityToken.tokenSignature
            client_connection.issuerFingerprint = self.session.securityToken.issuerFingerprint
            client_connection.force = force

            _send_msg(self, req)

            rsp = _recv_msg(self, proto.ClientConnectionSecurityTokenResponse())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:

                # Redirect the connection if requested
                if rsp.redirect:
                    self.sock.close()
                    self.sock = socket.create_connection((rsp.redirectHost, rsp.redirectPort))
                    self._sslize_connection()

                    return self._client_handshake_security_token(True)

                # Capture the session id
                self.serverSessionId = rsp.serverSessionId
                logger.debug(f"Connected to server session Id: {self.serverSessionId}")
                break
            # there is something broken in our handshake...retry
            if rsp.response.vendor_code == -202:
                logger.debug("Handshake error...retrying")
                continue

            raise _convert_exception(rsp.response)

    def _save_secondary_interfaces(self, new_secondary_interfaces):
        """After secondary interfaces are sent from the server, we need to
        save them and use them for redirecting. This is important if we 
        get redirected to mapped sql endpoints.

        Args:
            secondary_interfaces ([class 'google.protobuf.pyext._message.RepeatedCompositeContainer']): 
            the secondary interfaces, which is really a list of list of strings.
        """
        self.secondary_interfaces = []
        for i in range(len(new_secondary_interfaces)):
            self.secondary_interfaces.append([])
            for j in range(len(new_secondary_interfaces[i].address)):
                interface = new_secondary_interfaces[i].address[j]
                (interface_ip, interface_port) = interface.split(":")
                # Return of gethostbyname_ex is (hostname, alias of host name, other ip addresses of host name)
                other_ips = socket.gethostbyname_ex(interface_ip)[2]
                for other_ip in other_ips:
                    new_interface = other_ip + ":" + interface_port
                    self.secondary_interfaces[i].append(new_interface)

        hosts = []
        for one_host in self.hosts:
            hosts = hosts + [h + ":" + str(self.port) for h in socket.gethostbyname_ex(one_host)[2]]
        for outer_list in self.secondary_interfaces:
            for index in range(len(outer_list)):
                if outer_list[index] in hosts:
                    self.secondary_index = index
                    break

    def _encryption_routine(self, initialization_vector, peer_key):
        """Internal routine to do the encryption handshake of
        the password
        CBC is the previous form of encryption. We now use GCM by default.
        """
        # Create our keys using the parameters from the peer key
        params = peer_key.parameters()
        private_key = params.generate_private_key()

        # Create a shared key
        shared_key = private_key.exchange(peer_key)

        key = _hash_key(shared_key, b'\0')
        mac_key = _hash_key(shared_key, b'\1')

        if self.handshake == self.HANDSHAKE_CBC:
            # Pad the plaintext password out using PKCS7
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(self.password.encode(encoding='UTF-8', errors='strict'))
            padded_data += padder.finalize()

            # Encrypt the padded plaintext password using AES CBC and the key
            # we got from our KDF
            encryptor = Cipher(algorithms.AES(key), modes.CBC(initialization_vector),
                               backend=default_backend()).encryptor()
            min_cipher_bytes = len(padded_data) + 4096
            cipher = bytearray(min_cipher_bytes)
            len_encrypted = encryptor.update_into(padded_data, cipher)
            cipher = bytes(cipher[:len_encrypted]) + encryptor.finalize()
        else:
            encryptor = Cipher(algorithms.AES(key), modes.GCM(initialization_vector),
                               backend=default_backend()).encryptor()
            # We do not use AAD
            cipher = encryptor.update(self.password.encode(encoding='UTF-8', errors='strict')) + encryptor.finalize()
            # Server side expects that the tag is at the end of the cipher text.
            cipher += encryptor.tag

        # Now create an HMAC using the other KDF derived key and the
        # encrypted password
        hasher = hmac.HMAC(mac_key, hashes.SHA256(), backend=default_backend())
        hasher.update(cipher)
        generated_hmac = hasher.finalize()

        return (cipher, generated_hmac, private_key.public_key())

    def _parse_args(self, dsn, user, password, host, database, tls, handshake, configfile):  # pylint: disable=too-many-arguments
        """Internal routine to resolve function arguments, config file, and dsn"""
        # pylint: disable=no-member,too-many-branches,too-many-statements
        # First, parse the DSN if it exists
        if dsn is not None:
            parsed = dsnparse.parse(dsn)

            if parsed.scheme and parsed.scheme.lower() != 'ocient':
                raise MalformedURL(f"Invalid DSN scheme: {parsed.scheme}")

            for attr in ['database', 'user', 'password', 'port']:
                setattr(self, attr, getattr(parsed, attr))

            if parsed.host:
                self.hosts = parsed.host.split(',')

            if self.database is not None and len(self.database) == 0:
                self.database = None
            if self.database is not None and self.database[0] == '/':
                self.database = self.database[1:]

            if 'tls' in parsed.query:
                self.tls = parsed.query['tls']

            if 'force' in parsed.query:
                self.force = parsed.query['force']

            if 'handshake' in parsed.query:
                handshake = parsed.query['handshake'].lower()

            if self.user is None:
                self.user = ""

            if self.password is None:
                self.password = ""

        # Now override the DSN values with any values passed in as parameters
        if user is not None:
            self.user = user

        if password is not None:
            self.password = password

        if host:
            # Handle host:port
            parts = host.split(':')
            if len(parts) == 1:
                self.hosts = parts[0].split(',')
            elif len(parts) == 2:
                self.hosts = parts[0].split(',')
                self.port = int(parts[1])
            else:
                raise MalformedURL(f"Invalid host value: {host}")

        if database:
            self.database = database

        if tls is not None:
            self.tls = tls

        if handshake is not None:
            self.handshake = handshake

        # Set the default host now, since we use that as a key into the
        # config file
        if self.hosts is None:
            self.hosts = [self.DEFAULT_HOST]

        # Now build a configparser with default values
        config = configparser.ConfigParser(defaults={'port': str(self.DEFAULT_PORT),
                                                     'database': self.DEFAULT_DATABASE,
                                                     'tls': 'unverified',
                                                     'force': 'false',
                                                     'handshake': ''},
                                           interpolation=None)
        configvals = None

        # If we have a config file try loading that
        if configfile is not None:

            config.read(configfile)

            # Work out the host/database if we know it
            host_db = ','.join(self.hosts)
            if self.database is not None:
                host_db = host_db + "/" + self.database

            # Try and match each section in the INI file with the host/database
            for s in config.sections():
                if re.match(s, host_db):
                    configvals = config[s]
                    break

        # if we didn't find a matching host (or there is no file). use the defaults
        if configvals is None:
            configvals = config['DEFAULT']
        # Force is not places here so it can get parsed below.
        for attr in ['port', 'database', 'tls', 'handshake']:
            if getattr(self, attr) is None:
                setattr(self, attr, configvals[attr])

        if getattr(self, 'user') is None:
            self.user = configvals.get("user", "")

        # special case 'force' since getboolean is clever
        if self.force is None:
            self.force = configvals.getboolean('force')

        # And finally tidy up some things
        if isinstance(self.port, str):
            self.port = int(self.port)

        if isinstance(self.tls, str):
            if self.tls.lower() == 'off':
                self.tls = self.TLS_NONE
            elif self.tls.lower() == 'unverified':
                self.tls = self.TLS_UNVERIFIED
            elif self.tls.lower() == 'on':
                self.tls = self.TLS_ON
            else:
                raise MalformedURL(f"Invalid tls value: {self.tls}")

        if isinstance(self.handshake, str):
            if self.handshake.lower() == 'cbc':
                self.handshake = self.HANDSHAKE_CBC
            elif self.handshake.lower() == 'sso':
                self.handshake = self.HANDSHAKE_SSO
            # If they didn't specify handshake, it will be blank and thus should be GCM.
            elif self.handshake.lower() == 'gcm' or self.handshake.lower() == '':
                self.handshake = self.HANDSHAKE_GCM
            else:
                print(self.handshake)
                raise MalformedURL(f"Invalid handshake value: {self.handshake}")

        # Don't assert a user parameter has been set. An empty
        # string for this field is used for authenticating SSO users

        # Don't assert a password parameter has been set. At empty
        # user and password is for authentication flow with SSO.

    def close(self):
        """ Close the connection. Subsequent queries on this connection
        will fail
        """
        if not self.sock:
            raise Error("No connection")

        logger.debug(f"Closing connection on socket {self.sock}")
        # Do this little dance so that even if the close() call
        # blows up, we have already set self.sock to None
        sock = self.sock
        self.sock = None
        sock.close()

    def commit(self):
        """Commit a transaction. Currently ignored"""

    def cursor(self):
        """Return a new cursor for this connection"""
        if not self.sock:
            raise Error("No connection")
        return Cursor(self)

    def __del__(self):
        if self.sock is not None:
            self.close()

    def redirect(self, new_endpoint):
        """
        Handles redirecting to a new connection based on the secondary interfaces saved on this connection.
        Note that we have to consider the mapping that exists and remap the given host and port properly.

        Args:
            new_endpoint ([string]): [The new endpoint to use. We will map this. Format: "host:port"]

        Returns:
            [type]: A new connection.
        """
        endpoint_to_connect = ""
        if self.secondary_index != -1:
            outer_index = 0
            for outer_list in self.secondary_interfaces:
                if outer_list[0] == new_endpoint:
                    break
                outer_index += 1
            if(outer_index < len(self.secondary_interfaces)):
                endpoint_to_connect = self.secondary_interfaces[outer_index][self.secondary_index]
            else:
                endpoint_to_connect = new_endpoint

        else:
            endpoint_to_connect = new_endpoint

        return Connection(user=self.user,
                          password=self.password,
                          host=endpoint_to_connect,
                          database=self.database,
                          tls=self.tls,
                          handshake=self.handshake,
                          session=self.session)

    def refresh(self):
        """
        Used to refresh the session associated with this connection. The server will
        return a new server session id and security token.
        """
        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_REFRESH_SESSION
        client_connection = req.client_connection_refresh_session

        # Send message
        _send_msg(self, req)
        # Recieve message
        rsp = _recv_msg(self, proto.ClientConnectionRefreshSessionResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            # Capture the session id
            self.serverSessionId = rsp.sessionInfo.serverSessionId
            logger.debug(f"Connected to server session Id: {self.serverSessionId}")
            received_token = rsp.sessionInfo.securityToken
            if self.session.securityToken != None:
                self.session = Session(securityToken=SecurityToken(received_token.data, received_token.signature, received_token.issuerFingerprint))
            else:
                # Ignore the security token
                self.session = Session(userAndPassword=UserAndPassword(self.user, self.password))
            return
        # Something bad happened with the refresh attempt.
        raise _convert_exception(rsp.response)


class Cursor:
    # pylint: disable=too-many-instance-attributes
    """A database cursor, which is used to manage a querie and its returned results"""

    def __init__(self, conn):
        """Cursors are normally created by the cursor() call on a connection, but can
        be created directly by providing a connection
        """
        self.connection = conn
        self.arraysize = 1

        self._reinitialize()

    def _reinitialize(self):
        """Internal function to initialize a cursor"""
        # Set the state
        self.query_id = None
        self.rowcount = -1
        self.rownumber = None
        self.resultset_tuple = None
        self.description = None
        self.end_of_data = False
        self.explain_result = None
        self.list_result = None
        self._buffers = []
        self._offset = 0
        self._pending_ops = []

    def setinputsizes(self, sizes):
        """This can be used before a call to .execute*() to predefine
        memory areas for the operation's parameters. Currently ignored
        """

    def setoutputsize(self, size, column=None):
        """Set a column buffer size for fetches of large columns
        (e.g. LONGs, BLOBs, etc.). The column is specified as an
        index into the result sequence. Currently ignored
        """

    def close(self):
        """Close this cursor.  The current result set is closed, but
        the cursor can be reused for subsequent execute() calls.
        """
        self._reinitialize()

    def executemany(self, operation, parameterlist):
        """Prepare a database operation (query or command) and then execute it against
        all parameter sequences or mappings found in the sequence parameterlist.

        Parameters may be provided as a mapping and will be bound to variables
        in the operation. Variables are specified in Python extended format codes,
        e.g. ...WHERE name=%(name)
        """
        self._reinitialize()

        # we can't just execute all the queries at once....ocient only allows
        # one query at a time on a connection.  So queue up all the queries and
        # we'll call them later
        for param in parameterlist:
            self._pending_ops.append(operation % param)

        if self._pending_ops:
            self._execute_internal(self._pending_ops.pop(0))

        return self

    def execute(self, operation, parameters=None):
        """Prepare and execute a database operation (query or command).

        Parameters may be provided as a mapping and will be bound to variables
        in the operation. Variables are specified in Python extended format codes,
        e.g. ...WHERE name=%(name)
        """
        self._reinitialize()
        self._execute_internal(operation, parameters)

        return self

    def _execute_internal(self, operation, parameters=None):
        """Internal execute routine that gets called from execute and executemany
        """
        #pylint: disable=too-many-branches

        if hasattr(operation, 'decode'):
            operation = operation.decode()

        if parameters is not None:
            if hasattr(list(parameters.keys())[0], 'decode'):
                parameters = {key.decode(): value for (key, value) in parameters.items()}
            operation = operation % parameters

        # We need to figure out whether we should call
        # execute_query or execute_update
        stripped = operation

        # Loop until we have some starting words. Note this
        # doesn't actually handle the case of 'word1 /* comment */ word2',
        # but none of the other clients do either...
        while True:
            # strip off starting spaces
            stripped = stripped.lstrip()

            # if this starts with --, strip the rest of the line
            if stripped.startswith('--'):
                pos = stripped.find('\n')
                if pos == -1:
                    stripped = ""
                else:
                    stripped = stripped[pos+1:]

            # if this starts with /*, strip until */
            elif stripped.startswith('/*'):
                pos = stripped.find('*/')
                if pos == -1:
                    stripped = ""
                else:
                    stripped = stripped[pos+2:]
            else:
                # yay, no comments, move to the next phase
                break

        # if we don't have anything left, just return []
        if not stripped:
            return

        # now split out the words
        words = stripped.split(None, 3)

        # Single word matches
        query_type = words[0].upper()
        if query_type in ['SELECT', 'WITH', 'EXPORT', 'CHECK']:
            return self._execute_query(operation=operation, query_type=query_type)
        elif query_type in ['EXPLAIN']:
            # explain pipeline
            if len(words) > 1 and words[1].upper() == 'PIPELINE':
                return self._execute_query(operation=operation, query_type=query_type + " PIPELINE")
            else:
                return self._execute_query(operation=operation, query_type=query_type)
        elif query_type in ["LIST"]:
            if operation.upper() == "LIST ALL QUERIES":
                return self._execute_query(operation="SELECT * FROM SYS.QUERIES", query_type="SELECT")
            elif operation.upper() == "LIST ALL COMPLETED QUERIES":
                return self._execute_query(operation="SELECT * FROM SYS.COMPLETED_QUERIES", query_type="SELECT")
            else:
                return self._execute_list(operation=operation)
        elif query_type == "FORCE":
            self._execute_force(operation=operation)
        elif query_type == "SET":
            self._execute_set(words[1:])
        elif query_type == "GET":
            self._execute_get(words[1:])
        elif query_type == "KILL" or query_type == "CANCEL":
            self._execute_cancelkill(query_type, words[1:])
        elif query_type == "CLEAR":
            self._execute_clear(words[1:])
        else:
            # ok, this is an update
            self._execute_update(operation)

    def tables(self, schema='%', table='%'):
        """Get the database tables"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_TABLES, schema=schema, table=table)
        return self

    def system_tables(self, table='%'):
        """Get the database system tables"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_SYSTEM_TABLES, table=table)
        return self

    def views(self, view='%'):
        """Get the database views"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_VIEWS, view=view)
        return self

    def columns(self, schema='%', table='%', column='%'):
        """Get the database columns"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_COLUMNS,
                           schema=schema, table=table, column=column)
        return self

    def indexes(self, schema='%', table='%'):
        """Get the database indexes"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_INDEXES, schema=schema, table=table)
        return self

    def getTypeInfo(self):  # pylint: disable=invalid-name
        """Get the database type info"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_TYPE_INFO)
        return self

    def getSystemVersion(self):
        return self._execute_systemmetadata(proto.FetchSystemMetadata.GET_DATABASE_PRODUCT_VERSION)

    def _metadata_req(self, reqtype, schema='%', table='%', column='%', view='%'):
        """Internal function to get database metadata"""
        # pylint: disable=no-member,too-many-arguments
        self._reinitialize()
        # req.fetch_system_metadata.GET_TABLES
        req = proto.Request()
        req.type = req.FETCH_SYSTEM_METADATA
        req.fetch_system_metadata.call = reqtype
        req.fetch_system_metadata.schema = schema
        req.fetch_system_metadata.table = table
        req.fetch_system_metadata.column = column
        req.fetch_system_metadata.view = view
        req.fetch_system_metadata.test = True

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchSystemMetadataResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR:
            if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                _metadata_req(reqtype, schema=schema, table=table, column=column, view=view)
                return
            else:
                raise _convert_exception(rsp.response)

        self._get_result_metadata()

        self.rownumber = 0
        for blob in rsp.result_set_val.blobs:
            if not self._buffers:
                self._offset = 0
            self._buffers.append(blob)

    def _execute_query(self, operation, query_type: str = 'SELECT'):
        """Execute a query"""
        # pylint: disable=no-member

        factory = _OCIENT_REQUEST_FACTORIES.get(query_type.upper(), None)

        if factory is None:
            raise NotSupportedError(f"Query type '{query_type}' not supported by pyocient'")

        # generate the appropriate request
        req = factory.request(operation)

        # Loop while we retry redirects and reconnects
        while True:
            if req.type == proto.Request.RequestType.Value('EXECUTE_QUERY'):
                req.execute_query.forceRedirect = self.connection.force_next_redirect
                self.connection.force_next_redirect = False
            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, factory.response())
            except IOError:
                # remake our connection
                self.connection = Connection(user=self.connection.user,
                                             password=self.connection.password,
                                             host=f"{','.join(self.connection.hosts)}:{self.connection.port}",
                                             database=self.connection.database,
                                             tls=self.connection.tls,
                                             handshake=self.connection.handshake,
                                             session=self.connection.session)

                continue

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                    # Need to refresh the session
                    self.connection.refresh()
                    # and try again
                    continue
                else:
                    raise _convert_exception(rsp.response)

            # see if we are being told to redirect
            redirect = getattr(rsp, 'redirect', False)
            if not redirect:
                break

            # remake our connection
            self.connection.close()
            self.connection = self.connection.redirect(f"{rsp.redirectHost}:{rsp.redirectPort}")

        query_id = getattr(rsp, 'queryId', None)
        if query_id is not None:
            self.query_id = query_id

        self.rownumber = 0

        if query_type in ['SELECT', 'WITH']:
            self._get_result_metadata()

        elif query_type == 'EXPLAIN':
            self.description = [('explain',
                                TypeCodes.CHAR,
                                None,  # display_size
                                None,  # internal_size
                                None,  # precision
                                None,  # scale
                                None  # null_ok
                                 )]

            self.explain_result = rsp.plan

    # After list all queries and list all completed queries have been remapped, this is no longer used. But it can be used for other things.
    # Ex: list tables, list views, list table privileges. None of these are implemented yet.
    def _execute_list(self, operation: str = 'LIST ALL QUERIES'):
        """Execute LIST_ALL_QUERIES"""
        # pylint: disable=no-member

        factory = _OCIENT_REQUEST_FACTORIES.get(operation.upper(), None)

        if factory is None:
            raise NotSupportedError(f"List query '{operation}' not supported by pyocient'")

        # geerate the appropriate request
        req = factory.request(operation)

        while True:
            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, factory.response())
            except IOError:
                # remake our connection
                self.connection = Connection(user=self.connection.user,
                                             password=self.connection.password,
                                             host=f"{','.join(self.connection.hosts)}:{self.connection.port}",
                                             database=self.connection.database,
                                             tls=self.connection.tls,
                                             handshake=self.connection.handshake,
                                             session=self.connection.session)

                continue
            break

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_list(operation=operation)
                return
            else:
                raise _convert_exception(rsp.response)

        self.description = []

        rows = factory.process(rsp)
        if not rows:
            self.list_result = []
            return

        # Create the column descriptions
        row = rows[0]
        for field in row._fields:
            self.description.append((field,
                                     TypeCodes.cls_to_type(row._field_types[field]),
                                     None,  # display_size
                                     None,  # internal_size
                                     None,  # precision
                                     None,  # scale
                                     None  # null_ok
                                     ))

        # and set the results
        self.list_result = rows

    def _get_result_metadata(self):
        """Internal routine to get metadata for a result set"""
        # pylint: disable=no-member
        req = proto.Request()
        req.type = req.FETCH_METADATA

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchMetadataResponse())
        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp.response)

        cols = {}
        for (key, value) in rsp.cols2pos.items():
            cols[value] = key

        self.description = []
        colnames = []
        for i in range(len(cols)):  # pylint: disable=consider-using-enumerate
            name = cols[i]
            # This tuple is defined in PEP 249
            self.description.append((name,
                                    TypeCodes.to_type(rsp.cols2Types[name]),
                                    None,  # display_size
                                    None,  # internal_size
                                    None,  # precision
                                    None,  # scale
                                    None  # null_ok
                                     ))
            colnames.append(name)
        self.resultset_tuple = namedtuple('Row', colnames, rename=True)

    def _execute_update(self, operation):
        """Execute an update statement"""
        # pylint: disable=no-member
        # While we are redirecting...

        # There is no resultset data from an update
        self.end_of_data = True

        while True:
            req = proto.Request()
            req.type = req.EXECUTE_UPDATE
            req.execute_update.sql = operation
            req.execute_update.force = False

            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, proto.ExecuteUpdateResponse())
            except IOError:
                # remake our connection
                self.connection = Connection(user=self.connection.user,
                                             password=self.connection.password,
                                             host=f"{','.join(self.connection.hosts)}:{self.connection.port}",
                                             database=self.connection.database,
                                             tls=self.connection.tls,
                                             handshake=self.connection.handshake,
                                             session=self.connection.session)

                continue

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                    # Need to refresh the session
                    self.connection.refresh()
                    # and try again
                    continue
                else:
                    raise _convert_exception(rsp.response)

            # see if we are being told to redirect
            if not rsp.redirect:
                break

            # remake our connection
            self.connection = self.connection.redirect(f"{','.join(self.connection.hosts)}:{self.connection.port}")

    def _execute_force(self, operation) -> None:
        if operation.strip().upper() == "FORCE REDIRECT":
            # Sets the next command that is execute query to redirect
            self.connection.force_next_redirect = True
            self.end_of_data = True
        else:
            # Force external command
            self._execute_force_external(operation)

    def _execute_force_external(self, operation) -> None:
        # pylint: disable=no-member
        # While we are redirecting...
        factory = _OCIENT_REQUEST_FACTORIES["FORCE"]
        req = factory.request(operation=operation)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.ConfirmationResponse())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp)

    def _execute_set(self, params) -> None:
        if len(params) != 2:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        op = params[0].upper()
        val = params[1].strip()

        if op == 'SCHEMA':
            factory = _OCIENT_REQUEST_FACTORIES["SET SCHEMA"]
            req = factory.request(val)
        else:
            try:
                val = int(val)
            except ValueError:
                raise ProgrammingError(reason="Syntax error in SET. Value must be numeric")

            factory = _OCIENT_REQUEST_FACTORIES["SET"]
            req = factory.request(op, val)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_set(params)
                return
            else:
                raise _convert_exception(rsp)

    def _execute_get_schema(self) -> None:
        factory = _OCIENT_REQUEST_FACTORIES["GET SCHEMA"]
        req = factory.request()

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_get_schema()
                return
            else:
                raise _convert_exception(rsp.response)

        self.description = [('schema',
                            TypeCodes.CHAR,
                            None,  # display_size
                            None,  # internal_size
                            None,  # precision
                            None,  # scale
                            None  # null_ok
                             )]

        self.list_result = [namedtuple('Row', ('schema'))(rsp.schema,)]

    # If we need to implement more of these sorts of custom commands, consider
    # making a factory for the description and results.
    def _execute_get_server_session_id(self) -> None:
        self.description = [('server_session_id',
                            TypeCodes.CHAR,
                            None,  # display_size
                            None,  # internal_size
                            None,  # precision
                            None,  # scale
                            None  # null_ok
                             )]
        self.list_result = [namedtuple('Row', ('server_session_id'))(self.connection.serverSessionId,)]

    def _execute_get(self, params) -> None:
        if len(params) == 1 and params[0].upper() == 'SCHEMA':
            self._execute_get_schema()
        elif len(params) == 3 and params[0].upper() == 'SERVER' and params[1].upper() == 'SESSION' and params[2].upper() == 'ID':
            self._execute_get_server_session_id()
        else:
            raise ProgrammingError(reason="Syntax error")

    def _execute_clear(self, params) -> None:
        if len(params) != 1 or params[0].upper() != 'CACHE':
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        factory = _OCIENT_REQUEST_FACTORIES["CLEAR CACHE"]
        req = factory.request()

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            if(rsp.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_clear(params)
                return
            else:
                raise _convert_exception(rsp)

    def _execute_cancelkill(self, op, id) -> None:
        if len(id) != 1:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        factory = _OCIENT_REQUEST_FACTORIES[op]
        req = factory.request(id[0])

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_cancelkill(op, id)
                return
            else:
                raise _convert_exception(rsp.response)

    # TODO: replace the other metadata call
    def _execute_systemmetadata(self, op, schema=None, table=None, column=None, view=None):
        factory = _OCIENT_REQUEST_FACTORIES['GET SYSTEM METADATA']
        req = factory.request(op, schema, table, column, view)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if(rsp.response.vendor_code == SESSION_EXPIRED_CODE):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_systemmetadata(op, schema=schema, table=table, column=column, view=view)
                return
            else:
                raise _convert_exception(rsp.response)

        if rsp.HasField("result_set_val"):
            self._get_result_metadata()

            for blob in rsp.result_set_val.blobs:
                self._buffers.append(blob)
            return None

        if rsp.HasField('string_val'):
            return rsp.string_val

        return rsp.int_val

    def _get_more_data(self):
        """Internal routine to get more data from a query"""
        # pylint: disable=no-member
        req = proto.Request()
        req.type = req.FETCH_DATA
        req.fetch_data.fetch_size = self.arraysize
        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchDataResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR:
            raise _convert_exception(rsp.response)

        for blob in rsp.result_set.blobs:
            if not self._buffers:
                self._offset = 0
            self._buffers.append(blob)

    def fetchmany(self, size=None):
        """Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when no
        more rows are available.

        The number of rows to fetch per call is specified by the parameter. If it
        is not given, the cursor's arraysize determines the number of rows to be
        fetched. The method will try to fetch as many rows as indicated by the size
        parameter. If this is not possible due to the specified number of rows not
        being available, fewer rows may be returned.
        """
        if size is None:
            size = self.arraysize

        rows = []
        while size > 0:
            a_row = self.fetchone()
            if a_row is None:
                break
            rows.append(a_row)
            size -= 1
        return rows

    def fetchall(self):
        """Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.
        """
        return self.fetchmany(size=sys.maxsize)

    def __next__(self):
        a_row = self.fetchone()
        if a_row is None:
            raise StopIteration
        return a_row

    def __iter__(self):
        return self

    def fetchval(self):
        """The fetchval() convenience method returns the first column of the
        first row if there are results, otherwise it returns None.
        """
        arow = self.fetchone()
        if arow:
            return arow[0]
        return None

    def fetchone(self):
        """Fetch the next row of a query result set, returning a single sequence,
        or None when no more data is available.
        """
        # If there was never a query executed, throw an error
        if self.description is None:
            raise ProgrammingError("No result set available")

        # pylint: disable = too-many-branches
        if self.end_of_data:
            return None

        # special case explain.
        if self.explain_result is not None:
            ret = self.explain_result
            self.end_of_data = True
            return [ret]

        if self.list_result is not None:
            if self._offset >= len(self.list_result):
                self.end_of_data = True
                return None
            a_row = self.list_result[self._offset]
            self._offset += 1
            return a_row

        if self.rowcount < 0:
            self.rowcount = 0

        while not self._buffers:
            self._get_more_data()
            while self._buffers and self._buf() == b'\0\0\0\0':
                self._buffers.pop(0)

            if not self._buffers:
                # no data yet...wait so we don't hammer the host before asking for more
                sleep(0.25)

        if self._offset == 0:
            self._get_num_rows()

        row_length = self._get_int() - 4  # row_length includes the 4 bytes we just consumed
        end_offset = self._offset + row_length

        if self._bytes_remaining() == 1 and self._buf()[self._offset] == TypeCodes.DEM:
            self.rowcount -= 1
            self._buffers.pop(0)
            return self._process_pending()

        a_row = []
        while self._offset < end_offset:
            a_row.append(self._decode_entry())

        if self._offset >= len(self._buf()):
            self._buffers.pop(0)
            self._offset = 0
        self.rownumber += 1
        return self.resultset_tuple._make(a_row)

    def _process_pending(self):
        # if we have any pending queries to execute, kick one off now
        if self._pending_ops:
            self._buffers = []
            self._offset = 0
            self._execute_internal(self._pending_ops.pop(0))
            return self.fetchone()

        self.end_of_data = True
        return None

    def _buf(self):
        return self._buffers[0]

    def _bytes_remaining(self):
        if not self._buffers:
            return 0
        return len(self._buffers[0]) - self._offset

    def _get_num_rows(self):
        if self._bytes_remaining() >= 4:
            self.rowcount += self._get_int()

    def _decode_entry(self):
        # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
        coltype = self._get_byte()

        # easy conversions we can do with structs
        type_map = {TypeCodes.INT: '!i',
                    TypeCodes.LONG: '!q',
                    TypeCodes.FLOAT: '!f',
                    TypeCodes.DOUBLE: '!d',
                    TypeCodes.BOOLEAN: '?',
                    TypeCodes.SHORT: '!h'
                    }

        # if this is the easy conversion, just do it
        if coltype in type_map:
            return self._get_type(type_map[coltype])

        if coltype == TypeCodes.STRING:
            strlen = self._get_int()
            offset = self._offset
            self._offset += strlen
            return self._buf()[offset:offset+strlen].decode('utf-8')

        if coltype == TypeCodes.TIMESTAMP:
            return datetime.datetime.utcfromtimestamp(self._get_long())

        if coltype == TypeCodes.NULL:
            return None

        if coltype == TypeCodes.BYTE:
            return int.from_bytes(self._get_type('c'), "big", signed=True)

        if coltype == TypeCodes.TIME:
            seconds = self._get_long()
            second = int(seconds % 60)
            minutes = seconds / 60
            minute = int(minutes % 60)
            hours = minutes / 60
            hour = int(hours % 24)
            return datetime.time(hour, minute, second)

        if coltype == TypeCodes.BINARY:
            strlen = self._get_int()
            offset = self._offset
            self._offset += strlen
            return self._buf()[offset:offset+strlen]

        if coltype == TypeCodes.DECIMAL:
            precision = self._get_byte()
            scale = self._get_byte()

            if precision % 2 == 0:
                strlen = int((precision / 2) + 1)
            else:
                strlen = int((precision + 1) / 2)

            data = self._buf()[self._offset:(self._offset+strlen-1)]
            digits = []
            for byte in data:
                digits.append((byte & 0xf0) >> 4)
                digits.append(byte & 0x0f)

            sign = self._buf()[self._offset+strlen-1]

            digits.append(sign >> 4)
            sign = sign & 0x0f

            if sign == 12:
                sign = 0
            elif sign == 13:
                sign = 1
            else:
                raise Error(reason=f"Unknown decimal sign value {sign}")

            self._offset += strlen
            return decimal.Decimal((sign, digits, -scale))

        if coltype == TypeCodes.ARRAY:
            nested_level = 0

            arraytype = self._get_byte()

            while arraytype == TypeCodes.ARRAY:
                arraytype = self._get_byte()
                nested_level += 1

            return self._get_array(nested_level)

        if coltype == TypeCodes.UUID:
            self._offset += 16
            return uuid.UUID(bytes=self._buf()[self._offset-16:self._offset])

        if coltype == TypeCodes.ST_POINT:
            long = self._get_type('!d')
            lat = self._get_type('!d')
            if(isinf(long) or isinf(lat)):
                return "POINT EMPTY"
            return "POINT(" + str(long) + " " + str(lat) + ")"

        if coltype == TypeCodes.DATE:
            d = datetime.datetime.utcfromtimestamp(self._get_long() / 1000.0)
            return datetime.date(d.year, d.month, d.day)

        if coltype == TypeCodes.IP:
            off = self._offset
            self._offset += 16
            return ipaddress.ip_address(self._buf()[off:off+16])

        if coltype == TypeCodes.IPV4:
            off = self._offset
            self._offset += 4
            return ipaddress.ip_address(self._buf()[off:off+4])

        if coltype == TypeCodes.TIMESTAMP_NANOS:
            timestamp = self._get_long() / 1000000000.0
            return datetime.datetime.utcfromtimestamp(timestamp)

        if coltype == TypeCodes.TIME_NANOS:
            nanos = self._get_long()
            micros = int((nanos / 1000) % 1000000)
            seconds = nanos / 1000000000
            second = int(seconds % 60)
            minutes = seconds / 60
            minute = int(minutes % 60)
            hours = minutes / 60
            hour = int(hours % 24)

            return datetime.time(hour, minute, second, micros)

        if coltype == TypeCodes.TUPLE:
            return self._get_tuple()

        if coltype == TypeCodes.ST_LINESTRING:
            points = []
            num_elements = self._get_int()
            for i in range(num_elements):
                long = self._get_type('!d')
                lat = self._get_type('!d')
                points.append((long, lat))
            return points

        if coltype == TypeCodes.ST_POLYGON:
            exterior = []
            num_elements = self._get_int()
            for i in range(num_elements):
                long = self._get_type('!d')
                lat = self._get_type('!d')
                exterior.append((long, lat))
            holes = []
            num_rings = self._get_int()
            for i in range(num_rings):
                num_elements = self._get_int()
                ring = []
                for j in range(num_elements):
                    long = self._get_type('!d')
                    lat = self._get_type('!d')
                    ring.append((long, lat))
                holes.append(ring)
            return (exterior, holes)

        self.end_of_data = True
        raise Error(reason=f"Unknown column type {coltype}")

    def _get_byte(self):
        offset = self._offset
        self._offset += 1
        return self._buf()[offset]

    def _get_int(self):
        offset = self._offset
        self._offset += 4
        return struct.unpack_from('!i', self._buf(), offset)[0]

    def _get_long(self):
        offset = self._offset
        self._offset += 8
        return struct.unpack_from('!q', self._buf(), offset)[0]

    def _get_type(self, code):
        offset = self._offset
        self._offset += struct.calcsize(code)
        return struct.unpack_from(code, self._buf(), offset)[0]

    def _get_array(self, level):
        array = []

        num_elements = self._get_int()

        all_null = self._get_byte()

        if all_null != 0:
            return []

        for _ in range(num_elements):
            if level > 0:
                array.append(self._get_array(level-1))
            else:
                array.append(self._decode_entry())

        return array

    def _close_resultset(self):
        req = proto.Request()
        req.type = proto.Request.RequestType.Value('CLOSE_RESULT_SET')

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.ConfirmationResponse())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp)

    def _get_tuple(self):
        num_elements = self._get_int()
        restuple = ()
        for _ in range(num_elements):
            restuple += (self._decode_entry(),)
        return restuple


def connect(dsn=None, user=None, password=None, host=None, database=None, tls=None, force=None, handshake="gcm", configfile=None):
    # pylint: disable=too-many-arguments
    """Create a new database connection.

    The connection parameters can be specified as part of the dsn,
    using keyword arguments or both.  If both are specified, the keyword
    parameter overrides the value in the dsn.

    The Ocient DSN is of the format:
    `ocient://user:password@[host][:port][/database][?param1=value1&...]`

    `user` and `password` must be supplied.  `host` defaults to localhost,
    port defaults to 4050, database defaults to `system` and `tls` defaults
    to `unverified`.

    configfile specifies the name of a configuration file in INI format. See
    the Connection class for more detailed documentation.

    Currently supported parameters are:

    - tls: Which can have the values "off", "unverified", or "on" in the dsn,
         or Connection.TLS_NONE, Connection.TLS_UNVERIFIED, or
         Connection.TLS_ON as a keyword parameter.
    - handshake: "CBC", "GCM", or "SSO". "GCM" (Galois Counter Mode) should be used over "CBC" (Cipher Block Chaining) for password encryption. "SSO" for single sign on.
    - force: force the connection to remain on this host
    """
    if isinstance(handshake, str):
        if handshake.lower() == "gcm":
            handshake = Connection.HANDSHAKE_GCM
        elif handshake.lower() == "cbc":
            handshake = Connection.HANDSHAKE_CBC
        elif handshake.lower() == "sso":
            handshake = Connection.HANDSHAKE_SSO
        else:
            raise RuntimeError(f"Unknown Handshake method {handshake}")

    if isinstance(tls, str):
        if tls.lower() == "on":
            tls = Connection.TLS_ON
        elif tls.lower() == "unverified":
            tls = Connection.TLS_UNVERIFIED
        elif tls.lower() == "off":
            tls = Connection.TLS_NONE
        else:
            raise RuntimeError(f"Unknown TLS mode {tls}")

    params = {
        'user': user,
        'password': '*****',
        'host': host,
        'database': database,
        'tls': tls,
        'handshake': handshake,
    }

    logger.debug(f"Connect {params}")

    return Connection(dsn, user, password, host, database, tls, handshake, force, configfile)


def _custom_type_to_json(obj):
    """Helper function to convert types returned from queries to
    JSON values.  Typically invoked passed as the `default` parameter
    to json.dumps as in:

    `json.dumps(some_rows, default=_custom_type_to_json)`
    """
    if isinstance(obj, decimal.Decimal):
        return str(obj)

    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
        return obj.isoformat()

    if isinstance(obj, bytes):
        return list(obj)

    if isinstance(obj, uuid.UUID):
        return str(obj)

    if isinstance(obj, ipaddress.IPv4Address) or isinstance(obj, ipaddress.IPv6Address):
        return str(obj)

    print(f"type_to_string got called for type{type(obj)}")
    return f"placeholder for {type(obj)}"


def argparser():
    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter

    configfile = pathlib.Path.home() / '.pyocient'

    parser = ArgumentParser(description=f"""Ocient Python client {version}.
In the simplest case, run with a Data Source Name (dsn) and a
query.  For example:
  pyocient ocient://user:password@myhost:4050/mydb "select * from mytable"

Multiple query strings may be provided

DSN's are of the form:
  ocient://user:password@[host][:port][/database][?param1=value1&...]

Supported parameter are:
- tls: Which can have the values "off", "unverified", or "on"
- force: Which can have the values "true"
- handshake: Which can have the value "cbc"
""",
                            formatter_class=RawDescriptionHelpFormatter)

    # Flags that apply to both execution modes
    outgroup = parser.add_mutually_exclusive_group()
    outgroup.add_argument('-o', '--outfile', type=FileType('w'), default='-',
                          help="Output file")
    outgroup.add_argument("-n", "--noout", action='store_const', const=None, dest='outfile',
                          help="Do not output results")
    configgroup = parser.add_mutually_exclusive_group()
    configgroup.add_argument('-c', '--configfile', type=str, default=str(configfile),
                             help="Configuration file")
    configgroup.add_argument("--noconfig", action='store_const', const=None, dest='configfile',
                             help="No configuration file")
    parser.add_argument("-i", "--infile", type=FileType('r'), default=None,
                        help="Input file containing SQL statements")
    parser.add_argument("-l", "--loglevel", type=str, default='CRITICAL',
                        help="Logging level")
    parser.add_argument("--logfile", type=FileType('a'), default=sys.stdout,
                        help="Log file")
    parser.add_argument("-t", "--time", action="store_true",
                        help="Output query time")
    parser.add_argument("dsn",
                        help="DSN of the form ocient://user:password@[host][:port][/database][?param1=value1&...]")
    parser.add_argument("sql", nargs='?',
                        help="SQL statement")
    parser.add_argument("--tables", action="store_true",
                        help="List tables")
    parser.add_argument("--systables", action="store_true",
                        help="List system tables")
    parser.add_argument("--views", action="store_true",
                        help="List views")
    parser.add_argument("--format", "-f", type=str, choices=['json', 'table'], default='json',
                        help="Output format")
    parser.add_argument("--nocolor", action="store_true",
                        help="When using pyocient interactively, do not color")

    return parser


def main():
    import json
    from tabulate import tabulate
    from pygments.lexers.sql import SqlLexer
    from pygments.token import Token

    args = argparser().parse_args(sys.argv[1:])

    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)

    logging.basicConfig(level=log_level,
                        stream=args.logfile,
                        format='[%(asctime)s][%(levelname)s] %(message)s')

    sql_stmt = ''
    lexer = SqlLexer()

    def _do_query(args, connection, query):
        if args.time:
            starttime = time_ns()

        cursor = connection.cursor()

        try:
            cursor.execute(query)
        except SQLException as e:
            print(e)
            return cursor.connection

        if cursor.description and not cursor.explain_result:
            result = cursor.fetchall()
        else:
            result = cursor.connection

        if args.time:
            endtime = time_ns()

        if cursor.description is None:
            print("OK")

        elif args.outfile is not None:

            if cursor.explain_result:
                result = [{'explain': json.loads(cursor.explain_result)}]

                print(json.dumps(result, indent=4, default=_custom_type_to_json),
                      file=args.outfile)
            elif result:
                if args.format == 'json':
                    result = [row._asdict() for row in result]

                    print(json.dumps(result, indent=4, default=_custom_type_to_json),
                          file=args.outfile)
                elif args.format == "table":
                    print(tabulate(result,
                                   headers=[c[0] for c in cursor.description],
                                   tablefmt="psql"))

        if args.time:
            endtime = time_ns()
            print(f"Execution time: {(endtime - starttime)/1000000000:.3f} seconds")
        # If we don't return this connection, then we end up using the old connection which we could have been redirected
        return cursor.connection

    def _do_line(args, connection, text, sql_stmt):
        new_connection = connection
        for (token_type, token_val) in lexer.get_tokens(text):
            if token_type == Token.Punctuation and token_val == ';':
                new_connection = _do_query(args, connection, sql_stmt)
                sql_stmt = ''
            else:
                sql_stmt += token_val

        return (sql_stmt, new_connection)

    def _do_repl(args, connection):
        from prompt_toolkit import PromptSession
        from prompt_toolkit.lexers import PygmentsLexer
        from prompt_toolkit.history import FileHistory
        from pathlib import Path

        sql_stmt = ''

        session = PromptSession(lexer=PygmentsLexer(SqlLexer),
                                history=FileHistory(str(Path.home() / ".pyocient_history")))

        cursor = connection.cursor()

        print(f"Ocient Database™")
        print(f"System Version: {cursor.getSystemVersion()}, Client Version {version}")
        eof = False
        text = ''
        while not eof:
            try:
                text = session.prompt('> ')
            except KeyboardInterrupt:
                sql_stmt = ''
                continue
            except EOFError:
                break
            (sql_stmt, connection) = _do_line(args, connection, text, sql_stmt)

        if len(sql_stmt.strip()):
            connection = _do_query(args, connection, sql_stmt)

        print('GoodBye!')

    try:
        connection = connect(args.dsn, configfile=args.configfile)

        if args.sql:
            connection = _do_query(args, connection, args.sql)
        elif args.infile:
            (sql_stmt, connection) = _do_line(args, connection, args.infile.read(), sql_stmt)
            if len(sql_stmt.strip()):
                connection = _do_query(args, connection, sql_stmt)
        elif sys.stdin.isatty():
            _do_repl(args, connection)
        else:
            (sql_stmt, connection) = _do_line(args, connection, sys.stdin.read(), sql_stmt)

    except SQLException as exc:
        print(f"Error: {exc.reason}", file=sys.stderr)


if __name__ == "__main__":
    main()
